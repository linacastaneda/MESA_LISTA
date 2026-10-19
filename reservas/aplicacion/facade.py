#Facade: puerta de entrada a los casos de uso compartidos por ambos roles.

from reservas.modelo.entidades import Rol
from reservas.modelo.errores import Validacion


class ReservaFacade:
    def __init__(self, crear_uow, acceso, disponibilidad, servicio_reserva, reloj):
        self.crear_uow = crear_uow
        self.acceso = acceso
        self.disponibilidad = disponibilidad
        self.servicio_reserva = servicio_reserva
        self.reloj = reloj

    def crear_reserva(self, actor_id, datos, token, cliente_id=None):
        return self.servicio_reserva.crear(actor_id, datos, token, cliente_id)

    def cancelar_reserva(self, actor_id, reserva_id):
        return self.servicio_reserva.cancelar(actor_id, reserva_id)

    def consultar_disponibilidad(self, actor_id, datos):
        with self.crear_uow() as u:
            actor = self.acceso.actor(u, actor_id)
            self.acceso.restaurante(u, actor, datos.restaurante_id)
            return self.disponibilidad.seleccionar(u, datos, self.reloj())

    def horarios_disponibles(self, actor_id, restaurante_id, fecha, personas):
        with self.crear_uow() as u:
            actor = self.acceso.actor(u, actor_id)
            self.acceso.restaurante(u, actor, restaurante_id)
            return self.disponibilidad.horarios_del_dia(
                u, restaurante_id, fecha, personas, self.reloj()
            )

    def preparar_repeticion(self, actor_id, reserva_id):
        with self.crear_uow() as u:
            actor = self.acceso.actor(u, actor_id)
            reserva = self.acceso.reserva(u, actor, reserva_id)
            return reserva.datos.clonar()

    def listar_reservas(self, actor_id, restaurante_id=None, fecha=None, estado=None):
        with self.crear_uow() as u:
            actor = self.acceso.actor(u, actor_id)
            if restaurante_id:
                self.acceso.restaurante(u, actor, restaurante_id, exigir_activo=False)
            if estado and estado not in ("CONFIRMADA", "CANCELADA"):
                raise Validacion("El estado indicado no es válido.")
            if actor.rol == Rol.CLIENTE:
                reservas = u.reservas.listar(cliente_id=actor.id)
            else:
                reservas = u.reservas.listar(
                    restaurante_ids=u.asignaciones.listar_restaurantes(actor.id)
                )
            return [
                self._detalle(u, r)
                for r in reservas
                if (not restaurante_id or r.datos.restaurante_id == restaurante_id)
                and (not estado or r.estado == estado)
                and (not fecha or r.inicio.astimezone(self.disponibilidad.zona).date() == fecha)
            ]

    def obtener_detalle(self, actor_id, reserva_id):
        with self.crear_uow() as u:
            actor = self.acceso.actor(u, actor_id)
            return self._detalle(u, self.acceso.reserva(u, actor, reserva_id))

    @staticmethod
    def _detalle(u, reserva):
        return {
            "reserva": reserva,
            "restaurante": u.restaurantes.buscar_por_id(reserva.datos.restaurante_id),
            "mesa": u.mesas.buscar_por_id(reserva.mesa_id),
            "cliente": u.usuarios.buscar_por_id(reserva.cliente_id),
        }
