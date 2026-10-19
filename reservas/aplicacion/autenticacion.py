from werkzeug.security import check_password_hash, generate_password_hash

from reservas.patrones.adapter import UsuarioSesionAdapter


class ServicioAutenticacion:
    def __init__(self, crear_uow):
        self.crear_uow = crear_uow
        self._hash_ausente = generate_password_hash("cuenta-inexistente-solo-comparacion")

    def autenticar(self, correo, clave):
        with self.crear_uow() as u:
            usuario = u.usuarios.buscar_por_correo(correo)
            coincide = check_password_hash(
                usuario.hash_clave if usuario else self._hash_ausente, clave
            )
            if not usuario or not coincide or not usuario.activo:
                return None
            return UsuarioSesionAdapter(usuario)

    def cargar_sesion(self, identificador):
        try:
            id = int(identificador)
        except (TypeError, ValueError):
            return None
        with self.crear_uow() as u:
            usuario = u.usuarios.buscar_por_id(id)
            return UsuarioSesionAdapter(usuario) if usuario and usuario.activo else None
