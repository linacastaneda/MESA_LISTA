#Errores estables que pueden comunicarse sin filtrar detalles de SQLite.


class ErrorAplicacion(Exception):
    codigo_http = 422

    def __init__(self, mensaje, campo=None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.campo = campo


class Validacion(ErrorAplicacion):
    pass


class AccesoDenegado(ErrorAplicacion):
    codigo_http = 403


class NoEncontrado(ErrorAplicacion):
    codigo_http = 404


class Conflicto(ErrorAplicacion):
    codigo_http = 409


class SinDisponibilidad(Conflicto):
    pass


class ServicioOcupado(ErrorAplicacion):
    codigo_http = 503
