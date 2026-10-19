"""Implementación DAO para SQLite."""
from dataclasses import replace
from datetime import UTC, datetime, time
from reservas.aplicacion.contratos import AsignacionAdminDAO, HorarioDAO, MesaDAO, ReservaDAO, RestauranteDAO, UsuarioDAO
from reservas.modelo.entidades import DatosReserva, HorarioAtencion, Mesa, Reserva, Restaurante, Rol, Usuario
from reservas.infraestructura.mapeadores import iso, usuario_de_fila, mesa_de_fila, horario_de_fila, reserva_de_fila

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
