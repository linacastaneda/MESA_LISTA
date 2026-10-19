"""Contrato de persistencia."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Self
from reservas.modelo.entidades import HorarioAtencion, Mesa, Reserva, Restaurante, Usuario


class RestauranteDAO(ABC):
    @abstractmethod
    def buscar_por_id(self, id: int) -> Restaurante | None: ...
    @abstractmethod
    def buscar(self, nombre="", ciudad="") -> list[Restaurante]: ...
