"""Excepción de dominio."""

class ErrorAplicacion(Exception):
    codigo_http = 422

    def __init__(self, mensaje, campo=None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.campo = campo
