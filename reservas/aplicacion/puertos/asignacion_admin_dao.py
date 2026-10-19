"""Contrato de persistencia."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Self
from reservas.modelo.entidades import HorarioAtencion, Mesa, Reserva, Restaurante, Usuario


class AsignacionAdminDAO(ABC):
    @abstractmethod
    def puede_gestionar(self, usuario_id: int, restaurante_id: int) -> bool: ...
    @abstractmethod
    def listar_restaurantes(self, usuario_id: int) -> list[int]: ...
