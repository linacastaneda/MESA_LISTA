# Despliegue de MesaLista

## Destino correcto

Flask debe ejecutarse en un servidor Python. SQLite necesita un archivo persistente accesible desde ese servidor. GitHub Pages solo entrega recursos estáticos: puede alojar la presentación de `site/`, pero no los casos de uso de la aplicación.

El repositorio está preparado para publicar, pero todavía no está enlazado a una cuenta o URL real. No se han contratado servicios ni creado recursos de pago.

## Opción A: servidor Linux propio o de la universidad

1. Clona el repositorio en una carpeta propiedad del usuario de servicio.
2. Crea `.venv`, instala `requirements.txt` y genera una clave de sesión con `scripts/configurar.py`.
3. Configura `DATABASE_PATH` en una carpeta persistente con permisos de lectura/escritura para ese usuario.
4. Ejecuta explícitamente `flask --app run.py init-db` y, para la demostración, `flask --app run.py seed-demo`.
5. Sirve la aplicación mediante:

```bash
source .venv/bin/activate
gunicorn 'reservas:create_app()' --bind 127.0.0.1:8000 --workers 1 --threads 4 --timeout 30
```

6. Configura el proxy HTTPS del servidor hacia `127.0.0.1:8000` y establece `COOKIE_SECURE=1` para el acceso público HTTPS. No expongas el depurador.
7. Usa el supervisor de procesos del servidor para reiniciar Gunicorn cuando sea necesario. Conserva las variables de entorno y el archivo SQLite entre despliegues.

El programa no requiere confiar en cabeceras de proxy para construir URLs absolutas. No se añade `ProxyFix` sin una topología de proxy verificada. Las redirecciones de la aplicación son internas.

## Opción B: Render con disco persistente

**Esta opción es de pago.** La documentación vigente de Render exige un servicio de pago para un disco persistente. Los archivos de un servicio sin disco son efímeros; alojar allí SQLite perdería datos al reiniciar o desplegar.

1. Sube el proyecto a GitHub.
2. En Render, crea un Blueprint conectado al repositorio e indica la ruta `deploy/render.yaml`. Revisa el costo del plan y del disco antes de crear los recursos.
3. El Blueprint configura Python 3.13, Gunicorn, una única instancia, cuatro hilos y un disco de 1 GB montado en `/var/data`.
4. `DATABASE_PATH` apunta a `/var/data/reservas.sqlite3`. `SECRET_KEY` se genera en Render. `COOKIE_SECURE=1` corresponde al acceso HTTPS.
5. Introduce un valor privado para `DEMO_PASSWORD` de al menos 12 caracteres cuando se solicite. No lo publiques en GitHub.
6. El arranque ejecuta explícitamente `init-db`, que conserva las tablas y filas existentes. No crea cuentas de demostración automáticamente.
7. Una vez iniciado el servicio, abre su Shell y ejecuta:

```bash
flask --app run.py seed-demo
```

8. Entra con los correos del README y la contraseña elegida. El endpoint `/health` verifica acceso a la base inicializada.
9. Copia la URL HTTPS real del servicio a `site/config.js` si deseas enlazarla desde Pages.

Solo se preservan archivos bajo `/var/data`. No cambies la ruta de SQLite a una carpeta efímera. Mantén una instancia: un disco local no crea una base compartida entre múltiples servidores. Los identificadores de planes de alojamiento pueden cambiar; valida el Blueprint en el panel al publicarlo.

No se ejecutó un despliegue externo como parte de la validación local. El archivo es una configuración preparada, no evidencia de publicación.

## GitHub Pages: presentación opcional

`site/index.html` explica el proyecto. `site/config.js` contiene `window.MESALISTA_APP_URL`, inicialmente vacía. Al configurarla con una URL HTTPS, aparece el botón para abrir Flask. No hay autenticación ni almacenamiento de reservas en esa página.

En el repositorio selecciona **Settings → Pages → Source → GitHub Actions** y ejecuta manualmente el workflow **Publicar presentacion en Pages** desde `main`. El artefacto publicado solo contiene `site/`; no expone la base ni `.env`.

## Respaldo y restauración

Con el entorno virtual activo:

```bash
python scripts/respaldo.py instance/respaldo-antes-de-cambio.sqlite3
```

En Render, elige un destino bajo `/var/data` y conserva también copias externas al proveedor. El script usa `Connection.backup`; no copia un archivo SQLite de forma insegura mientras se escribe.

Para restaurar: detén todos los procesos que usan la base, conserva una copia de la base actual, coloca la copia validada en `DATABASE_PATH`, corrige permisos y reinicia. Comprueba login, historial y `/health` antes de reabrir el acceso.

## Fuentes oficiales consultadas

- [GitHub Pages: limitaciones de lenguajes de servidor](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site).
- [GitHub Pages con workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
- [Gunicorn para Flask](https://flask.palletsprojects.com/en/stable/deploying/gunicorn/).
- [Flask en Render](https://render.com/docs/deploy-flask).
- [Discos persistentes de Render](https://render.com/docs/disks).
- [Referencia de Blueprints](https://render.com/docs/blueprint-spec).
