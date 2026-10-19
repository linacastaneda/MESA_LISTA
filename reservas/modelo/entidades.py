#Dominio sin dependencias de Flask, SQL ni sesiones web.

from dataclasses import dataclass, replace
from datetime import datetime, time
from enum import StrEnum

from reservas.modelo.errores import Conflicto, Validacion
from reservas.patrones.prototype import Prototipo


class Rol(StrEnum):
    CLIENTE = "CLIENTE"
    ADMINISTRADOR = "ADMINISTRADOR"


class EstadoReserva(StrEnum):
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"


@dataclass(frozen=True)
class Usuario:
    id: int
    nombre: str
    correo: str
    hash_clave: str
    rol: Rol
    activo: bool = True


@dataclass(frozen=True)
class Restaurante:
    id: int
    nombre: str
    ciudad: str
    direccion: str
    activo: bool = True


@dataclass(frozen=True)
class AsignacionAdministrador:
    usuario_id: int
    restaurante_id: int


@dataclass(frozen=True)
class Mesa:
    id: int | None
    restaurante_id: int
    numero: str
    capacidad: int
    activa: bool = True

    def __post_init__(self):
        if not self.numero.strip() or len(self.numero) > 20:
            raise Validacion("El número de mesa debe tener entre 1 y 20 caracteres.", "numero")
        if type(self.capacidad) is not int or self.capacidad <= 0:
            raise Validacion("La capacidad debe ser un entero positivo.", "capacidad")


@dataclass(frozen=True)
class HorarioAtencion:
    id: int | None
    restaurante_id: int
    dia_semana: int
    apertura: time
    cierre: time

    def __post_init__(self):
        if type(self.dia_semana) is not int or not 1 <= self.dia_semana <= 7:
            raise Validacion("Selecciona un día válido.", "dia_semana")
        if self.apertura >= self.cierre:
            raise Validacion("El cierre debe ser posterior a la apertura del mismo día.", "cierre")
        if any(t.second or t.microsecond or t.tzinfo for t in (self.apertura, self.cierre)):
            raise Validacion("Los horarios deben expresarse en horas y minutos.")


@dataclass
class DatosReserva(Prototipo["DatosReserva"]):
    restaurante_id: int
    inicio: datetime
    personas: int
    observaciones: str = ""

    def validar(self):
        if type(self.personas) is not int or self.personas <= 0:
            raise Validacion("Ingresa un número entero de personas mayor que cero.", "personas")
        if not isinstance(self.inicio, datetime) or self.inicio.tzinfo is None:
            raise Validacion("La fecha debe incluir una zona horaria válida.", "inicio")
        if not isinstance(self.observaciones, str) or len(self.observaciones) > 500:
            raise Validacion("Las observaciones admiten hasta 500 caracteres.", "observaciones")
        if type(self.restaurante_id) is not int or self.restaurante_id <= 0:
            raise Validacion("Selecciona un restaurante válido.", "restaurante_id")

    def clonar(self) -> "DatosReserva":
        #Todos los atributos actuales son inmutables. Si se agregan listas, deberá ampliarse esta copia para no compartir esas colecciones.
        return replace(self)


class Reserva:
    #Encapsula estado y datos; solo cancelar cambia el estado del dominio.

    def __init__(
        self,
        id,
        cliente_id,
        creado_por_id,
        mesa_id,
        datos,
        fin,
        fecha_creacion,
        token_operacion,
        estado=EstadoReserva.CONFIRMADA,
    ):
        datos.validar()
        if fin.tzinfo is None or fin <= datos.inicio:
            raise Validacion("El intervalo de reserva no es válido.", "inicio")
        if any(type(v) is not int or v <= 0 for v in (cliente_id, creado_por_id, mesa_id)):
            raise Validacion("La reserva requiere cliente, creador y mesa.")
        if fecha_creacion.tzinfo is None or not token_operacion:
            raise Validacion("La reserva requiere fecha de creación y token de operación.")
        self.id = id
        self.cliente_id = cliente_id
        self.creado_por_id = creado_por_id
        self.mesa_id = mesa_id
        self._datos = datos.clonar()
        self.fin = fin
        self.fecha_creacion = fecha_creacion
        self.token_operacion = token_operacion
        self._estado = EstadoReserva(estado)

    @property
    def datos(self):
        return self._datos.clonar()

    @property
    def inicio(self):
        return self._datos.inicio

    @property
    def estado(self):
        return self._estado

    def cancelar(self, ahora):
        if self._estado == EstadoReserva.CANCELADA:
            return False
        if self.inicio <= ahora:
            raise Conflicto("Una reserva que ya comenzó no se puede cancelar.")
        self._estado = EstadoReserva.CANCELADA
        return True
