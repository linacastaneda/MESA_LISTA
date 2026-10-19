# Evidencias para el informe y el video

## Imágenes incluidas

Las imágenes 01–11 son capturas reales del navegador con datos ficticios. Las imágenes 12–20 son **extractos renderizados de los archivos fuente entregados**, con ruta y números de línea; no se presentan como capturas de Sublime. Pueden sustituirse por pantallazos del editor al preparar el informe.

| Archivo en `capturas/` | Contenido |
| --- | --- |
| `01_login.png` | Pantalla de inicio de sesión |
| `02_restaurantes.png` | Catálogo y búsqueda |
| `03_formulario_reserva.png` | Consulta de horarios y formulario de confirmación |
| `04_reserva_confirmada.png` | Reserva persistida y mesa asignada |
| `05_repetir_reserva.png` | Datos copiados y confirmación nueva |
| `06_reserva_cancelada.png` | Cambio de estado con historial conservado |
| `07_reservas_administrador.png` | Listado autorizado del administrador |
| `08_mesas.png` | Gestión de mesas |
| `09_horarios.png` | Franjas de atención |
| `10_movil.png` | Catálogo a 390 px de ancho |
| `11_formulario_movil.png` | Formulario adaptable a móvil |
| `12_transaccion_reserva.png` | Servicio, autorización, token, disponibilidad, Builder y commit |
| `13_director_builder.png` | Orden explícito de construcción |
| `14_builder_producto.png` | Validación y creación del producto |
| `15_prototype.png` | Prototipo concreto y clonación |
| `16_facade_copia.png` | Uso de Prototype desde la fachada |
| `17_adapter.png` | Contrato de sesión por composición |
| `18_unidad_trabajo.png` | Conexión compartida, transacción, rollback y errores |
| `19_prueba_concurrencia.png` | P17 con barrera y dos conexiones |
| `20_dao_sqlite.png` | Inserción parametrizada y reconstrucción de entidad |

Para incorporarlas al Google Docs, añadan número de figura, título y nota que explique el comportamiento. No muestren `.env`, contraseñas ni hashes completos en el video. Las capturas de ejecución deben relacionarse con el código explicado.

Los identificadores y fechas de los pantallazos son ejemplos de la ejecución realizada. Una instalación nueva comienza sin reservas y propondrá fechas relativas a su reloj.

## Guion de 8 a 10 minutos

| Tiempo | Qué explicar y mostrar |
| --- | --- |
| 0:00–1:00 | Problema, alcance y roles. Entrar como cliente. |
| 1:00–2:00 | Arquitectura de tres capas y modelo relacional. Explicar mesa/reserva y cliente/creador. |
| 2:00–3:00 | Recorrer `crear_reserva` del controlador a la fachada y al servicio. |
| 3:00–4:00 | Mostrar contrato, director, builder y producto. Crear una reserva real. |
| 4:00–5:00 | Repetir la reserva. Explicar qué clona Prototype y qué no se copia. |
| 5:00–6:00 | Explicar Facade y Adapter. Mostrar el adaptador y cambiar al rol administrador. |
| 6:00–7:00 | Reservar para un cliente y gestionar mesas/horarios. Mostrar rechazo de un cambio incompatible. |
| 7:00–8:00 | Explicar la transacción y ejecutar `python -m pytest -q -k P17`. |
| 8:00–9:00 | Mostrar resultado global de pruebas y persistencia después de reiniciar. |
| 9:00–10:00 | Resumir decisiones, ejecución en Debian y diferencia entre Pages y servidor Flask. |

Los tiempos son orientativos. La grabación debe usar las clases y resultados de esta entrega, no solo leer los diagramas.

## Pendientes del equipo

1. Incorporar las evidencias elegidas y los resultados al informe APA compartido.
2. Revisar nombres y demás datos académicos de la portada.
3. Grabar el video, subirlo a YouTube con acceso apropiado para el profesor y añadir el enlace real.
4. Si se pide acceso público, crear el repositorio y publicar Flask en un servidor compatible.

**Enlace de YouTube:** pendiente de grabación y publicación.
