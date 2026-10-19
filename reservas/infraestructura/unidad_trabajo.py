#Una conexión por operación; commit únicamente en la unidad de trabajo.

import sqlite3
from pathlib import Path

from reservas.aplicacion.contratos import UnidadTrabajo
from reservas.modelo.errores import Conflicto, ServicioOcupado
from reservas.infraestructura.dao_sqlite import (
    SqliteAsignacionAdminDAO,
    SqliteHorarioDAO,
    SqliteMesaDAO,
    SqliteReservaDAO,
    SqliteRestauranteDAO,
    SqliteUsuarioDAO,
)


def conectar(ruta, timeout=5.0):
    # No se crea silenciosamente una base vacía por una ruta incorrecta.
    uri = Path(ruta).resolve().as_uri() + "?mode=rw"
    conexion = sqlite3.connect(uri, uri=True, timeout=timeout, isolation_level=None)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys=ON")
    return conexion


class UnidadTrabajoSqlite(UnidadTrabajo):
    def __init__(self, ruta, timeout=5.0):
        self.ruta = ruta
        self.timeout = timeout
        self.conexion = None

    def __enter__(self):
        self.conexion = conectar(self.ruta, self.timeout)
        self.usuarios = SqliteUsuarioDAO(self.conexion)
        self.restaurantes = SqliteRestauranteDAO(self.conexion)
        self.asignaciones = SqliteAsignacionAdminDAO(self.conexion)
        self.mesas = SqliteMesaDAO(self.conexion)
        self.horarios = SqliteHorarioDAO(self.conexion)
        self.reservas = SqliteReservaDAO(self.conexion)
        return self

    def iniciar_escritura(self):
        self.conexion.execute("BEGIN IMMEDIATE")

    def confirmar(self):
        self.conexion.commit()

    def revertir(self):
        self.conexion.rollback()

    def __exit__(self, tipo, valor, traza):
        try:
            if self.conexion.in_transaction:
                self.revertir()
        finally:
            self.conexion.close()
        if isinstance(valor, sqlite3.IntegrityError):
            raise Conflicto(
                "El cambio entra en conflicto con los datos existentes. "
                "Revisa duplicados y disponibilidad."
            ) from valor
        if isinstance(valor, sqlite3.OperationalError) and valor.sqlite_errorcode in (
            sqlite3.SQLITE_BUSY,
            sqlite3.SQLITE_LOCKED,
        ):
            raise ServicioOcupado(
                "El sistema está atendiendo otra operación. "
                "Tus datos se conservaron; vuelve a intentarlo."
            ) from valor
        return False
