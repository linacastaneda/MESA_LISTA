# Contrato del patrón creacional Prototype.

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Prototipo(ABC, Generic[T]):
    @abstractmethod
    def clonar(self) -> T:
        # Devuelve un objeto independiente con los mismos datos editables.
        raise NotImplementedError