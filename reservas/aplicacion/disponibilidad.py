from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from reservas.dominio.entidades import DatosReserva
from reservas.dominio.errores import SinDisponibilidad, Validacion


class ServicioDisponibilidad:
    def __init__(self, duracion_minutos=90, zona="America/Bogota"):
        if type(duracion_minutos) is not int or duracion_minutos <= 0:
            raise ValueError("La duración debe ser un entero positivo.")
        self.duracion = timedelta(minutes=duracion_minutos)
        self.zona = ZoneInfo(zona)

    def cabe_en_franjas(self, inicio, fin, franjas, comprobar_paso=False):
        inicio, fin = inicio.astimezone(self.zona), fin.astimezone(self.zona)
        if inicio.date() != fin.date():
            return False
        for franja in franjas:
            if franja.dia_semana != inicio.isoweekday():
                continue
            apertura = datetime.combine(inicio.date(), franja.apertura, self.zona)
            cierre = datetime.combine(inicio.date(), franja.cierre, self.zona)
            if apertura <= inicio and fin <= cierre:
                if not comprobar_paso or (inicio - apertura).total_seconds() % 1800 == 0:
                    return True
        return False

    def seleccionar(self, u, datos: DatosReserva, ahora):
        datos.validar()
        if datos.inicio <= ahora:
            raise Validacion("Selecciona una fecha y una hora futuras.", "inicio")
        fin = datos.inicio + self.duracion
        franjas = u.horarios.listar_por_dia(
            datos.restaurante_id, datos.inicio.astimezone(self.zona).isoweekday()
        )
        if not self.cabe_en_franjas(datos.inicio, fin, franjas, comprobar_paso=True):
            raise Validacion(
                "Elige una hora de atención válida; la reserva completa debe caber "
                "antes del cierre y respetar los pasos de 30 minutos.",
                "inicio",
            )
        candidatas = u.mesas.listar_candidatas(datos.restaurante_id, datos.personas)
        if not candidatas:
            raise SinDisponibilidad(
                "No hay una mesa con capacidad suficiente para ese grupo.", "personas"
            )
        for mesa in candidatas:
            if not u.reservas.buscar_solapadas(mesa.id, datos.inicio, fin):
                return mesa, fin
        raise SinDisponibilidad(
            "Ese horario ya no tiene mesas disponibles. Prueba otra hora.", "inicio"
        )

    def horarios_del_dia(self, u, restaurante_id, fecha, personas, ahora):
        if type(personas) is not int or personas <= 0:
            raise Validacion("Ingresa un número de personas mayor que cero.", "personas")
        franjas = u.horarios.listar_por_dia(restaurante_id, fecha.isoweekday())
        candidatas = u.mesas.listar_candidatas(restaurante_id, personas)
        opciones = []
        for f in franjas:
            inicio = datetime.combine(fecha, f.apertura, self.zona)
            cierre = datetime.combine(fecha, f.cierre, self.zona)
            while inicio + self.duracion <= cierre:
                if inicio > ahora:
                    fin = inicio + self.duracion
                    libre = any(
                        not u.reservas.buscar_solapadas(m.id, inicio, fin) for m in candidatas
                    )
                    opciones.append({"valor": inicio.strftime("%H:%M"), "disponible": libre})
                inicio += timedelta(minutes=30)
        return opciones


def reloj_utc():
    return datetime.now(UTC)
