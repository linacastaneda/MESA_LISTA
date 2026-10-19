"""Entidad del dominio HorarioAtencion."""
from dataclasses import dataclass, replace
from datetime import datetime, time
from enum import StrEnum
from reservas.modelo.errores import Conflicto, Validacion
from reservas.patrones.prototype import Prototipo

@dataclass(frozen=True)
class HorarioAtencion:
    id: int | None
    restaurante_id: int
    dia_semana: int
    apertura: time
    cierre: time

    def __post_init__(self):
        if type(self.dia_semana) is not int or not 1 <= self.dia_semana <= 7:
            raise Validacion("Selecciona un día válido.", "dia_semana")
        if self.apertura >= self.cierre:
            raise Validacion("El cierre debe ser posterior a la apertura del mismo día.", "cierre")
        if any(t.second or t.microsecond or t.tzinfo for t in (self.apertura, self.cierre)):
            raise Validacion("Los horarios deben expresarse en horas y minutos.")
