"""Implementación DAO para SQLite."""
from dataclasses import replace
from datetime import UTC, datetime, time
from reservas.aplicacion.contratos import AsignacionAdminDAO, HorarioDAO, MesaDAO, ReservaDAO, RestauranteDAO, UsuarioDAO
from reservas.modelo.entidades import DatosReserva, HorarioAtencion, Mesa, Reserva, Restaurante, Rol, Usuario
from reservas.infraestructura.mapeadores import iso, usuario_de_fila, mesa_de_fila, horario_de_fila, reserva_de_fila

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
