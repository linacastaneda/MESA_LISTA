# Correspondencia entre el diseño y la implementación

El documento rector es el Google Docs enlazado en el README. `diseno_aprobado.md` conserva la lectura textual usada al comenzar; el Google Docs contiene los diagramas originales. Las fuentes actualizadas del código están en `diagramas.md`.

| Decisión | Implementación y motivo |
| --- | --- |
| Tres capas y MVC en presentación | Flask/Jinja en `presentacion`; casos de uso y contratos en `aplicacion`; DAO/UoW en `infraestructura`; entidades independientes en `dominio`. |
| Dos creacionales y dos estructurales | Builder, Prototype, Facade y Adapter con participantes explícitos y uso real. No se cuentan funcionalidades automáticas del framework. |
| SQL directo y DAO | `sqlite3` y parámetros SQL; los servicios no construyen consultas. Los filtros de nombre y ciudad se comparan con `casefold` tras leer restaurantes activos para tratar letras españolas sin concatenar SQL. Es suficiente para el catálogo académico. |
| Persistencia e integridad | Seis tablas, claves foráneas habilitadas por conexión, restricciones, índices y triggers contra solapamiento. |
| Concurrencia | `BEGIN IMMEDIATE` antes de autorización definitiva y consulta de token/cupo. UoW traduce conflictos y bloqueos. Prueba P17 real con dos conexiones. |
| Duración e historia | 90 minutos configurables; `fin` queda guardado. Las etiquetas temporales de la vista no agregan estados persistentes. |
| Copia segura | `DatosReserva.clonar`; los GET de repetición no insertan. Si se cambia la fecha de una copia histórica, se vuelve a autorizar el origen y se conservan sus observaciones y cliente. |
| Administración | `ServicioConfiguracion` comprueba la configuración propuesta contra reservas confirmadas no finalizadas. Desactivar usa `MesaDAO.guardar(activa=False)`. |
| Catálogos y listados | `ServicioCatalogos` consulta opciones autorizadas. La fachada retorna detalles compuestos para que los controladores no accedan a SQL. Son clases auxiliares que concretan el diseño. |
| Credenciales iniciales | `configurar.py` genera secretos locales; `seed-demo` usa una contraseña configurable y hashes independientes. No se distribuye una contraseña de producción. |
| Inicialización | `create_app` no inicializa ni siembra la base. El operador ejecuta `init-db` y `seed-demo`. En el despliegue opcional, `servir.sh` declara una llamada idempotente a `init-db`; nunca borra ni vuelve a sembrar. |
| Horarios y formulario | Un formulario GET consulta fecha/grupo y otro POST confirma hora y detalles. No hay tokens CSRF ni contraseñas en parámetros de consulta. |
| GitHub Pages | Su alojamiento estático no ejecuta Flask. `site/` es una presentación opcional y enlaza al servidor real. El código funcional conserva Flask y SQLite. |
| Datos de demostración | Dos restaurantes, dos administradores y dos clientes. La base inicial no tiene reservas vencidas; las pruebas usan un reloj inyectado y la interfaz propone mañana. |
| Inicialización de IDs | Los IDs de los catálogos de demostración son explícitos para documentar permisos; SQLite asigna IDs de nuevas mesas, franjas y reservas. |
| Fuente del programa | `run.py` inicia el servidor local. No se compila como Java: Python interpreta el código dentro del entorno virtual. |

## Límites conscientes

El diseño cubre el parcial. SQLite dispone de un escritor simultáneo; se mantiene una instancia de aplicación y transacciones cortas. No se incluyen festivos, excepciones por fecha, multi-moneda ni disponibilidad distribuida entre servidores. No hay interfaz para asignar roles o registrar nuevas cuentas, conforme al alcance.

El README y las evidencias reflejan pruebas ejecutadas localmente. La publicación externa y el video no se declaran realizados.
