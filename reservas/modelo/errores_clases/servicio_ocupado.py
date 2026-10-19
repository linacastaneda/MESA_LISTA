"""Excepción de dominio."""
from .error_aplicacion import ErrorAplicacion

class ServicioOcupado(ErrorAplicacion):
    codigo_http = 503
