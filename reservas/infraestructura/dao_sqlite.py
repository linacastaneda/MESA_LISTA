#Mapeo fila/entidad. Todos los DAO reciben la conexión de su unidad de trabajo.

from dataclasses import replace
from datetime import UTC, datetime, time

from reservas.aplicacion.contratos import (
    AsignacionAdminDAO,
    HorarioDAO,
    MesaDAO,
    ReservaDAO,
    RestauranteDAO,
    UsuarioDAO,
)
from reservas.dominio.entidades import (
    DatosReserva,
    HorarioAtencion,
    Mesa,
    Reserva,
    Restaurante,
    Rol,
    Usuario,
)


def iso(valor):
    return valor.astimezone(UTC).isoformat(timespec="microseconds")


def usuario_de_fila(fila):
    if fila is None:
        return None
    return Usuario(
        fila["id"],
        fila["nombre"],
        fila["correo"],
        fila["hash_clave"],
        Rol(fila["rol"]),
        bool(fila["activo"]),
    )


def mesa_de_fila(f):
    return Mesa(f["id"], f["restaurante_id"], f["numero"], f["capacidad"], bool(f["activa"]))


def horario_de_fila(f):
    return HorarioAtencion(
        f["id"],
        f["restaurante_id"],
        f["dia_semana"],
        time.fromisoformat(f["apertura"]),
        time.fromisoformat(f["cierre"]),
    )


def reserva_de_fila(f):
    if f is None:
        return None
    datos = DatosReserva(
        f["restaurante_id"], datetime.fromisoformat(f["inicio"]), f["personas"], f["observaciones"]
    )
    return Reserva(
        f["id"],
        f["cliente_id"],
        f["creado_por_id"],
        f["mesa_id"],
        datos,
        datetime.fromisoformat(f["fin"]),
        datetime.fromisoformat(f["fecha_creacion"]),
        f["token_operacion"],
        f["estado"],
    )


class SqliteUsuarioDAO(UsuarioDAO):
    def __init__(self, conexion):
        self.conexion = conexion

    def buscar_por_id(self, id):
        return usuario_de_fila(
            self.conexion.execute("SELECT * FROM usuario WHERE id=?", (id,)).fetchone()
        )

    def buscar_por_correo(self, correo):
        return usuario_de_fila(
            self.conexion.execute(
                "SELECT * FROM usuario WHERE correo=?", (correo.strip().lower(),)
            ).fetchone()
        )

    def listar_clientes(self):
        return [
            usuario_de_fila(f)
            for f in self.conexion.execute(
                "SELECT * FROM usuario WHERE rol='CLIENTE' AND activo=1 ORDER BY nombre"
            )
        ]


class SqliteRestauranteDAO(RestauranteDAO):
    def __init__(self, conexion):
        self.conexion = conexion

    def buscar_por_id(self, id):
        f = self.conexion.execute("SELECT * FROM restaurante WHERE id=?", (id,)).fetchone()
        return (
            Restaurante(f["id"], f["nombre"], f["ciudad"], f["direccion"], bool(f["activo"]))
            if f
            else None
        )

    def buscar(self, nombre="", ciudad=""):
        filas = self.conexion.execute("SELECT * FROM restaurante WHERE activo=1 ORDER BY nombre")
        return [
            Restaurante(f["id"], f["nombre"], f["ciudad"], f["direccion"], True)
            for f in filas
            if nombre.casefold() in f["nombre"].casefold()
            and ciudad.casefold() in f["ciudad"].casefold()
        ]


class SqliteAsignacionAdminDAO(AsignacionAdminDAO):
    def __init__(self, conexion):
        self.conexion = conexion

    def puede_gestionar(self, usuario_id, restaurante_id):
        return (
            self.conexion.execute(
                "SELECT 1 FROM administrador_restaurante WHERE usuario_id=? AND restaurante_id=?",
                (usuario_id, restaurante_id),
            ).fetchone()
            is not None
        )

    def listar_restaurantes(self, usuario_id):
        return [
            f[0]
            for f in self.conexion.execute(
                "SELECT restaurante_id FROM administrador_restaurante WHERE usuario_id=?",
                (usuario_id,),
            )
        ]


class SqliteMesaDAO(MesaDAO):
    def __init__(self, conexion):
        self.conexion = conexion

    def buscar_por_id(self, id):
        f = self.conexion.execute("SELECT * FROM mesa WHERE id=?", (id,)).fetchone()
        return mesa_de_fila(f) if f else None

    def listar(self, restaurante_id):
        return [
            mesa_de_fila(f)
            for f in self.conexion.execute(
                "SELECT * FROM mesa WHERE restaurante_id=? ORDER BY id", (restaurante_id,)
            )
        ]

    def listar_candidatas(self, restaurante_id, personas):
        return [
            mesa_de_fila(f)
            for f in self.conexion.execute(
                "SELECT * FROM mesa WHERE restaurante_id=? AND activa=1 AND capacidad>=? ORDER BY capacidad,id",
                (restaurante_id, personas),
            )
        ]

    def guardar(self, mesa):
        valores = (mesa.numero, mesa.capacidad, int(mesa.activa))
        if mesa.id is None:
            cur = self.conexion.execute(
                "INSERT INTO mesa(numero,capacidad,activa,restaurante_id) VALUES(?,?,?,?)",
                (*valores, mesa.restaurante_id),
            )
            return replace(mesa, id=cur.lastrowid)
        self.conexion.execute(
            "UPDATE mesa SET numero=?,capacidad=?,activa=? WHERE id=? AND restaurante_id=?",
            (*valores, mesa.id, mesa.restaurante_id),
        )
        return mesa


class SqliteHorarioDAO(HorarioDAO):
    def __init__(self, conexion):
        self.conexion = conexion

    def listar_por_dia(self, restaurante_id, dia):
        return [h for h in self.listar(restaurante_id) if h.dia_semana == dia]

    def listar(self, restaurante_id):
        return [
            horario_de_fila(f)
            for f in self.conexion.execute(
                "SELECT * FROM horario_atencion WHERE restaurante_id=? ORDER BY dia_semana,apertura",
                (restaurante_id,),
            )
        ]

    def buscar_por_id(self, id):
        f = self.conexion.execute("SELECT * FROM horario_atencion WHERE id=?", (id,)).fetchone()
        return horario_de_fila(f) if f else None

    def guardar(self, horario):
        v = (
            horario.dia_semana,
            horario.apertura.strftime("%H:%M"),
            horario.cierre.strftime("%H:%M"),
        )
        if horario.id is None:
            cur = self.conexion.execute(
                "INSERT INTO horario_atencion(dia_semana,apertura,cierre,restaurante_id) VALUES(?,?,?,?)",
                (*v, horario.restaurante_id),
            )
            return replace(horario, id=cur.lastrowid)
        self.conexion.execute(
            "UPDATE horario_atencion SET dia_semana=?,apertura=?,cierre=? WHERE id=? AND restaurante_id=?",
            (*v, horario.id, horario.restaurante_id),
        )
        return horario

    def eliminar_franja(self, id):
        self.conexion.execute("DELETE FROM horario_atencion WHERE id=?", (id,))


class SqliteReservaDAO(ReservaDAO):
    CONSULTA = "SELECT r.*,m.restaurante_id FROM reserva r JOIN mesa m ON m.id=r.mesa_id "

    def __init__(self, conexion):
        self.conexion = conexion

    def buscar_por_id(self, id):
        return reserva_de_fila(
            self.conexion.execute(self.CONSULTA + "WHERE r.id=?", (id,)).fetchone()
        )

    def buscar_por_token(self, token):
        return reserva_de_fila(
            self.conexion.execute(self.CONSULTA + "WHERE r.token_operacion=?", (token,)).fetchone()
        )

    def buscar_solapadas(self, mesa_id, inicio, fin):
        return [
            reserva_de_fila(f)
            for f in self.conexion.execute(
                self.CONSULTA
                + "WHERE r.mesa_id=? AND r.estado='CONFIRMADA' AND r.inicio<? AND r.fin>?",
                (mesa_id, iso(fin), iso(inicio)),
            )
        ]

    def listar(self, cliente_id=None, restaurante_ids=None):
        condiciones, valores = [], []
        if cliente_id is not None:
            condiciones.append("r.cliente_id=?")
            valores.append(cliente_id)
        if restaurante_ids is not None:
            if not restaurante_ids:
                return []
            condiciones.append(
                "m.restaurante_id IN (" + ",".join("?" for _ in restaurante_ids) + ")"
            )
            valores.extend(restaurante_ids)
        filtro = "WHERE " + " AND ".join(condiciones) if condiciones else ""
        return [
            reserva_de_fila(f)
            for f in self.conexion.execute(
                self.CONSULTA + filtro + " ORDER BY r.inicio DESC,r.id DESC", valores
            )
        ]

    def listar_vigentes(self, restaurante_id, ahora):
        return [
            reserva_de_fila(f)
            for f in self.conexion.execute(
                self.CONSULTA + "WHERE m.restaurante_id=? AND r.estado='CONFIRMADA' AND r.fin>?",
                (restaurante_id, iso(ahora)),
            )
        ]

    def guardar(self, reserva):
        d = reserva.datos
        cur = self.conexion.execute(
            "INSERT INTO reserva(cliente_id,creado_por_id,mesa_id,inicio,fin,personas,observaciones,"
            "estado,fecha_creacion,token_operacion) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (
                reserva.cliente_id,
                reserva.creado_por_id,
                reserva.mesa_id,
                iso(d.inicio),
                iso(reserva.fin),
                d.personas,
                d.observaciones,
                reserva.estado,
                iso(reserva.fecha_creacion),
                reserva.token_operacion,
            ),
        )
        return self.buscar_por_id(cur.lastrowid)

    def cancelar(self, reserva):
        self.conexion.execute(
            "UPDATE reserva SET estado=? WHERE id=?", (reserva.estado, reserva.id)
        )
