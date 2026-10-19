"""Implementación DAO para SQLite."""
from dataclasses import replace
from datetime import UTC, datetime, time
from reservas.aplicacion.contratos import AsignacionAdminDAO, HorarioDAO, MesaDAO, ReservaDAO, RestauranteDAO, UsuarioDAO
from reservas.modelo.entidades import DatosReserva, HorarioAtencion, Mesa, Reserva, Restaurante, Rol, Usuario
from reservas.infraestructura.mapeadores import iso, usuario_de_fila, mesa_de_fila, horario_de_fila, reserva_de_fila

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
