#Adapter por composición: Usuario -> contrato esperado por Flask-Login.

from reservas.modelo.entidades import Usuario


class UsuarioSesionAdapter:
    def __init__(self, usuario: Usuario):
        self.usuario = usuario

    def get_id(self):
        return str(self.usuario.id)

    @property
    def is_active(self):
        return self.usuario.activo

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False
