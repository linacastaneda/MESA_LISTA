from reservas.modelo.entidades import Rol


class ServicioCatalogos:
    def __init__(self, crear_uow, acceso):
        self.crear_uow = crear_uow
        self.acceso = acceso

    def restaurantes(self, actor_id, nombre="", ciudad=""):
        with self.crear_uow() as u:
            actor = self.acceso.actor(u, actor_id)
            resultados = [r for r in u.restaurantes.buscar(nombre.strip(), ciudad.strip()) if r.id == 1]
            if actor.rol == Rol.ADMINISTRADOR:
                ids = u.asignaciones.listar_restaurantes(actor.id)
                resultados = [r for r in resultados if r.id in ids]
            return resultados

    def clientes(self, actor_id):
        with self.crear_uow() as u:
            actor = self.acceso.actor(u, actor_id)
            self.acceso.administrador(actor)
            return u.usuarios.listar_clientes()

    def configuracion(self, actor_id, restaurante_id):
        with self.crear_uow() as u:
            actor = self.acceso.actor(u, actor_id)
            self.acceso.administrador(actor)
            restaurante = self.acceso.restaurante(u, actor, restaurante_id)
            return {
                "restaurante": restaurante,
                "mesas": u.mesas.listar(restaurante_id),
                "horarios": u.horarios.listar(restaurante_id),
            }
