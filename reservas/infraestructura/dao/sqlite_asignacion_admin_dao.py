"""Implementación DAO para SQLite."""
from dataclasses import replace
from datetime import UTC, datetime, time
from reservas.aplicacion.contratos import AsignacionAdminDAO, HorarioDAO, MesaDAO, ReservaDAO, RestauranteDAO, UsuarioDAO
from reservas.modelo.entidades import DatosReserva, HorarioAtencion, Mesa, Reserva, Restaurante, Rol, Usuario
from reservas.infraestructura.mapeadores import iso, usuario_de_fila, mesa_de_fila, horario_de_fila, reserva_de_fila

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
