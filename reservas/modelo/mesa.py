"""Entidad del dominio Mesa."""
from dataclasses import dataclass, replace
from datetime import datetime, time
from enum import StrEnum
from reservas.modelo.errores import Conflicto, Validacion
from reservas.patrones.prototype import Prototipo

@dataclass(frozen=True)
class Mesa:
    id: int | None
    restaurante_id: int
    numero: str
    capacidad: int
    activa: bool = True

    def __post_init__(self):
        if not self.numero.strip() or len(self.numero) > 20:
            raise Validacion("El número de mesa debe tener entre 1 y 20 caracteres.", "numero")
        if type(self.capacidad) is not int or self.capacidad <= 0:
            raise Validacion("La capacidad debe ser un entero positivo.", "capacidad")
