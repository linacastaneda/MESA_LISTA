"""Excepción de dominio."""
from .error_aplicacion import ErrorAplicacion

class AccesoDenegado(ErrorAplicacion):
    codigo_http = 403
