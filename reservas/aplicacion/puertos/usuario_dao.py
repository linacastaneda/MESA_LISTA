"""Contrato de persistencia."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Self
from reservas.modelo.entidades import HorarioAtencion, Mesa, Reserva, Restaurante, Usuario


class UsuarioDAO(ABC):
    @abstractmethod
    def buscar_por_id(self, id: int) -> Usuario | None: ...
    @abstractmethod
    def buscar_por_correo(self, correo: str) -> Usuario | None: ...
    @abstractmethod
    def listar_clientes(self) -> list[Usuario]: ...
