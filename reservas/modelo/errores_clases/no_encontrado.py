"""Excepción de dominio."""
from .error_aplicacion import ErrorAplicacion

class NoEncontrado(ErrorAplicacion):
    codigo_http = 404
