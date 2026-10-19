"""Participante del patrón Builder."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from reservas.modelo.entidades import DatosReserva, Mesa, Reserva
from reservas.modelo.errores import Validacion

@dataclass(frozen=True)
class ContextoReserva:
    cliente_id: int
    creado_por_id: int
    mesa: Mesa
    datos: DatosReserva
    fin: datetime
    ahora: datetime
    token: str
