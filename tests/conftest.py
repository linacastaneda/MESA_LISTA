import re
import shutil
from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe

import pytest

from reservas import create_app
from reservas.dominio.entidades import DatosReserva
from reservas.infraestructura.inicializacion import cargar_demo, inicializar

CLAVE = "ClaveSoloParaPruebas-2026!"

class RelojFijo:
    def __init__(self):
        self.ahora = datetime(2030, 1, 7, 13, tzinfo=UTC)

    def __call__(self):
        return self.ahora


@pytest.fixture(scope="session")
def base_semilla(tmp_path_factory):
    ruta = tmp_path_factory.mktemp("semilla") / "semilla.sqlite3"
    inicializar(ruta)
    cargar_demo(ruta, CLAVE)
    return ruta


@pytest.fixture
def app(tmp_path, base_semilla):
    ruta = tmp_path / "prueba.sqlite3"
    shutil.copy2(base_semilla, ruta)
    reloj = RelojFijo()
    return create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "s" * 64,
            "DATABASE": str(ruta),
            "RELOJ": reloj,
            "WTF_CSRF_ENABLED": True,
        }
    )


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def facade(app):
    return app.extensions["reservas"]


@pytest.fixture
def uow(app):
    return app.extensions["crear_uow"]


@pytest.fixture
def datos(app):
    def crear(personas=2, restaurante_id=1, inicio=None, observaciones=""):
        return DatosReserva(
            restaurante_id,
            inicio or app.config["RELOJ"]() + timedelta(days=1, hours=4),
            personas,
            observaciones,
        )

    return crear


@pytest.fixture
def token():
    return token_urlsafe(32)


def campo_oculto(response, nombre):
    html = response.get_data(as_text=True)
    patron = rf'<input[^>]*name="{nombre}"[^>]*value="([^"]*)"'
    resultado = re.search(patron, html)
    assert resultado, f"No se encontró {nombre} en el formulario"
    return resultado.group(1)


def entrar(client, correo="cliente@demo.local", clave=CLAVE, next_url=""):
    pagina = client.get("/login" + next_url)
    return client.post(
        "/login" + next_url,
        data={"correo": correo, "clave": clave, "csrf_token": campo_oculto(pagina, "csrf_token")},
    )


def formulario_reserva(client, datos, cliente_id=None):
    from zoneinfo import ZoneInfo

    local = datos.inicio.astimezone(ZoneInfo("America/Bogota"))
    pagina = client.get(
        "/reservas/nueva",
        query_string={
            "restaurante_id": datos.restaurante_id,
            "fecha": local.date().isoformat(),
            "personas": datos.personas,
        },
    )
    valores = {
        "restaurante_id": datos.restaurante_id,
        "fecha": local.date().isoformat(),
        "personas": datos.personas,
        "hora": local.strftime("%H:%M"),
        "observaciones": datos.observaciones,
        "csrf_token": campo_oculto(pagina, "csrf_token"),
        "token_operacion": campo_oculto(pagina, "token_operacion"),
    }
    if cliente_id:
        valores["cliente_id"] = cliente_id
    return valores
