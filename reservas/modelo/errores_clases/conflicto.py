"""Excepción de dominio."""
from .error_aplicacion import ErrorAplicacion

class Conflicto(ErrorAplicacion):
    codigo_http = 409
