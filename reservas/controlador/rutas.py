"""Controladores HTTP: traducen formularios a casos de uso, sin SQL."""

import secrets
from datetime import UTC, date, datetime, time, timedelta
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from reservas.modelo.entidades import DatosReserva, HorarioAtencion, Mesa, Rol
from reservas.modelo.errores import ErrorAplicacion, Validacion
from reservas.controlador.formularios import HorarioForm, LoginForm, MesaForm, ReservaForm

web = Blueprint("web", __name__)


def servicio(nombre="reservas"):
    return current_app.extensions[nombre]


def actor_id():
    return current_user.usuario.id


def es_admin():
    return current_user.usuario.rol == Rol.ADMINISTRADOR


def entero(valor, defecto=None):
    if valor in (None, ""):
        return defecto
    try:
        numero = int(valor)
    except (ValueError, TypeError):
        raise Validacion("Se recibió un número no válido.") from None
    if numero <= 0:
        raise Validacion("Los identificadores y cantidades deben ser mayores que cero.")
    return numero


def fecha_valida(valor, defecto=None):
    if not valor:
        return defecto
    try:
        return date.fromisoformat(valor)
    except ValueError:
        raise Validacion("La fecha no es válida.", "fecha") from None


def agregar_error(form, error):
    campo = "hora" if error.campo == "inicio" else error.campo
    if campo and hasattr(form, campo):
        getattr(form, campo).errors = [error.mensaje]
    else:
        flash(error.mensaje, "error")


@web.route("/")
def inicio():
    return redirect(url_for("web.restaurantes" if current_user.is_authenticated else "web.login"))


@web.route("/health")
def salud():
    # No contiene datos privados; comprueba que el esquema está inicializado.
    try:
        with servicio("crear_uow")() as u:
            u.restaurantes.buscar()
        return {"estado": "ok"}
    except Exception:
        current_app.logger.exception("Falló la comprobación de salud")
        return {"estado": "no_disponible"}, 503


@web.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("web.reservas" if es_admin() else "web.restaurantes"))
    form = LoginForm()
    codigo = 200
    if form.validate_on_submit():
        usuario = servicio("autenticacion").autenticar(form.correo.data, form.clave.data)
        if usuario:
            session.clear()
            login_user(usuario, remember=False)
            session.permanent = True
            destino = request.args.get("next", "")
            try:
                parsed = urlsplit(destino)
            except ValueError:
                destino = ""
                parsed = urlsplit("")
            if not (
                destino.startswith("/")
                and not destino.startswith("//")
                and not parsed.netloc
                and not parsed.scheme
                and "\\" not in destino
                and not any(c in destino for c in "\r\n\t")
            ):
                destino = url_for(
                    "web.reservas"
                    if usuario.usuario.rol == Rol.ADMINISTRADOR
                    else "web.restaurantes"
                )
            return redirect(destino)
        flash("Correo o contraseña incorrectos, o cuenta no disponible.", "error")
        codigo = 401
    elif request.method == "POST":
        codigo = 422
    return render_template("login.html", form=form), codigo


@web.post("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("web.login"))


@web.get("/restaurantes")
@login_required
def restaurantes():
    nombre, ciudad = request.args.get("nombre", "")[:100], request.args.get("ciudad", "")[:100]
    opciones = servicio("catalogos").restaurantes(actor_id(), nombre, ciudad)
    return render_template("restaurantes.html", restaurantes=opciones, nombre=nombre, ciudad=ciudad)


def preparar_formulario(datos=None, cliente_id=None):
    form = ReservaForm()
    restaurantes = servicio("catalogos").restaurantes(actor_id())
    form.restaurante_id.choices = [(r.id, r.nombre + " · " + r.ciudad) for r in restaurantes]
    clientes = servicio("catalogos").clientes(actor_id()) if es_admin() else []
    form.cliente_id.choices = [(c.id, c.nombre + " · " + c.correo) for c in clientes]
    if request.method == "GET":
        zona = ZoneInfo(current_app.config["TIMEZONE"])
        manana = current_app.config["RELOJ"]().astimezone(zona).date() + timedelta(days=1)
        form.restaurante_id.data = entero(
            request.args.get("restaurante_id"),
            datos.restaurante_id if datos else (restaurantes[0].id if restaurantes else None),
        )
        form.fecha.data = fecha_valida(
            request.args.get("fecha"), datos.inicio.astimezone(zona).date() if datos else manana
        )
        form.personas.data = entero(request.args.get("personas"), datos.personas if datos else 2)
        form.hora.data = (
            datos.inicio.astimezone(zona).strftime("%H:%M")
            if datos
            else request.args.get("hora", "")
        )
        form.observaciones.data = datos.observaciones if datos else ""
        form.token_operacion.data = secrets.token_urlsafe(32)
        if es_admin():
            form.cliente_id.data = cliente_id or (clientes[0].id if clientes else None)
    return form, restaurantes


def mostrar_formulario(form, restaurantes, codigo=200, repetida=False, origen_repeticion=None):
    opciones = []
    if (
        form.restaurante_id.data
        and form.fecha.data
        and form.personas.data
        and form.personas.data > 0
    ):
        try:
            opciones = servicio().horarios_disponibles(
                actor_id(), form.restaurante_id.data, form.fecha.data, form.personas.data
            )
        except ErrorAplicacion as error:
            # Los errores de autorización no se convierten en un mensaje de disponibilidad.
            if error.codigo_http in (403, 404):
                raise
            agregar_error(form, error)
            codigo = error.codigo_http
    elegido = next((r for r in restaurantes if r.id == form.restaurante_id.data), None)
    return render_template(
        "reserva_form.html",
        form=form,
        restaurantes=restaurantes,
        opciones=opciones,
        restaurante=elegido,
        repetida=repetida,
        origen_repeticion=origen_repeticion,
    ), codigo


@web.get("/reservas/nueva")
@login_required
def nueva_reserva():
    origen = entero(request.args.get("repetir_id"))
    if origen:
        datos = servicio().preparar_repeticion(actor_id(), origen)
        detalle = servicio().obtener_detalle(actor_id(), origen)
        form, restaurantes = preparar_formulario(datos, detalle["reserva"].cliente_id)
        return mostrar_formulario(form, restaurantes, repetida=True, origen_repeticion=origen)
    form, restaurantes = preparar_formulario()
    return mostrar_formulario(form, restaurantes)


@web.post("/reservas")
@login_required
def crear_reserva():
    form, restaurantes = preparar_formulario()
    if form.validate_on_submit():
        try:
            hora = time.fromisoformat(form.hora.data)
            zona = ZoneInfo(current_app.config["TIMEZONE"])
            inicio = datetime.combine(form.fecha.data, hora, zona).astimezone(UTC)
            datos = DatosReserva(
                form.restaurante_id.data, inicio, form.personas.data, form.observaciones.data or ""
            )
            reserva = servicio().crear_reserva(
                actor_id(),
                datos,
                form.token_operacion.data,
                form.cliente_id.data if es_admin() else None,
            )
            flash(
                "Tu reserva está confirmada."
                if not es_admin()
                else "Reserva confirmada para el cliente.",
                "success",
            )
            return redirect(url_for("web.detalle_reserva", reserva_id=reserva.id))
        except ValueError:
            form.hora.errors = ["Selecciona una hora válida."]
        except ErrorAplicacion as error:
            if error.codigo_http in (403, 404):
                raise
            agregar_error(form, error)
            return mostrar_formulario(form, restaurantes, error.codigo_http)
    return mostrar_formulario(form, restaurantes, 422)


@web.get("/reservas")
@login_required
def reservas():
    restaurante_id = entero(request.args.get("restaurante_id"))
    fecha = fecha_valida(request.args.get("fecha"))
    estado = request.args.get("estado") or None
    lista = servicio().listar_reservas(actor_id(), restaurante_id, fecha, estado)
    opciones = servicio("catalogos").restaurantes(actor_id())
    return render_template(
        "reservas.html",
        lista=lista,
        restaurantes=opciones,
        filtro_restaurante=restaurante_id,
        filtro_fecha=fecha,
        filtro_estado=estado,
    )


@web.get("/reservas/<int:reserva_id>")
@login_required
def detalle_reserva(reserva_id):
    return render_template(
        "reserva_detalle.html", **servicio().obtener_detalle(actor_id(), reserva_id)
    )


@web.post("/reservas/<int:reserva_id>/cancelar")
@login_required
def cancelar_reserva(reserva_id):
    servicio().cancelar_reserva(actor_id(), reserva_id)
    flash("Reserva cancelada. La mesa vuelve a estar disponible.", "success")
    return redirect(url_for("web.detalle_reserva", reserva_id=reserva_id))


@web.get("/reservas/<int:reserva_id>/repetir")
@login_required
def repetir_reserva(reserva_id):
    datos = servicio().preparar_repeticion(actor_id(), reserva_id)
    detalle = servicio().obtener_detalle(actor_id(), reserva_id)
    form, restaurantes = preparar_formulario(datos, detalle["reserva"].cliente_id)
    return mostrar_formulario(form, restaurantes, repetida=True, origen_repeticion=reserva_id)


def contexto_admin(form):
    restaurantes = servicio("catalogos").restaurantes(actor_id())
    form.restaurante_id.choices = [(r.id, r.nombre) for r in restaurantes]
    if request.method == "GET":
        form.restaurante_id.data = entero(
            request.args.get("restaurante_id"), restaurantes[0].id if restaurantes else None
        )
    restaurante_id = form.restaurante_id.data
    if not restaurante_id:
        raise Validacion("No tienes restaurantes disponibles para configurar.")
    datos = servicio("catalogos").configuracion(actor_id(), restaurante_id)
    return restaurantes, datos


@web.route("/admin/mesas", methods=["GET", "POST"])
@login_required
def mesas():
    form = MesaForm()
    restaurantes, datos = contexto_admin(form)
    codigo = 200
    editar_id = entero(request.args.get("editar")) if request.method == "GET" else None
    if editar_id:
        mesa = next((m for m in datos["mesas"] if m.id == editar_id), None)
        if not mesa:
            raise Validacion("La mesa seleccionada no pertenece a este restaurante.")
        form.id.data, form.numero.data = str(mesa.id), mesa.numero
        form.capacidad.data, form.activa.data = mesa.capacidad, mesa.activa
    if form.validate_on_submit():
        try:
            mesa = Mesa(
                entero(form.id.data),
                form.restaurante_id.data,
                form.numero.data.strip(),
                form.capacidad.data,
                form.activa.data,
            )
            servicio("configuracion").guardar_mesa(actor_id(), mesa)
            flash("La configuración de la mesa se guardó.", "success")
            return redirect(url_for("web.mesas", restaurante_id=mesa.restaurante_id))
        except ErrorAplicacion as error:
            if error.codigo_http in (403, 404):
                raise
            agregar_error(form, error)
            codigo = error.codigo_http
    elif request.method == "POST":
        codigo = 422
    return render_template("mesas.html", form=form, restaurantes=restaurantes, **datos), codigo


@web.route("/admin/horarios", methods=["GET", "POST"])
@login_required
def horarios():
    form = HorarioForm()
    restaurantes, datos = contexto_admin(form)
    codigo = 200
    editar_id = entero(request.args.get("editar")) if request.method == "GET" else None
    if editar_id:
        horario = next((h for h in datos["horarios"] if h.id == editar_id), None)
        if not horario:
            raise Validacion("La franja seleccionada no pertenece a este restaurante.")
        form.id.data = str(horario.id)
        form.dia_semana.data = horario.dia_semana
        form.apertura.data, form.cierre.data = horario.apertura, horario.cierre
    if request.method == "POST" and request.form.get("accion") == "eliminar":
        servicio("configuracion").eliminar_horario(
            actor_id(), form.restaurante_id.data, entero(request.form.get("eliminar_id"))
        )
        flash("La franja fue eliminada.", "success")
        return redirect(url_for("web.horarios", restaurante_id=form.restaurante_id.data))
    if form.validate_on_submit():
        try:
            horario = HorarioAtencion(
                entero(form.id.data),
                form.restaurante_id.data,
                form.dia_semana.data,
                form.apertura.data,
                form.cierre.data,
            )
            servicio("configuracion").guardar_horario(actor_id(), horario)
            flash("El horario de atención se guardó.", "success")
            return redirect(url_for("web.horarios", restaurante_id=horario.restaurante_id))
        except ErrorAplicacion as error:
            if error.codigo_http in (403, 404):
                raise
            agregar_error(form, error)
            codigo = error.codigo_http
    elif request.method == "POST":
        codigo = 422
    return render_template("horarios.html", form=form, restaurantes=restaurantes, **datos), codigo
