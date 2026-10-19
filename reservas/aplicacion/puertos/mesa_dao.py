"""Contrato de persistencia."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Self
from reservas.modelo.entidades import HorarioAtencion, Mesa, Reserva, Restaurante, Usuario


class MesaDAO(ABC):
    @abstractmethod
    def buscar_por_id(self, id: int) -> Mesa | None: ...
    @abstractmethod
    def listar(self, restaurante_id: int) -> list[Mesa]: ...
    @abstractmethod
    def listar_candidatas(self, restaurante_id: int, personas: int) -> list[Mesa]: ...
    @abstractmethod
    def guardar(self, mesa: Mesa) -> Mesa: ...
