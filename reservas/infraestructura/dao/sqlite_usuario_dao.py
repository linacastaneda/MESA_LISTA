"""Implementación DAO para SQLite."""
from dataclasses import replace
from datetime import UTC, datetime, time
from reservas.aplicacion.contratos import AsignacionAdminDAO, HorarioDAO, MesaDAO, ReservaDAO, RestauranteDAO, UsuarioDAO
from reservas.modelo.entidades import DatosReserva, HorarioAtencion, Mesa, Reserva, Restaurante, Rol, Usuario
from reservas.infraestructura.mapeadores import iso, usuario_de_fila, mesa_de_fila, horario_de_fila, reserva_de_fila

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
