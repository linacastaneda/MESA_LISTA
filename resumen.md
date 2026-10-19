# Resumen para el equipo

**MesaLista** convierte el diseño aprobado en un módulo web real de reservas. Se ejecuta con `python run.py` después de instalar dependencias, generar la configuración e inicializar la base según el README.

## Cómo leer el código

Comiencen por `reservas/__init__.py`: conecta los servicios con la persistencia SQLite y registra la web. Después sigan esta ruta de una reserva:

1. `presentacion/rutas.py`, función `crear_reserva`: valida el formulario y traduce fecha y hora a UTC.
2. `aplicacion/facade.py`, método `crear_reserva`: ofrece el caso de uso compartido por los dos roles.
3. `aplicacion/reservas.py`, método `crear`: abre la unidad de trabajo, toma el bloqueo de escritura y revalida actor, cliente y restaurante.
4. El mismo servicio verifica el token de operación. Un reenvío idéntico devuelve la reserva ya existente.
5. `aplicacion/disponibilidad.py` comprueba futuro, franja, duración, paso de 30 minutos, capacidad y ausencia de solapamientos.
6. `patrones/builder.py` construye el objeto `Reserva` completo mediante un director y un constructor concreto.
7. `infraestructura/dao_sqlite.py` inserta con parámetros; `UnidadTrabajoSqlite` confirma toda la operación. Si ocurre un error, revierte.
8. El controlador redirige al detalle. El navegador no decide permisos ni asigna la mesa.

## Los cuatro patrones que hay que sustentar

### Builder — creacional

`ConstructorReserva` declara los pasos. `ReservaBuilder` reúne y valida los valores. `DirectorReserva` fija el orden. `ContextoReserva` transporta información previamente autorizada. El producto es `Reserva`.

No se usa únicamente como nombre de una función: hay contrato, director, constructor y producto. El builder no consulta SQL. Se crea uno por operación y se reinicia para no mezclar datos. Pruebas P25–P26.

### Prototype — creacional

`DatosReserva` implementa `Prototipo.clonar()`. Contiene restaurante, inicio, personas y observaciones. Al pulsar **Volver a reservar**, la fachada obtiene una copia independiente que precarga el formulario.

No se copian el ID, la mesa, el estado, el creador ni el token de la reserva original. La confirmación vuelve a pasar por disponibilidad y Builder. Pruebas P27–P28.

### Facade — estructural

`ReservaFacade` ofrece una interfaz para consultar disponibilidad, crear, listar, cancelar, obtener detalles y preparar una repetición. Coordina los servicios; no contiene SQL ni plantillas.

Las autorizaciones definitivas permanecen en el servicio que abre la transacción. Así, invocarlo directamente tampoco permite saltarse los permisos. Prueba P29 y pruebas HTTP de ambos roles.

### Adapter — estructural

Flask-Login espera `get_id`, `is_active`, `is_authenticated` e `is_anonymous`. Nuestra entidad `Usuario` no conoce esos miembros. `UsuarioSesionAdapter` la contiene y ofrece la interfaz que necesita la biblioteca.

`ServicioAutenticacion` verifica el hash antes de crear una sesión. La recarga de sesión vuelve a comprobar si la cuenta sigue activa. El adaptador no asigna roles ni da acceso a restaurantes. Prueba P30.

## Capas, DAO y base relacional

La presentación conoce los casos de uso. La aplicación conoce contratos DAO y de unidad de trabajo. Las implementaciones SQLite cumplen esos contratos. El dominio conserva las invariantes sin importar Flask ni SQLite.

Existen seis tablas: `usuario`, `restaurante`, `administrador_restaurante`, `mesa`, `horario_atencion` y `reserva`. El restaurante de una reserva se obtiene por su mesa. `DatosReserva` es un objeto de dominio, no una tabla. Cliente y creador son referencias diferentes porque un administrador puede reservar para otro usuario.

La unidad de trabajo es la dueña de la conexión y del commit. Todos sus DAO usan la misma conexión. La regla más importante es que la transacción comienza **antes de comprobar la disponibilidad definitiva**, y los triggers sirven como una defensa adicional.

## Qué mostrar al profesor

Muestren login de ambos roles, creación, cancelación, repetición y administración. Luego sigan una reserva desde el controlador hasta el DAO. Ubiquen los participantes de cada patrón y expliquen una prueba que demuestra su comportamiento.

`tests/test_casos_documento.py` conserva los identificadores P01–P30. `docs/pruebas.md` relaciona cada requisito con su código y resultado. `docs/diagramas.md` se renderiza directamente en GitHub.

## Publicación

El código y la documentación pueden ir a GitHub. La aplicación completa requiere un servidor Python con disco persistente. GitHub Pages puede alojar `site/`, que presenta el proyecto y enlaza al servidor cuando se configure su URL. Las instrucciones están en el README y `docs/despliegue.md`.
