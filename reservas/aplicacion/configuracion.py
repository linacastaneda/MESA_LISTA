from reservas.dominio.errores import AccesoDenegado, Conflicto, Validacion


class ServicioConfiguracion:
    def __init__(self, crear_uow, acceso, disponibilidad, reloj):
        self.crear_uow = crear_uow
        self.acceso = acceso
        self.disponibilidad = disponibilidad
        self.reloj = reloj

    def _autorizar(self, u, actor_id, restaurante_id):
        actor = self.acceso.actor(u, actor_id)
        self.acceso.administrador(actor)
        self.acceso.restaurante(u, actor, restaurante_id)

    def guardar_mesa(self, actor_id, mesa):
        with self.crear_uow() as u:
            u.iniciar_escritura()
            self._autorizar(u, actor_id, mesa.restaurante_id)
            if mesa.id:
                anterior = u.mesas.buscar_por_id(mesa.id)
                if not anterior or anterior.restaurante_id != mesa.restaurante_id:
                    raise AccesoDenegado("No puedes modificar esa mesa.")
                vigentes = u.reservas.listar_vigentes(mesa.restaurante_id, self.reloj())
                if any(
                    r.mesa_id == mesa.id and (not mesa.activa or r.datos.personas > mesa.capacidad)
                    for r in vigentes
                ):
                    raise Conflicto(
                        "La mesa tiene reservas vigentes incompatibles con este cambio."
                    )
            guardada = u.mesas.guardar(mesa)
            u.confirmar()
            return guardada

    def guardar_horario(self, actor_id, horario):
        with self.crear_uow() as u:
            u.iniciar_escritura()
            self._autorizar(u, actor_id, horario.restaurante_id)
            if horario.id:
                anterior = u.horarios.buscar_por_id(horario.id)
                if not anterior or anterior.restaurante_id != horario.restaurante_id:
                    raise AccesoDenegado("No puedes modificar esa franja.")
            propuestas = [
                h for h in u.horarios.listar(horario.restaurante_id) if h.id != horario.id
            ]
            if any(
                h.dia_semana == horario.dia_semana
                and horario.apertura < h.cierre
                and horario.cierre > h.apertura
                for h in propuestas
            ):
                raise Validacion(
                    "La franja se superpone con otro horario del mismo día.", "apertura"
                )
            propuestas.append(horario)
            self._proteger_reservas(u, horario.restaurante_id, propuestas)
            guardado = u.horarios.guardar(horario)
            u.confirmar()
            return guardado

    def eliminar_horario(self, actor_id, restaurante_id, horario_id):
        with self.crear_uow() as u:
            u.iniciar_escritura()
            self._autorizar(u, actor_id, restaurante_id)
            horario = u.horarios.buscar_por_id(horario_id)
            if not horario or horario.restaurante_id != restaurante_id:
                raise AccesoDenegado("No puedes eliminar esa franja.")
            propuestas = [h for h in u.horarios.listar(restaurante_id) if h.id != horario_id]
            self._proteger_reservas(u, restaurante_id, propuestas)
            u.horarios.eliminar_franja(horario_id)
            u.confirmar()

    def _proteger_reservas(self, u, restaurante_id, propuestas):
        for reserva in u.reservas.listar_vigentes(restaurante_id, self.reloj()):
            if not self.disponibilidad.cabe_en_franjas(reserva.inicio, reserva.fin, propuestas):
                raise Conflicto(
                    "Ese cambio dejaría una reserva vigente fuera del horario de atención."
                )
