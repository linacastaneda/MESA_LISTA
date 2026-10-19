#Copia coherente de SQLite mediante su API de backup, incluso con el servidor activo.

import argparse
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv


def main():
    raiz = Path(__file__).resolve().parent.parent
    load_dotenv(raiz / ".env")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destino", type=Path)
    args = parser.parse_args()
    origen = Path(
        os.environ.get("DATABASE_PATH", str(raiz / "instance" / "reservas.sqlite3"))
    ).resolve()
    destino = args.destino.resolve()
    if origen == destino or destino.exists():
        parser.error("El destino debe ser un archivo nuevo diferente de la base original.")
    destino.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(destino, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    try:
        with sqlite3.connect(origen.as_uri() + "?mode=ro", uri=True) as fuente:
            with sqlite3.connect(destino) as copia:
                fuente.backup(copia)
    except Exception:
        destino.unlink(missing_ok=True)
        raise
    print(f"Respaldo creado: {destino}")


if __name__ == "__main__":
    main()
