import re
from collections.abc import Callable

from reservas.aplicacion.contratos import UnidadTrabajo
from reservas.dominio.entidades import Rol
from reservas.dominio.errores import Conflicto, Validacion
from reservas.patrones.builder import ContextoReserva, DirectorReserva, ReservaBuilder


class ServicioReserva:
    def __init__(self, crear_uow: Callable[[], UnidadTrabajo], acceso, disponibilidad, reloj):
        self.crear_uow = crear_uow
        self.acceso = acceso
        self.disponibilidad = disponibilidad
        self.reloj = reloj

    def crear(self, actor_id, datos, token, cliente_id=None):
        datos.validar()
        if not isinstance(token, str) or not re.fullmatch(r"[A-Za-z0-9_-]{20,128}", token):
            raise Validacion("Abre un formulario nuevo para obtener un token válido.")
        with self.crear_uow() as u:
            # La comprobación definitiva comienza DESPUÉS de reservar la escritura.
            u.iniciar_escritura()
            actor = self.acceso.actor(u, actor_id)
            self.acceso.restaurante(u, actor, datos.restaurante_id)
            cliente_id = actor.id if actor.rol == Rol.CLIENTE else cliente_id
            cliente = u.usuarios.buscar_por_id(cliente_id) if cliente_id else None
            if not cliente or not cliente.activo or cliente.rol != Rol.CLIENTE:
                raise Validacion("Selecciona un cliente activo.", "cliente_id")
            existente = u.reservas.buscar_por_token(token)
            if existente:
                if (
                    existente.creado_por_id != actor.id
                    or existente.cliente_id != cliente_id
                    or existente.datos != datos
                ):
                    raise Conflicto(
                        "El token ya fue utilizado para otra solicitud. Abre una reserva nueva."
                    )
                u.confirmar()
                return existente
            ahora = self.reloj()
            mesa, fin = self.disponibilidad.seleccionar(u, datos, ahora)
            contexto = ContextoReserva(cliente_id, actor.id, mesa, datos, fin, ahora, token)
            reserva = DirectorReserva(ReservaBuilder()).preparar(contexto)
            persistida = u.reservas.guardar(reserva)
            u.confirmar()
            return persistida

    def cancelar(self, actor_id, reserva_id):
        with self.crear_uow() as u:
            u.iniciar_escritura()
            actor = self.acceso.actor(u, actor_id)
            reserva = self.acceso.reserva(u, actor, reserva_id)
            if reserva.cancelar(self.reloj()):
                u.reservas.cancelar(reserva)
            u.confirmar()
            return reserva
