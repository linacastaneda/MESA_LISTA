"""Entidad del dominio Rol."""
from dataclasses import dataclass, replace
from datetime import datetime, time
from enum import StrEnum
from reservas.modelo.errores import Conflicto, Validacion
from reservas.patrones.prototype import Prototipo

class Rol(StrEnum):
    CLIENTE = "CLIENTE"
    ADMINISTRADOR = "ADMINISTRADOR"
