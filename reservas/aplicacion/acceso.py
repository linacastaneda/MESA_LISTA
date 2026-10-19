from reservas.aplicacion.contratos import UnidadTrabajo
from reservas.modelo.entidades import Rol
from reservas.modelo.errores import AccesoDenegado, NoEncontrado


class ServicioAcceso:
    def actor(self, u: UnidadTrabajo, actor_id):
        actor = u.usuarios.buscar_por_id(actor_id)
        if not actor or not actor.activo:
            raise AccesoDenegado("La cuenta no está autorizada para realizar esta operación.")
        return actor

    def administrador(self, actor):
        if actor.rol != Rol.ADMINISTRADOR:
            raise AccesoDenegado("Esta sección está disponible para administradores.")

    def restaurante(self, u, actor, restaurante_id, exigir_activo=True):
        restaurante = u.restaurantes.buscar_por_id(restaurante_id)
        if not restaurante:
            raise NoEncontrado("No se encontró el restaurante.")
        if actor.rol == Rol.ADMINISTRADOR and not u.asignaciones.puede_gestionar(
            actor.id, restaurante_id
        ):
            raise AccesoDenegado("No tienes permiso para gestionar ese restaurante.")
        if exigir_activo and not restaurante.activo:
            raise AccesoDenegado("El restaurante no está disponible.")
        return restaurante

    def reserva(self, u, actor, reserva_id):
        reserva = u.reservas.buscar_por_id(reserva_id)
        if not reserva:
            raise NoEncontrado("No se encontró la reserva.")
        if actor.rol == Rol.CLIENTE:
            if reserva.cliente_id != actor.id:
                raise AccesoDenegado("No tienes permiso para consultar esa reserva.")
        else:
            self.restaurante(u, actor, reserva.datos.restaurante_id, exigir_activo=False)
        return reserva
