#Builder: contrato, constructor concreto, director y contexto autorizado.

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from reservas.modelo.entidades import DatosReserva, Mesa, Reserva
from reservas.modelo.errores import Validacion


class ConstructorReserva(ABC):
    @abstractmethod
    def reiniciar(self): ...
    @abstractmethod
    def con_cliente(self, cliente_id): ...
    @abstractmethod
    def con_mesa(self, mesa): ...
    @abstractmethod
    def con_intervalo(self, inicio, fin): ...
    @abstractmethod
    def con_detalles(self, personas, observaciones): ...
    @abstractmethod
    def con_auditoria(self, creado_por_id, fecha_creacion, token): ...
    @abstractmethod
    def construir(self) -> Reserva: ...


class ReservaBuilder(ConstructorReserva):
    def __init__(self):
        self.reiniciar()

    def reiniciar(self):
        self._valores = {}
        return self

    def con_cliente(self, cliente_id):
        self._valores["cliente_id"] = cliente_id
        return self

    def con_mesa(self, mesa):
        self._valores["mesa"] = mesa
        return self

    def con_intervalo(self, inicio, fin):
        self._valores.update(inicio=inicio, fin=fin)
        return self

    def con_detalles(self, personas, observaciones):
        self._valores.update(personas=personas, observaciones=observaciones)
        return self

    def con_auditoria(self, creado_por_id, fecha_creacion, token):
        self._valores.update(
            creado_por_id=creado_por_id, fecha_creacion=fecha_creacion, token_operacion=token
        )
        return self

    def construir(self):
        campos = {
            "cliente_id",
            "mesa",
            "inicio",
            "fin",
            "personas",
            "observaciones",
            "creado_por_id",
            "fecha_creacion",
            "token_operacion",
        }
        if campos != self._valores.keys():
            raise Validacion("La construcción de la reserva está incompleta.")
        v = self._valores
        mesa = v["mesa"]
        if not isinstance(mesa, Mesa) or not mesa.id or not mesa.activa:
            raise Validacion("Se requiere una mesa activa persistida.")
        datos = DatosReserva(mesa.restaurante_id, v["inicio"], v["personas"], v["observaciones"])
        datos.validar()
        if datos.personas > mesa.capacidad:
            raise Validacion("La mesa no tiene capacidad para ese grupo.", "personas")
        reserva = Reserva(
            None,
            v["cliente_id"],
            v["creado_por_id"],
            mesa.id,
            datos,
            v["fin"],
            v["fecha_creacion"],
            v["token_operacion"],
        )
        self.reiniciar()
        return reserva


@dataclass(frozen=True)
class ContextoReserva:
    cliente_id: int
    creado_por_id: int
    mesa: Mesa
    datos: DatosReserva
    fin: datetime
    ahora: datetime
    token: str


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
