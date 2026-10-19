"""Entidad del dominio DatosReserva."""
from dataclasses import dataclass, replace
from datetime import datetime, time
from enum import StrEnum
from reservas.modelo.errores import Conflicto, Validacion
from reservas.patrones.prototype import Prototipo

@dataclass
class DatosReserva(Prototipo["DatosReserva"]):
    restaurante_id: int
    inicio: datetime
    personas: int
    observaciones: str = ""

    def validar(self):
        if type(self.personas) is not int or self.personas <= 0:
            raise Validacion("Ingresa un número entero de personas mayor que cero.", "personas")
        if not isinstance(self.inicio, datetime) or self.inicio.tzinfo is None:
            raise Validacion("La fecha debe incluir una zona horaria válida.", "inicio")
        if not isinstance(self.observaciones, str) or len(self.observaciones) > 500:
            raise Validacion("Las observaciones admiten hasta 500 caracteres.", "observaciones")
        if type(self.restaurante_id) is not int or self.restaurante_id <= 0:
            raise Validacion("Selecciona un restaurante válido.", "restaurante_id")

    def clonar(self) -> "DatosReserva":
        #Todos los atributos actuales son inmutables. Si se agregan listas, deberá ampliarse esta copia para no compartir esas colecciones.
        return replace(self)
