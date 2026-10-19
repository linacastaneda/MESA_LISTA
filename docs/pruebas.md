# Pruebas y trazabilidad

Se ejecutaron **61 casos parametrizados**, sin fallos, en Python **3.12.14** y **3.13.16**. Las versiones instaladas están fijadas en `requirements*.txt`. No se declara una ejecución sobre Debian 13 dentro de este entorno: se verificaron las dos versiones de Python y el README aporta los comandos para Debian.

Los identificadores P01–P30 provienen del Google Docs. Una fila del diseño puede dar lugar a varias variantes automatizadas.

| Caso | Comportamiento comprobado | Resultado |
| --- | --- | --- |
| P01 | Login válido de cliente y administrador; redirección por rol | Aprobado |
| P02 | Contraseña incorrecta y cuenta desactivada | Aprobado |
| P03 | Cliente rechaza rutas administrativas | Aprobado |
| P04 | Administrador no consulta ni modifica otro restaurante | Aprobado |
| P05 | Cliente no obtiene detalles de reservas ajenas | Aprobado |
| P06 | Creación y selección de menor capacidad, desempate por ID | Aprobado |
| P07 | Personas cero, negativas, texto y booleano | Aprobado |
| P08 | Inicio pasado o exactamente actual | Aprobado |
| P09 | Cierre, descanso y horario fuera de atención | Aprobado |
| P10 | Grupo mayor que todas las mesas | Aprobado |
| P11 | Solapamiento rechazado sobre la última mesa | Aprobado |
| P12 | Fin e inicio contiguos admitidos | Aprobado |
| P13 | Cancelación futura libera mesa y conserva historial | Aprobado |
| P14 | Cancelación al comenzar rechazada | Aprobado |
| P15 | Desactivación o reducción incompatible de mesa rechazada | Aprobado |
| P16 | Eliminación o reducción incompatible de horario rechazada | Aprobado |
| P17 | Dos conexiones simultáneas por la última mesa; exactamente una reserva | Aprobado |
| P18 | Reenvío idéntico devuelve el mismo ID | Aprobado |
| P19 | Token con otro actor o contenido rechazado sin duplicación | Aprobado |
| P20 | Fallo posterior al INSERT revierte la escritura | Aprobado |
| P21 | Otra instancia de la aplicación recupera el dato persistido | Aprobado |
| P22 | POST sin CSRF o con token falso rechazado | Aprobado |
| P23 | HTML en observaciones se muestra escapado | Aprobado |
| P24 | Unicidad de correo y número de mesa | Aprobado |
| P25 | Builder incompleto e intervalo inválido rechazados | Aprobado |
| P26 | Builder reutilizado no conserva datos de otro producto | Aprobado |
| P27 | Clon independiente y composición protegida | Aprobado |
| P28 | Repetición precargada, token nuevo y cupo revalidado | Aprobado |
| P29 | Fachada coordina la creación desde ambos roles | Aprobado |
| P30 | Adapter traduce ID y estado de actividad | Aprobado |

## Integración adicional

`test_http_integridad.py` verifica:

- Recorrido HTTP de cliente con CSRF: crear, reenvío, detalle, repetir, cancelar y salir.
- Recorrido HTTP de administrador: reservar para otro cliente, crear/editar mesa y crear/eliminar franja.
- Valores de formulario inválidos y conservación del token de operación.
- Identidad del cliente tomada de la sesión, no concedida por campos ajenos a su rol.
- Redirecciones externas y destinos malformados rechazados.
- Sesión de cuenta desactivada invalidada en la siguiente solicitud.
- Franjas superpuestas, cruce de medianoche y permisos de configuración.
- Paso de 30 minutos y restaurante inactivo.
- Triggers reales para INSERT y UPDATE superpuestos y restricción de FK.
- Bloqueo SQLite agotado y reintento posterior con el mismo token.
- Cambio de mesa permitido al finalizar la reserva sin cambiar su estado histórico.
- Inicialización idempotente y negativa a sobrescribir usuarios con la semilla.
- Salud, cabeceras de respuesta y entrada de búsqueda con caracteres de SQL.
- Etiqueta temporal “Finalizada” sin agregar un estado a la base.
- Repetición histórica con nueva fecha y conservación de observaciones y cliente.

## Comprobación visual y de navegador

Se recorrió la aplicación en Chromium con automatización de navegador: login, búsqueda, formulario, confirmación, copia, cancelación, listado administrativo, mesas y horarios. Se revisaron pantallas de **1440 px** y **390 px**. El recorrido no registró errores JavaScript ni respuestas HTTP 5xx. Las capturas reales están en `capturas/`.

El navegador es una herramienta de verificación, no una dependencia necesaria para ejecutar la aplicación. La suite de Python cubre las regresiones funcionales sin requerir Node.

## Relación con requisitos

| Requisitos | Código principal | Evidencia |
| --- | --- | --- |
| RF01–RF02 | `autenticacion.py`, `adapter.py`, `acceso.py`, `rutas.py` | P01–P05, P22 y pruebas de sesión |
| RF03–RF05 | `catalogos.py`, `disponibilidad.py`, `reservas.py`, `builder.py` | P06–P12, P17–P20 |
| RF06–RF08 | `facade.py`, `Reserva.cancelar`, `DatosReserva.clonar` | P05, P13–P14, P27–P28 |
| RF09–RF10 | `configuracion.py`, `Mesa`, `HorarioAtencion` | P15–P16, gestión HTTP de catálogos |
| RF11 | `ServicioReserva.crear` y formulario del administrador | P29 y creación HTTP para cliente |
| RF12 | `schema.sql`, DAO y `UnidadTrabajoSqlite` | P20–P21, inicialización y restricciones |
| Dos creacionales | `builder.py`, `prototype.py`, `DatosReserva` | P25–P28 |
| Dos estructurales | `facade.py`, `adapter.py` | P29–P30 y recorridos HTTP |

## Reproducir

```bash
python -m pytest -q
python -m pytest -q -k P17
ruff check .
ruff format --check .
python -m pip check
```

La evidencia de ejecución automatizada se conserva en `resultado_pytest.txt` y `resultados_junit.xml`. Si se modifica el código, se deben ejecutar nuevamente las pruebas y actualizar los resultados antes de usarlos en el informe.
