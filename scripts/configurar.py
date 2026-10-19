#Genera secretos locales sin sobrescribir una configuración existente.
import os
import secrets
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
ruta = raiz / ".env"
try:
    fd = os.open(ruta, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
except FileExistsError:
    print("Ya existe .env. Se conserva sin cambios.")
else:
    with os.fdopen(fd, "w", encoding="utf-8") as archivo:
        archivo.write(f"SECRET_KEY={secrets.token_hex(32)}\n")
        archivo.write(f"DEMO_PASSWORD={secrets.token_urlsafe(18)}\n")
        archivo.write("COOKIE_SECURE=0\nRESERVA_DURACION_MINUTOS=90\n")
    print("Configuración local creada. Consulta DEMO_PASSWORD en .env para iniciar sesión.")
