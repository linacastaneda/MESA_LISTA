"""Entidad del dominio Restaurante."""
from dataclasses import dataclass, replace
from datetime import datetime, time
from enum import StrEnum
from reservas.modelo.errores import Conflicto, Validacion
from reservas.patrones.prototype import Prototipo

@dataclass(frozen=True)
class Restaurante:
    id: int
    nombre: str
    ciudad: str
    direccion: str
    activo: bool = True
