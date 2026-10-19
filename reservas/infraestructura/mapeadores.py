"""Funciones auxiliares de conversión fila/entidad."""

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
from reservas.modelo.entidades import (
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


