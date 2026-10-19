#Regresiones de integración, formularios y errores recuperables.

from dataclasses import replace
from datetime import time, timedelta
from secrets import token_urlsafe

import pytest

from reservas.modelo.entidades import HorarioAtencion
from reservas.modelo.errores import AccesoDenegado, Conflicto, ServicioOcupado, Validacion
from reservas.infraestructura.dao_sqlite import iso
from reservas.infraestructura.inicializacion import cargar_demo, inicializar
from tests.conftest import CLAVE, campo_oculto, entrar, formulario_reserva


def test_recorrido_http_cliente_crear_repetir_cancelar(client, datos, uow):
    entrar(client)
    assert b"La Mesa" in client.get("/restaurantes?nombre=mesa&ciudad=Bogot").data
    d = datos(observaciones="Mesa tranquila, por favor.")
    valores = formulario_reserva(client, d)
    respuesta = client.post("/reservas", data=valores)
    assert respuesta.status_code == 302
    assert client.post("/reservas", data=valores).location == respuesta.location
    detalle = client.get(respuesta.location)
    assert detalle.status_code == 200 and b"Mesa tranquila" in detalle.data
    copia = client.get(respuesta.location + "/repetir")
    assert b"Mesa tranquila" in copia.data
    assert campo_oculto(copia, "token_operacion") != valores["token_operacion"]
    cancelada = client.post(
        respuesta.location + "/cancelar",
        data={"csrf_token": campo_oculto(detalle, "csrf_token")},
        follow_redirects=True,
    )
    assert cancelada.status_code == 200 and b"Cancelada" in cancelada.data
    with uow() as u:
        assert len(u.reservas.listar()) == 1
    assert (
        client.post(
            "/logout", data={"csrf_token": campo_oculto(cancelada, "csrf_token")}
        ).status_code
        == 302
    )
    assert client.get("/reservas").status_code == 302


def test_admin_http_crea_para_cliente_y_modifica_catalogos(client, datos, uow):
    entrar(client, "admin@demo.local")
    valores = formulario_reserva(client, datos(), cliente_id=2)
    respuesta = client.post("/reservas", data=valores, follow_redirects=True)
    assert respuesta.status_code == 200 and b"Diego Ruiz" in respuesta.data
    pagina = client.get("/admin/mesas")
    csrf = campo_oculto(pagina, "csrf_token")
    r = client.post(
        "/admin/mesas",
        data={
            "restaurante_id": 1,
            "numero": "Terraza",
            "capacidad": 5,
            "activa": "y",
            "csrf_token": csrf,
        },
    )
    assert r.status_code == 302
    with uow() as u:
        mesa = next(m for m in u.mesas.listar(1) if m.numero == "Terraza")
    pagina = client.get(f"/admin/mesas?editar={mesa.id}")
    assert b"Terraza" in pagina.data
    r = client.post(
        "/admin/mesas",
        data={
            "id": mesa.id,
            "restaurante_id": 1,
            "numero": "Terraza 2",
            "capacidad": 6,
            "csrf_token": csrf,
        },
    )
    assert r.status_code == 302
    with uow() as u:
        guardada = u.mesas.buscar_por_id(mesa.id)
        assert guardada.numero == "Terraza 2" and not guardada.activa
    r = client.post(
        "/admin/horarios",
        data={
            "restaurante_id": 1,
            "dia_semana": 1,
            "apertura": "08:00",
            "cierre": "10:00",
            "csrf_token": csrf,
        },
    )
    assert r.status_code == 302
    with uow() as u:
        h = next(h for h in u.horarios.listar(1) if h.apertura == time(8))
    assert client.get(f"/admin/horarios?editar={h.id}").status_code == 200
    r = client.post(
        "/admin/horarios",
        data={"restaurante_id": 1, "accion": "eliminar", "eliminar_id": h.id, "csrf_token": csrf},
    )
    assert r.status_code == 302
    with uow() as u:
        assert u.horarios.buscar_por_id(h.id) is None


@pytest.mark.parametrize(
    "campo,valor",
    [
        ("personas", "texto"),
        ("personas", "0"),
        ("hora", "29:00"),
        ("fecha", "fecha-mala"),
        ("observaciones", "x" * 501),
    ],
)
def test_formulario_rechaza_datos_invalidos_y_conserva_token(client, datos, uow, campo, valor):
    entrar(client)
    valores = formulario_reserva(client, datos())
    valores[campo] = valor
    respuesta = client.post("/reservas", data=valores)
    assert respuesta.status_code == 422
    assert campo_oculto(respuesta, "token_operacion") == valores["token_operacion"]
    with uow() as u:
        assert not u.reservas.listar()


def test_identidad_cliente_se_toma_de_sesion(client, datos, uow):
    entrar(client)
    valores = formulario_reserva(client, datos())
    valores["cliente_id"] = "2"
    #El campo de otro rol no concede identidad ni capacidad de actuar por terceros.
    respuesta = client.post("/reservas", data=valores)
    assert respuesta.status_code in (302, 422)
    with uow() as u:
        assert all(r.cliente_id == 1 for r in u.reservas.listar())


@pytest.mark.parametrize(
    "destino",
    [
        "https://evil.example",
        "//evil.example",
        "/\\evil.example",
        "http://[invalido",
        "/ok\r\nLocation: https://evil.example",
    ],
)
def test_redireccion_externa_rechazada(client, destino):
    from urllib.parse import urlencode

    respuesta = entrar(client, next_url="?" + urlencode({"next": destino}))
    assert respuesta.location == "/restaurantes"


def test_sesion_inactiva_no_puede_operar(client, uow):
    entrar(client)
    with uow() as u:
        u.iniciar_escritura()
        u.conexion.execute("UPDATE usuario SET activo=0 WHERE id=1")
        u.confirmar()
    assert client.get("/reservas").status_code == 302


def test_configuracion_horarios_superpuestos_y_medianoche(app, uow):
    conf = app.extensions["configuracion"]
    with pytest.raises(Validacion):
        conf.guardar_horario(3, HorarioAtencion(None, 1, 1, time(12), time(16)))
    with pytest.raises(Validacion):
        HorarioAtencion(None, 1, 1, time(22), time(2))
    with pytest.raises(AccesoDenegado):
        conf.guardar_horario(1, HorarioAtencion(None, 1, 1, time(8), time(10)))
    conf.guardar_horario(3, HorarioAtencion(None, 1, 1, time(8), time(10)))
    with uow() as u:
        assert len(u.horarios.listar_por_dia(1, 1)) == 3


def test_horario_de_30_minutos_y_restaurante_inactivo(facade, datos, token, uow):
    d = datos()
    d.inicio += timedelta(minutes=5)
    with pytest.raises(Validacion):
        facade.crear_reserva(1, d, token)
    with uow() as u:
        u.iniciar_escritura()
        u.conexion.execute("UPDATE restaurante SET activo=0 WHERE id=1")
        u.confirmar()
    with pytest.raises(AccesoDenegado):
        facade.crear_reserva(1, datos(), token)


def test_disparadores_insert_update_y_claves_foraneas(facade, datos, token, uow):
    r = facade.crear_reserva(1, datos(personas=12), token)
    with pytest.raises(Conflicto):
        with uow() as u:
            u.iniciar_escritura()
            u.conexion.execute(
                "INSERT INTO reserva(cliente_id,creado_por_id,mesa_id,inicio,fin,personas,estado,fecha_creacion,token_operacion) VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    2,
                    2,
                    r.mesa_id,
                    iso(r.inicio),
                    iso(r.fin),
                    12,
                    "CONFIRMADA",
                    iso(r.fecha_creacion),
                    token_urlsafe(32),
                ),
            )
    segunda = facade.crear_reserva(2, datos(personas=12, inicio=r.fin), token_urlsafe(32))
    with pytest.raises(Conflicto):
        with uow() as u:
            u.iniciar_escritura()
            u.conexion.execute(
                "UPDATE reserva SET inicio=?,fin=? WHERE id=?",
                (iso(r.inicio), iso(r.fin), segunda.id),
            )
    with pytest.raises(Conflicto):
        with uow() as u:
            u.iniciar_escritura()
            u.conexion.execute("DELETE FROM mesa WHERE id=?", (r.mesa_id,))


def test_busy_timeout_reintento_mismo_token(app, facade, datos, token, uow):
    app.config["SQLITE_TIMEOUT"] = 0.03
    with uow() as bloqueador:
        bloqueador.iniciar_escritura()
        with pytest.raises(ServicioOcupado):
            facade.crear_reserva(1, datos(), token)
    r = facade.crear_reserva(1, datos(), token)
    assert r.id


def test_cambio_mesa_permitido_despues_de_finalizar(app, facade, datos, token, uow):
    r = facade.crear_reserva(1, datos(), token)
    app.config["RELOJ"].ahora = r.fin
    with uow() as u:
        mesa = u.mesas.buscar_por_id(r.mesa_id)
    app.extensions["configuracion"].guardar_mesa(3, replace(mesa, activa=False))
    assert facade.obtener_detalle(1, r.id)["reserva"].estado == "CONFIRMADA"


def test_init_y_seed_no_borran_datos(app, facade, datos, token, uow):
    r = facade.crear_reserva(1, datos(), token)
    inicializar(app.config["DATABASE"])
    with pytest.raises(Conflicto):
        cargar_demo(app.config["DATABASE"], CLAVE)
    with uow() as u:
        assert u.reservas.buscar_por_id(r.id)


def test_health_headers_y_busqueda_parametrizada(client):
    assert client.get("/health").json == {"estado": "ok"}
    entrar(client)
    respuesta = client.get("/restaurantes", query_string={"nombre": "' OR 1=1 --"})
    assert respuesta.status_code == 200 and b"No encontramos restaurantes" in respuesta.data
    assert respuesta.headers["X-Content-Type-Options"] == "nosniff"
    assert respuesta.headers["Cache-Control"] == "no-store"


def test_paginacion_temporal_es_presentacion_no_estado(app, client, facade, datos, token):
    r = facade.crear_reserva(1, datos(), token)
    app.config["RELOJ"].ahora = r.fin + timedelta(minutes=1)
    entrar(client)
    respuesta = client.get("/reservas")
    assert b"Finalizada" in respuesta.data
    assert facade.obtener_detalle(1, r.id)["reserva"].estado == "CONFIRMADA"


def test_repeticion_historica_conserva_datos_al_consultar_nueva_fecha(
    app, client, facade, datos, token
):
    reserva = facade.crear_reserva(
        3, datos(observaciones="Conservar estas observaciones"), token, cliente_id=2
    )
    app.config["RELOJ"].ahora = reserva.fin + timedelta(days=1)
    entrar(client, "admin@demo.local")
    pagina = client.get(f"/reservas/{reserva.id}/repetir")
    assert campo_oculto(pagina, "repetir_id") == str(reserva.id)
    nueva_fecha = (app.config["RELOJ"]() + timedelta(days=1)).date().isoformat()
    recarga = client.get(
        "/reservas/nueva",
        query_string={
            "repetir_id": reserva.id,
            "fecha": nueva_fecha,
            "restaurante_id": 1,
            "personas": 3,
        },
    )
    assert recarga.status_code == 200
    assert b"Conservar estas observaciones" in recarga.data
    assert f'value="{nueva_fecha}"'.encode() in recarga.data
    assert b'selected value="2"' in recarga.data
