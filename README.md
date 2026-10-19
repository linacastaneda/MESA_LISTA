# MesaLista — Reservas de restaurantes

Sistema web desarrollado con **Python, Flask y SQLite**, organizado con **Modelo–Vista–Controlador (MVC)**, capa de servicios y persistencia DAO.

## Organización

```text
reservas/
├── modelo/           # Entidades, una clase por archivo, y errores_clases/
├── vista/
│   ├── templates/    # Plantillas HTML (Jinja2)
│   └── static/       # CSS, JavaScript e imágenes
├── controlador/      # Rutas Flask y forms/ (un formulario por archivo)
├── aplicacion/       # Servicios, lógica de negocio y puertos DAO
├── infraestructura/  # dao/ (cada DAO por archivo), transacciones y esquema SQLite
├── patrones/         # Builder, Prototype, Facade y Adapter
└── __init__.py       # create_app: inicialización de Flask
tests/                 # Pruebas automatizadas
scripts/               # Configuración y respaldo
run.py                 # Inicio de la aplicación
```

Las clases de dominio, los contratos DAO, los DAO SQLite, los formularios y los participantes del patrón Builder están separados en archivos Python individuales. Los módulos `entidades.py`, `errores.py`, `contratos.py`, `dao_sqlite.py`, `formularios.py` y `builder.py` mantienen importaciones públicas compatibles con el resto de la aplicación.

## Patrones implementados

| Patrón | Tipo | Uso |
|---|---|---|
| Builder | Creacional | `reservas/patrones/constructores/`: construcción de una reserva válida |
| Prototype | Creacional | `DatosReserva.clonar()` y `reservas/patrones/prototype.py`: repetición de datos |
| Facade | Estructural | `reservas/patrones/facade.py`: coordinación de operaciones |
| Adapter | Estructural | `reservas/patrones/adapter.py`: adaptación de Usuario a Flask-Login |

## Instalación en Windows (PowerShell)

Se recomienda Python 3.11 o posterior.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pip install tzdata
python scripts/configurar.py
# Antes de seed-demo, ajusta DEMO_PASSWORD en .env como se indica abajo
python -m flask --app run.py init-db
python -m flask --app run.py seed-demo
python run.py
```

Abre **http://127.0.0.1:5000**. Para siguientes ejecuciones, activa `.venv` y ejecuta `python run.py`.

En Linux, activa el entorno con `source .venv/bin/activate`. El paquete `tzdata` es especialmente importante para la zona horaria `America/Bogota` en Windows.

## Acceso para evaluación académica

Para que el profesor pueda **iniciar sesión en MesaLista**, se incluyen las siguientes credenciales de demostración. **Son exclusivamente para el proyecto académico; no deben reutilizarse en sistemas reales.**

| Cuenta | Rol | Contraseña de demostración |
|---|---|---|
| `cliente@demo.local` | Cliente | `gqmDOmA63RK7rmNr2huhc7tx` |
| `cliente2@demo.local` | Cliente | `gqmDOmA63RK7rmNr2huhc7tx` |
| `admin@demo.local` | Administrador de La Mesa | `gqmDOmA63RK7rmNr2huhc7tx` |
| `admin2@demo.local` | Administrador de Patio Verde | `gqmDOmA63RK7rmNr2huhc7tx` |

**Configuración necesaria para que estas credenciales funcionen:** ejecuta `python scripts/configurar.py` para crear el archivo local `.env`. El script genera `SECRET_KEY` y una contraseña aleatoria. **Antes de ejecutar `seed-demo` por primera vez**, abre el archivo `.env` y reemplaza únicamente su línea `DEMO_PASSWORD` por:

```dotenv
DEMO_PASSWORD=gqmDOmA63RK7rmNr2huhc7tx
```

**Deja la `SECRET_KEY` generada automáticamente**, sin publicarla. Luego ejecuta `python -m flask --app run.py init-db`, `python -m flask --app run.py seed-demo` y `python run.py`. Abre `http://127.0.0.1:5000` para iniciar sesión.

Si ya se crearon las cuentas con otra `DEMO_PASSWORD`, cambiar solo el archivo `.env` **no actualiza** las contraseñas almacenadas: deberás seguir un procedimiento de restablecimiento o preparar una base de demostración nueva.

## Funcionalidades

- Autenticación de clientes y administradores.
- Búsqueda de restaurantes, consulta de horarios y reservas con asignación automática de mesa.
- Historial, cancelación y repetición de datos de reserva.
- Gestión autorizada de mesas y horarios de los restaurantes.
- Persistencia SQLite mediante DAO y transacciones que impiden reservas incompatibles.

## Pruebas

Instala `requirements-dev.txt` y ejecuta:

```powershell
python -m pytest -q
```

Las pruebas utilizan bases temporales. El proyecto original registró 61 pruebas aprobadas; vuelve a ejecutar la suite para comprobar tu instalación.

## Seguridad

No publiques `.env`, bases SQLite locales ni el entorno virtual `.venv`. Estos archivos están excluidos mediante `.gitignore`. Las credenciales se almacenan con hash y las consultas SQL usan parámetros.
