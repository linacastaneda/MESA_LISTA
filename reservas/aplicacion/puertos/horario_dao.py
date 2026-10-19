"""Contrato de persistencia."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Self
from reservas.modelo.entidades import HorarioAtencion, Mesa, Reserva, Restaurante, Usuario


class HorarioDAO(ABC):
    @abstractmethod
    def listar_por_dia(self, restaurante_id: int, dia: int) -> list[HorarioAtencion]: ...
    @abstractmethod
    def listar(self, restaurante_id: int) -> list[HorarioAtencion]: ...
    @abstractmethod
    def buscar_por_id(self, id: int) -> HorarioAtencion | None: ...
    @abstractmethod
    def guardar(self, horario: HorarioAtencion) -> HorarioAtencion: ...
    @abstractmethod
    def eliminar_franja(self, id: int) -> None: ...
