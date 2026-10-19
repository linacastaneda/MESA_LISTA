"""Implementación DAO para SQLite."""
from dataclasses import replace
from datetime import UTC, datetime, time
from reservas.aplicacion.contratos import AsignacionAdminDAO, HorarioDAO, MesaDAO, ReservaDAO, RestauranteDAO, UsuarioDAO
from reservas.modelo.entidades import DatosReserva, HorarioAtencion, Mesa, Reserva, Restaurante, Rol, Usuario
from reservas.infraestructura.mapeadores import iso, usuario_de_fila, mesa_de_fila, horario_de_fila, reserva_de_fila

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
