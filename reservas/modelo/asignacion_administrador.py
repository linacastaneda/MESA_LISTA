"""Entidad del dominio AsignacionAdministrador."""
from dataclasses import dataclass, replace
from datetime import datetime, time
from enum import StrEnum
from reservas.modelo.errores import Conflicto, Validacion
from reservas.patrones.prototype import Prototipo

@dataclass(frozen=True)
class AsignacionAdministrador:
    usuario_id: int
    restaurante_id: int
