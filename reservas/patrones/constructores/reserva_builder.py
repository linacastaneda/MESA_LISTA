"""Participante del patrón Builder."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from reservas.modelo.entidades import DatosReserva, Mesa, Reserva
from reservas.modelo.errores import Validacion
from reservas.patrones.constructores.constructor_reserva import ConstructorReserva

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
