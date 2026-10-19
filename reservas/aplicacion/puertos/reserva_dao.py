"""Contrato de persistencia."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Self
from reservas.modelo.entidades import HorarioAtencion, Mesa, Reserva, Restaurante, Usuario


class ReservaDAO(ABC):
    @abstractmethod
    def buscar_por_id(self, id: int) -> Reserva | None: ...
    @abstractmethod
    def buscar_por_token(self, token: str) -> Reserva | None: ...
    @abstractmethod
    def buscar_solapadas(self, mesa_id: int, inicio: datetime, fin: datetime) -> list[Reserva]: ...
    @abstractmethod
    def listar(
        self, cliente_id: int | None = None, restaurante_ids: list[int] | None = None
    ) -> list[Reserva]: ...
    @abstractmethod
    def listar_vigentes(self, restaurante_id: int, ahora: datetime) -> list[Reserva]: ...
    @abstractmethod
    def guardar(self, reserva: Reserva) -> Reserva: ...
    @abstractmethod
    def cancelar(self, reserva: Reserva) -> None: ...
