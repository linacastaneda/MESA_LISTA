"""Entidad del dominio Reserva."""
from dataclasses import dataclass, replace
from datetime import datetime, time
from enum import StrEnum
from reservas.modelo.errores import Conflicto, Validacion
from reservas.patrones.prototype import Prototipo
from .datos_reserva import DatosReserva
from .estado_reserva import EstadoReserva

class Reserva:
    #Encapsula estado y datos; solo cancelar cambia el estado del dominio.

    def __init__(
        self,
        id,
        cliente_id,
        creado_por_id,
        mesa_id,
        datos,
        fin,
        fecha_creacion,
        token_operacion,
        estado=EstadoReserva.CONFIRMADA,
    ):
        datos.validar()
        if fin.tzinfo is None or fin <= datos.inicio:
            raise Validacion("El intervalo de reserva no es válido.", "inicio")
        if any(type(v) is not int or v <= 0 for v in (cliente_id, creado_por_id, mesa_id)):
            raise Validacion("La reserva requiere cliente, creador y mesa.")
        if fecha_creacion.tzinfo is None or not token_operacion:
            raise Validacion("La reserva requiere fecha de creación y token de operación.")
        self.id = id
        self.cliente_id = cliente_id
        self.creado_por_id = creado_por_id
        self.mesa_id = mesa_id
        self._datos = datos.clonar()
        self.fin = fin
        self.fecha_creacion = fecha_creacion
        self.token_operacion = token_operacion
        self._estado = EstadoReserva(estado)

    @property
    def datos(self):
        return self._datos.clonar()

    @property
    def inicio(self):
        return self._datos.inicio

    @property
    def estado(self):
        return self._estado

    def cancelar(self, ahora):
        if self._estado == EstadoReserva.CANCELADA:
            return False
        if self.inicio <= ahora:
            raise Conflicto("Una reserva que ya comenzó no se puede cancelar.")
        self._estado = EstadoReserva.CANCELADA
        return True
