"""Punto de composición. create_app configura dependencias; no se cuenta como patrón GoF."""

import os
from datetime import timedelta
from pathlib import Path

import click
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFError, CSRFProtect

from reservas.aplicacion.acceso import ServicioAcceso
from reservas.aplicacion.autenticacion import ServicioAutenticacion
from reservas.aplicacion.catalogos import ServicioCatalogos
from reservas.aplicacion.configuracion import ServicioConfiguracion
from reservas.aplicacion.disponibilidad import ServicioDisponibilidad, reloj_utc
from reservas.aplicacion.facade import ReservaFacade
from reservas.aplicacion.reservas import ServicioReserva
from reservas.modelo.errores import ErrorAplicacion
from reservas.infraestructura.inicializacion import CUENTAS_DEMO, cargar_demo, inicializar
from reservas.infraestructura.unidad_trabajo import UnidadTrabajoSqlite


def create_app(config=None):
    raiz = Path(__file__).resolve().parent.parent
    load_dotenv(raiz / ".env")
    app = Flask(
        __name__,
        template_folder="vista/templates",
        static_folder="vista/static",
        instance_path=str(raiz / "instance"),
    )
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        DATABASE=os.environ.get("DATABASE_PATH", str(raiz / "instance" / "reservas.sqlite3")),
        RESERVA_DURACION_MINUTOS=int(os.environ.get("RESERVA_DURACION_MINUTOS", "90")),
        TIMEZONE="America/Bogota",
        SQLITE_TIMEOUT=5.0,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        WTF_CSRF_TIME_LIMIT=7200,
        MAX_CONTENT_LENGTH=64 * 1024,
        RELOJ=reloj_utc,
    )
    if config:
        app.config.update(config)
    if not app.config["SECRET_KEY"] or len(app.config["SECRET_KEY"]) < 32:
        raise RuntimeError(
            "Configura SECRET_KEY con al menos 32 caracteres. "
            "Para uso local ejecuta: python scripts/configurar.py"
        )
    app.config["DATABASE"] = str(Path(app.config["DATABASE"]).resolve())

    def crear_uow():
        return UnidadTrabajoSqlite(app.config["DATABASE"], app.config["SQLITE_TIMEOUT"])

    acceso = ServicioAcceso()
    disponibilidad = ServicioDisponibilidad(
        app.config["RESERVA_DURACION_MINUTOS"], app.config["TIMEZONE"]
    )
    reloj = app.config["RELOJ"]
    servicio = ServicioReserva(crear_uow, acceso, disponibilidad, reloj)
    app.extensions["reservas"] = ReservaFacade(crear_uow, acceso, disponibilidad, servicio, reloj)
    app.extensions["catalogos"] = ServicioCatalogos(crear_uow, acceso)
    app.extensions["configuracion"] = ServicioConfiguracion(
        crear_uow, acceso, disponibilidad, reloj
    )
    autenticacion = ServicioAutenticacion(crear_uow)
    app.extensions["autenticacion"] = autenticacion
    app.extensions["crear_uow"] = crear_uow
    CSRFProtect(app)
    login = LoginManager(app)
    login.login_view = "web.login"
    login.login_message = "Inicia sesión para continuar."
    login.login_message_category = "info"
    login.user_loader(autenticacion.cargar_sesion)
    from reservas.controlador.rutas import web

    app.register_blueprint(web)

    @app.template_filter("local")
    def local(valor, formato="%d/%m/%Y · %H:%M"):
        return valor.astimezone(disponibilidad.zona).strftime(formato)

    @app.context_processor
    def contexto():
        return {
            "ahora": reloj(),
            "duracion": app.config["RESERVA_DURACION_MINUTOS"],
            "dias": ["", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
        }

    @app.errorhandler(ErrorAplicacion)
    def error_dominio(error):
        return render_template(
            "error.html", codigo=error.codigo_http, mensaje=error.mensaje
        ), error.codigo_http

    @app.errorhandler(CSRFError)
    def error_csrf(error):
        return render_template(
            "error.html",
            codigo=400,
            mensaje="El formulario venció o su token no es válido. "
            "Vuelve a abrir la página antes de enviar.",
        ), 400

    @app.errorhandler(404)
    def no_encontrado(error):
        return render_template("error.html", codigo=404, mensaje="No encontramos esa página."), 404

    @app.errorhandler(500)
    def error_interno(error):
        return render_template(
            "error.html",
            codigo=500,
            mensaje="No pudimos completar la operación. Inténtalo nuevamente.",
        ), 500

    @app.after_request
    def cabeceras(respuesta):
        respuesta.headers["X-Content-Type-Options"] = "nosniff"
        respuesta.headers["X-Frame-Options"] = "DENY"
        respuesta.headers["Referrer-Policy"] = "same-origin"
        respuesta.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; "
            "font-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        )
        if not respuesta.headers.get("Cache-Control") or respuesta.mimetype == "text/html":
            respuesta.headers["Cache-Control"] = "no-store"
        if app.config["SESSION_COOKIE_SECURE"]:
            respuesta.headers["Strict-Transport-Security"] = "max-age=31536000"
        return respuesta

    @app.cli.command("init-db")
    def init_db():
        """Crea tablas e índices ausentes; conserva datos existentes."""
        inicializar(app.config["DATABASE"])
        click.echo("Base preparada. Los datos existentes se conservaron.")

    @app.cli.command("seed-demo")
    def seed_demo():
        """Carga cuentas ficticias solo en una base vacía."""
        clave = os.environ.get("DEMO_PASSWORD") or click.prompt(
            "Contraseña para las cuatro cuentas de demostración (mínimo 12 caracteres)",
            hide_input=True,
            confirmation_prompt=True,
        )
        try:
            cargar_demo(app.config["DATABASE"], clave)
        except ErrorAplicacion as exc:
            raise click.ClickException(exc.mensaje) from exc
        click.echo("Datos de demostración cargados. Contraseña: el valor de DEMO_PASSWORD en .env.")
        for _, nombre, correo, rol in CUENTAS_DEMO:
            click.echo(f"{correo} — {nombre} — {rol}")

    return app
