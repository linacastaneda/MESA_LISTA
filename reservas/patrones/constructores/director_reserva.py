"""Participante del patrón Builder."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from reservas.modelo.entidades import DatosReserva, Mesa, Reserva
from reservas.modelo.errores import Validacion
from reservas.patrones.constructores.constructor_reserva import ConstructorReserva
from reservas.patrones.constructores.contexto_reserva import ContextoReserva

class DirectorReserva:
    def __init__(self, constructor: ConstructorReserva):
        self.constructor = constructor

    def preparar(self, contexto: ContextoReserva) -> Reserva:
        b = self.constructor
        b.reiniciar()
        b.con_cliente(contexto.cliente_id)
        b.con_mesa(contexto.mesa)
        b.con_intervalo(contexto.datos.inicio, contexto.fin)
        b.con_detalles(contexto.datos.personas, contexto.datos.observaciones)
        b.con_auditoria(contexto.creado_por_id, contexto.ahora, contexto.token)
        return b.construir()
