"""Entidad del dominio Usuario."""
from dataclasses import dataclass, replace
from datetime import datetime, time
from enum import StrEnum
from reservas.modelo.errores import Conflicto, Validacion
from reservas.patrones.prototype import Prototipo
from .rol import Rol

@dataclass(frozen=True)
class Usuario:
    id: int
    nombre: str
    correo: str
    hash_clave: str
    rol: Rol
    activo: bool = True
