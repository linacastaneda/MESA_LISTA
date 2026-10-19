"""Contrato de persistencia."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Self
from reservas.modelo.entidades import HorarioAtencion, Mesa, Reserva, Restaurante, Usuario
from reservas.aplicacion.puertos.usuario_dao import UsuarioDAO
from reservas.aplicacion.puertos.restaurante_dao import RestauranteDAO
from reservas.aplicacion.puertos.asignacion_admin_dao import AsignacionAdminDAO
from reservas.aplicacion.puertos.mesa_dao import MesaDAO
from reservas.aplicacion.puertos.horario_dao import HorarioDAO
from reservas.aplicacion.puertos.reserva_dao import ReservaDAO

class UnidadTrabajo(ABC):
    usuarios: UsuarioDAO
    restaurantes: RestauranteDAO
    asignaciones: AsignacionAdminDAO
    mesas: MesaDAO
    horarios: HorarioDAO
    reservas: ReservaDAO

    @abstractmethod
    def __enter__(self) -> Self: ...
    @abstractmethod
    def __exit__(self, tipo, valor, traza): ...
    @abstractmethod
    def iniciar_escritura(self) -> None: ...
    @abstractmethod
    def confirmar(self) -> None: ...
    @abstractmethod
    def revertir(self) -> None: ...
