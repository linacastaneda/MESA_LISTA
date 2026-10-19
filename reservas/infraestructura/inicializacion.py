#Inicialización explícita, repetible y sin borrado de datos.

import sqlite3
from pathlib import Path

from werkzeug.security import generate_password_hash

from reservas.dominio.errores import Conflicto, Validacion
from reservas.infraestructura.unidad_trabajo import UnidadTrabajoSqlite

CUENTAS_DEMO = [
    (1, "Ana Torres", "cliente@demo.local", "CLIENTE"),
    (2, "Diego Ruiz", "cliente2@demo.local", "CLIENTE"),
    (3, "Camila Ortiz", "admin@demo.local", "ADMINISTRADOR"),
    (4, "Mateo Silva", "admin2@demo.local", "ADMINISTRADOR"),
]


def inicializar(ruta):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(ruta) as conexion:
        version = conexion.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, 1):
            raise Conflicto("Versión de base incompatible. Conserva una copia antes de migrar.")
        conexion.executescript(Path(__file__).with_name("schema.sql").read_text(encoding="utf-8"))


def cargar_demo(ruta, clave):
    if len(clave) < 12:
        raise Validacion("La clave de demostración debe tener al menos 12 caracteres.")
    # Los hashes se calculan fuera de la transacción para mantenerla corta.
    usuarios = [
        (id, nombre, correo, generate_password_hash(clave), rol)
        for id, nombre, correo, rol in CUENTAS_DEMO
    ]
    with UnidadTrabajoSqlite(ruta) as u:
        u.iniciar_escritura()
        if u.conexion.execute("SELECT COUNT(*) FROM usuario").fetchone()[0]:
            raise Conflicto("La base ya contiene usuarios. No se sobrescribieron los datos.")
        u.conexion.executemany(
            "INSERT INTO usuario(id,nombre,correo,hash_clave,rol) VALUES(?,?,?,?,?)", usuarios
        )
        u.conexion.executemany(
            "INSERT INTO restaurante(id,nombre,ciudad,direccion) VALUES(?,?,?,?)",
            [
                (1, "La Mesa", "Bogotá", "Calle 70 # 9-24"),
                (2, "Patio Verde", "Medellín", "Carrera 43 # 12-18"),
            ],
        )
        u.conexion.executemany(
            "INSERT INTO administrador_restaurante VALUES(?,?)", [(3, 1), (4, 2)]
        )
        for restaurante in (1, 2):
            for numero, capacidad in enumerate((2, 2, 4, 4, 6, 8, 12), 1):
                u.conexion.execute(
                    "INSERT INTO mesa(restaurante_id,numero,capacidad) VALUES(?,?,?)",
                    (restaurante, str(numero), capacidad),
                )
            for dia in range(1, 8):
                for apertura, cierre in [("11:30", "15:30"), ("18:00", "22:30")]:
                    u.conexion.execute(
                        "INSERT INTO horario_atencion(restaurante_id,dia_semana,apertura,cierre) "
                        "VALUES(?,?,?,?)",
                        (restaurante, dia, apertura, cierre),
                    )
        u.confirmar()
