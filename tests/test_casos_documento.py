#Casos P01-P30 del Google Docs. Cada prueba usa una base temporal aislada.
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import timedelta
from secrets import token_urlsafe
from threading import Barrier, Lock
from unittest.mock import patch

import pytest

from reservas import create_app
from reservas.aplicacion.reservas import ServicioReserva
from reservas.modelo.entidades import EstadoReserva, Rol, Usuario
from reservas.modelo.errores import AccesoDenegado, Conflicto, SinDisponibilidad, Validacion
from reservas.infraestructura.dao_sqlite import SqliteReservaDAO
from reservas.infraestructura.unidad_trabajo import UnidadTrabajoSqlite
from reservas.patrones.adapter import UsuarioSesionAdapter
from reservas.patrones.builder import ContextoReserva, DirectorReserva, ReservaBuilder
from tests.conftest import CLAVE, campo_oculto, entrar


@pytest.mark.parametrize(
    "correo,ruta", [("cliente@demo.local", "/restaurantes"), ("admin@demo.local", "/reservas")]
)
def test_P01_login_valido(client, correo, ruta):
    respuesta = entrar(client, correo)
    assert respuesta.status_code == 302 and respuesta.location.endswith(ruta)
    assert client.get(ruta).status_code == 200


def test_P02_clave_incorrecta_y_cuenta_inactiva(client, uow):
    respuesta = entrar(client, clave="incorrecta")
    assert respuesta.status_code == 401
    with uow() as u:
        u.iniciar_escritura()
        u.conexion.execute("UPDATE usuario SET activo=0 WHERE id=1")
        u.confirmar()
    assert entrar(client).status_code == 401
    with client.session_transaction() as s:
        assert "_user_id" not in s


def test_P03_cliente_no_admin(client):
    entrar(client)
    assert client.get("/admin/mesas").status_code == 403
    assert client.get("/admin/horarios").status_code == 403


def test_P04_admin_no_accede_a_otro_restaurante(app, client, facade, datos, token, uow):
    entrar(client, "admin@demo.local")
    assert client.get("/admin/mesas?restaurante_id=2").status_code == 403
    with pytest.raises(AccesoDenegado):
        facade.crear_reserva(3, datos(restaurante_id=2), token, cliente_id=1)
    with uow() as u:
        mesa = u.mesas.listar(2)[0]
    with pytest.raises(AccesoDenegado):
        app.extensions["configuracion"].guardar_mesa(3, replace(mesa, capacidad=100))
    with uow() as u:
        assert not u.reservas.listar()
        assert u.mesas.buscar_por_id(mesa.id).capacidad == mesa.capacidad


def test_P05_cliente_no_ve_reserva_ajena(client, facade, datos, token):
    reserva = facade.crear_reserva(2, datos(observaciones="Detalle privado de otro cliente"), token)
    entrar(client)
    respuesta = client.get(f"/reservas/{reserva.id}")
    assert respuesta.status_code == 403
    assert b"Detalle privado" not in respuesta.data
    assert facade.listar_reservas(1) == []


def test_P06_reserva_valida_mesa_minima(facade, datos, token, uow):
    reserva = facade.crear_reserva(1, datos(personas=3), token)
    assert reserva.id and reserva.estado == EstadoReserva.CONFIRMADA
    with uow() as u:
        mesa = u.mesas.buscar_por_id(reserva.mesa_id)
        assert mesa.capacidad == 4 and mesa.id == 3
        assert len(u.reservas.listar()) == 1
        assert u.conexion.execute("PRAGMA foreign_keys").fetchone()[0] == 1


@pytest.mark.parametrize("personas", [0, -1, "dos", True])
def test_P07_personas_invalidas(facade, datos, token, personas, uow):
    with pytest.raises(Validacion):
        facade.crear_reserva(1, datos(personas=personas), token)
    with uow() as u:
        assert not u.reservas.listar()


@pytest.mark.parametrize("diferencia", [0, -1])
def test_P08_inicio_no_futuro(app, facade, datos, token, diferencia):
    with pytest.raises(Validacion):
        facade.crear_reserva(
            1, datos(inicio=app.config["RELOJ"]() + timedelta(seconds=diferencia)), token
        )


@pytest.mark.parametrize("hora_utc", [19, 20, 3])
def test_P09_cierre_y_descanso(facade, datos, token, hora_utc):
    d = datos()
    d.inicio = d.inicio.replace(hour=hora_utc, minute=30)
    with pytest.raises(Validacion):
        facade.crear_reserva(1, d, token)


def test_P10_capacidad_insuficiente(facade, datos, token):
    with pytest.raises(SinDisponibilidad):
        facade.crear_reserva(1, datos(personas=13), token)


def test_P11_solapamiento_impedido(facade, datos, token, uow):
    reserva = facade.crear_reserva(1, datos(personas=12), token)
    with pytest.raises(SinDisponibilidad):
        facade.crear_reserva(
            2, datos(personas=12, inicio=reserva.inicio + timedelta(minutes=30)), token_urlsafe(32)
        )
    with uow() as u:
        assert len(u.reservas.listar()) == 1


def test_P12_extremos_contiguos(facade, datos, token):
    primera = facade.crear_reserva(1, datos(personas=12), token)
    segunda = facade.crear_reserva(2, datos(personas=12, inicio=primera.fin), token_urlsafe(32))
    assert primera.mesa_id == segunda.mesa_id and primera.fin == segunda.inicio


def test_P13_cancelacion_libera_y_conserva_historial(facade, datos, token, uow):
    primera = facade.crear_reserva(1, datos(personas=12), token)
    assert facade.cancelar_reserva(1, primera.id).estado == EstadoReserva.CANCELADA
    assert facade.cancelar_reserva(1, primera.id).estado == EstadoReserva.CANCELADA
    segunda = facade.crear_reserva(2, datos(personas=12), token_urlsafe(32))
    assert primera.mesa_id == segunda.mesa_id
    with uow() as u:
        assert len(u.reservas.listar()) == 2


def test_P14_no_cancelar_iniciada(app, facade, datos, token, uow):
    reserva = facade.crear_reserva(1, datos(), token)
    app.config["RELOJ"].ahora = reserva.inicio
    with pytest.raises(Conflicto):
        facade.cancelar_reserva(1, reserva.id)
    with uow() as u:
        assert u.reservas.buscar_por_id(reserva.id).estado == EstadoReserva.CONFIRMADA


@pytest.mark.parametrize("cambio", [{"activa": False}, {"capacidad": 1}])
def test_P15_proteger_mesa_con_reserva(app, facade, datos, token, uow, cambio):
    reserva = facade.crear_reserva(1, datos(), token)
    with uow() as u:
        mesa = u.mesas.buscar_por_id(reserva.mesa_id)
    with pytest.raises(Conflicto):
        app.extensions["configuracion"].guardar_mesa(3, replace(mesa, **cambio))
    with uow() as u:
        assert u.mesas.buscar_por_id(mesa.id) == mesa


def test_P16_proteger_horario(app, facade, datos, token, uow):
    from datetime import time

    reserva = facade.crear_reserva(1, datos(), token)
    with uow() as u:
        franja = u.horarios.listar_por_dia(1, reserva.inicio.isoweekday())[0]
    conf = app.extensions["configuracion"]
    with pytest.raises(Conflicto):
        conf.eliminar_horario(3, 1, franja.id)
    with pytest.raises(Conflicto):
        conf.guardar_horario(3, replace(franja, cierre=time(12, 30)))
    with uow() as u:
        assert u.horarios.buscar_por_id(franja.id) == franja


def test_P17_concurrencia_dos_conexiones_ultima_mesa(app, facade, datos, uow):
    barrera = Barrier(2)
    conexiones = []
    candado = Lock()

    class UowSincronizada(UnidadTrabajoSqlite):
        def iniciar_escritura(self):
            with candado:
                conexiones.append(self.conexion)
            barrera.wait(timeout=10)
            super().iniciar_escritura()

    def crear_uow():
        return UowSincronizada(app.config["DATABASE"])

    servicio = ServicioReserva(crear_uow, facade.acceso, facade.disponibilidad, app.config["RELOJ"])

    def competir(actor):
        try:
            return servicio.crear(actor, datos(personas=12), token_urlsafe(32)).id
        except SinDisponibilidad:
            return None

    with ThreadPoolExecutor(max_workers=2) as ejecutor:
        resultados = list(ejecutor.map(competir, [1, 2]))
    assert len(conexiones) == 2 and conexiones[0] is not conexiones[1]
    assert sum(r is not None for r in resultados) == 1
    with uow() as u:
        assert len(u.reservas.listar()) == 1


def test_P18_idempotencia(facade, datos, token, uow):
    d = datos()
    primera = facade.crear_reserva(1, d, token)
    segunda = facade.crear_reserva(1, d.clonar(), token)
    assert segunda.id == primera.id
    with uow() as u:
        assert len(u.reservas.listar()) == 1


def test_P19_token_actor_o_contenido_distinto(facade, datos, token, uow):
    d = datos()
    facade.crear_reserva(1, d, token)
    with pytest.raises(Conflicto):
        facade.crear_reserva(2, d, token)
    with pytest.raises(Conflicto):
        facade.crear_reserva(1, datos(personas=3), token)
    with uow() as u:
        assert len(u.reservas.listar()) == 1


def test_P20_rollback_escritura_parcial(facade, datos, token, uow):
    original = SqliteReservaDAO.guardar

    def fallar(self, reserva):
        original(self, reserva)
        raise RuntimeError("fallo simulado después de INSERT")

    with patch.object(SqliteReservaDAO, "guardar", fallar):
        with pytest.raises(RuntimeError):
            facade.crear_reserva(1, datos(), token)
    with uow() as u:
        assert not u.reservas.listar()
    assert facade.crear_reserva(1, datos(), token).id


def test_P21_persistencia_tras_reiniciar(app, facade, datos, token):
    r = facade.crear_reserva(1, datos(), token)
    nueva = create_app(
        {"TESTING": True, "SECRET_KEY": "x" * 64, "DATABASE": app.config["DATABASE"]}
    )
    assert nueva.extensions["reservas"].obtener_detalle(1, r.id)["reserva"].id == r.id


def test_P22_csrf_obligatorio(client):
    assert (
        client.post("/login", data={"correo": "cliente@demo.local", "clave": CLAVE}).status_code
        == 400
    )
    entrar(client)
    assert client.post("/logout").status_code == 400
    assert client.post("/reservas", data={"csrf_token": "falso"}).status_code == 400


def test_P23_html_escapado(client, facade, datos, token):
    r = facade.crear_reserva(1, datos(observaciones='<script>alert("x")</script>'), token)
    entrar(client)
    pagina = client.get(f"/reservas/{r.id}")
    assert b"<script>alert" not in pagina.data
    assert b"&lt;script&gt;" in pagina.data


def test_P24_unicidad_mesa_correo(uow):
    with pytest.raises(Conflicto):
        with uow() as u:
            u.iniciar_escritura()
            u.conexion.execute(
                "INSERT INTO mesa(restaurante_id,numero,capacidad) VALUES(1,?,2)", ("1",)
            )
    with pytest.raises(Conflicto):
        with uow() as u:
            u.iniciar_escritura()
            u.conexion.execute(
                "INSERT INTO usuario(nombre,correo,hash_clave,rol) VALUES('X',?,'hash','CLIENTE')",
                ("cliente@demo.local",),
            )


def test_P25_builder_incompleto_intervalo_invalido(datos, uow, app, token):
    b = ReservaBuilder()
    with pytest.raises(Validacion):
        b.construir()
    with uow() as u:
        mesa = u.mesas.buscar_por_id(1)
    d = datos()
    contexto = ContextoReserva(1, 1, mesa, d, d.inicio, app.config["RELOJ"](), token)
    with pytest.raises(Validacion):
        DirectorReserva(b).preparar(contexto)


def test_P26_builder_sin_residuos(datos, uow, app, token):
    with uow() as u:
        mesa = u.mesas.buscar_por_id(1)
    d = datos(observaciones="primera")
    contexto = ContextoReserva(
        1, 1, mesa, d, d.inicio + timedelta(minutes=90), app.config["RELOJ"](), token
    )
    b = ReservaBuilder()
    director = DirectorReserva(b)
    r1 = director.preparar(contexto)
    with pytest.raises(Validacion):
        b.construir()
    r2 = director.preparar(
        replace(contexto, datos=datos(observaciones="segunda"), token=token_urlsafe(32))
    )
    assert r1 is not r2 and r1.id is None and r2.id is None
    assert r1.datos.observaciones == "primera" and r2.datos.observaciones == "segunda"


def test_P27_prototype_independiente(facade, datos, token):
    d = datos()
    copia = d.clonar()
    assert copia == d and copia is not d
    copia.personas = 99
    assert d.personas == 2
    r = facade.crear_reserva(1, d, token)
    d.observaciones = "modificado externamente"
    assert r.datos.observaciones == ""
    clon = facade.preparar_repeticion(1, r.id)
    clon.observaciones = "nueva"
    assert facade.obtener_detalle(1, r.id)["reserva"].datos.observaciones == ""


def test_P28_repetir_sin_cupo_revalida(client, facade, datos, token, uow):
    reserva = facade.crear_reserva(1, datos(personas=12), token)
    entrar(client)
    pagina = client.get(f"/reservas/{reserva.id}/repetir")
    assert pagina.status_code == 200 and b"Copiamos los datos" in pagina.data
    assert campo_oculto(pagina, "token_operacion") != token
    with pytest.raises(SinDisponibilidad):
        facade.crear_reserva(1, facade.preparar_repeticion(1, reserva.id), token_urlsafe(32))
    with uow() as u:
        assert len(u.reservas.listar()) == 1


def test_P29_fachada_ambos_roles(facade, datos):
    with patch.object(
        facade.servicio_reserva, "crear", wraps=facade.servicio_reserva.crear
    ) as espia:
        cliente = facade.crear_reserva(1, datos(), token_urlsafe(32))
        admin = facade.crear_reserva(3, datos(), token_urlsafe(32), cliente_id=2)
        assert espia.call_count == 2
        assert cliente.cliente_id == cliente.creado_por_id == 1
        assert admin.cliente_id == 2 and admin.creado_por_id == 3


def test_P30_adapter_id_y_actividad():
    usuario = Usuario(99, "Prueba", "x@demo.local", "hash", Rol.CLIENTE, False)
    adapter = UsuarioSesionAdapter(usuario)
    assert adapter.get_id() == "99" and not adapter.is_active
    assert adapter.is_authenticated and not adapter.is_anonymous
    assert not hasattr(usuario, "get_id")
