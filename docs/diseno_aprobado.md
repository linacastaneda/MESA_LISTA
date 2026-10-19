# Diseño aprobado — lectura de Google Docs

Fuente: https://docs.google.com/document/d/14z_A_z1YTG5Pj5Uts0hP8RasWQNbZ8ZtvMGVArdb-Fk/edit

Copia de texto consultada al iniciar la implementación. Los diagramas originales están en Google Docs; las fuentes Mermaid actualizadas están en `diagramas.md`.

Análisis y diseño orientado a objetos del sistema web de reservas de restaurantes

Gerardo Ropero - Lina Castañeda - Juan Riaño

Ciencias De La Computación E Inteligencia Artificial

Patrones De Diseño De Software

José Marcial Téllez

Octubre, 2026

Análisis y diseño orientado a objetos del sistema web de reservas de restaurantes

Este proyecto propone una aplicación web para consultar disponibilidad y gestionar reservas de restaurantes mediante los roles de cliente y administrador. La solución se desarrollará con Python, Flask y SQLite, organizada en tres capas y con MVC en la presentación. El diseño integra Builder y Prototype como patrones creacionales, y Facade y Adapter como patrones estructurales.

La dificultad principal es coordinar horarios, capacidad de las mesas y permisos sin confirmar reservas incompatibles. Por ello, el diseño separa la interfaz, las reglas de negocio y el acceso a datos, y define una transacción para verificar disponibilidad y registrar cada reserva de forma indivisible.

Objetivos

Diseñar una aplicación web orientada a objetos que permita a clientes y administradores gestionar reservas válidas, mediante responsabilidades separadas, persistencia relacional y cuatro patrones de diseño explícitos.

Definir casos de uso, permisos y reglas verificables para los dos roles.

Establecer el modelo relacional y los contratos DAO necesarios para conservar los datos.

Justificar y representar los patrones, sus participantes y sus colaboraciones.

Preparar los criterios de prueba y el recorrido de sustentación del proyecto.

Alcance y decisiones

El núcleo comprende login, búsqueda, formulario de reserva y consulta del historial. Se incluye una configuración administrativa mínima de mesas y horarios para cubrir la gestión mencionada en el enunciado. Los restaurantes, las cuentas y las asignaciones de administradores se cargarán como datos de demostración. Se contemplan varios restaurantes y cada administrador tendrá un ámbito explícito.

Se excluyen de esta versión el registro público, la recuperación de contraseña, los pagos, los pedidos, las notificaciones externas y la combinación de mesas. Las reservas se confirmarán automáticamente si cumplen las reglas; no se requiere aprobación manual. Repetir una reserva prepara un formulario nuevo y no confirma automáticamente una reserva.

Actores y requisitos

Tabla 1

Permisos por actor

Operación

Cliente

Administrador

Iniciar y cerrar sesión

Su cuenta

Su cuenta

Buscar restaurantes y disponibilidad

Restaurantes activos

Restaurantes asignados

Crear reserva

Para sí mismo

Para cliente existente

Consultar cancelar y repetir

Sus propias reservas

Reservas de sus restaurantes

Gestionar mesas y horarios

Sin acceso

Solo restaurantes asignados

Asignar roles o restaurantes

Sin acceso

Sin interfaz en esta versión

El rol se obtiene de la cuenta autenticada. Los identificadores recibidos en formularios o direcciones web no acreditan propiedad ni permisos. ServicioAcceso comprobará la relación entre actor, recurso y restaurante en cada operación protegida.

Tabla 2

Requisitos funcionales

ID

Comportamiento verificable

RF01

Autenticar cuentas activas y cerrar la sesión.

RF02

Aplicar los permisos del rol y del restaurante en el servidor.

RF03

Buscar restaurantes activos por nombre o ciudad.

RF04

Consultar disponibilidad por restaurante inicio y personas.

RF05

Crear una reserva con asignación automática de mesa.

RF06

Listar reservas permitidas y mostrar sus detalles.

RF07

Cancelar una reserva futura y liberar su mesa.

RF08

Preparar una nueva reserva mediante una copia de datos.

RF09

Crear editar y desactivar mesas sin invalidar reservas.

RF10

Crear editar y eliminar franjas de atención válidas.

RF11

Permitir al administrador reservar para clientes existentes.

RF12

Conservar los datos tras reiniciar la aplicación.

Requisitos de calidad

La interfaz tendrá etiquetas visibles, navegación por teclado, mensajes junto a los campos y conservación de los valores válidos cuando exista un error. La validación del navegador se complementará con validación del servidor. Las observaciones se mostrarán como texto escapado y las consultas SQL utilizarán parámetros.

La solución deberá ser reproducible en Debian mediante un entorno virtual, dependencias fijadas y una base inicial. Las entidades y servicios podrán probarse sin abrir el navegador. Las credenciales se almacenarán con hash; la configuración secreta se mantendrá fuera del código entregado. Se verificará el comportamiento simultáneo de dos solicitudes que compitan por la misma mesa.

Reglas de negocio

Tabla 3

Reglas de reservas y configuración

ID

Regla

RN01

Cada cuenta tiene un rol CLIENTE o ADMINISTRADOR. Solo las cuentas activas pueden operar.

RN02

El cliente opera sobre sus reservas. El administrador requiere asignación al restaurante del recurso.

RN03

Una reserva ocupa una sola mesa activa de un restaurante activo. No se unen mesas.

RN04

Se asigna la menor capacidad disponible que cubra el grupo. El desempate usa el identificador de mesa.

RN05

Personas debe ser un entero positivo y no superar la capacidad de la mesa asignada.

RN06

El inicio debe ser futuro. La duración inicial es 90 minutos; se centraliza en la configuración del proyecto.

RN07

El intervalo completo debe caber en una franja del día. No se admiten franjas que crucen medianoche.

RN08

Dos reservas CONFIRMADA no pueden superponerse en la misma mesa. El extremo final no se incluye.

RN09

Los estados persistentes son CONFIRMADA y CANCELADA. El paso del tiempo no crea un tercer estado.

RN10

Solo se cancelan reservas confirmadas cuyo inicio aún no ha ocurrido. El registro no se elimina.

RN11

Una copia exige nueva disponibilidad y nuevo identificador. La reserva anterior no cambia.

RN12

Mesas y horarios no pueden modificarse de forma que invalide una reserva confirmada aún no finalizada.

RN13

Las franjas de un mismo día y restaurante no se superponen. Los inicios seleccionables avanzan en pasos de 30 minutos desde la apertura.

RN14

Los envíos repetidos con el mismo token y contenido no crean duplicados. Un contenido distinto requiere un token nuevo.

Para detectar superposición se verificará que el inicio nuevo sea anterior al fin existente y que el fin nuevo sea posterior al inicio existente. Así, una reserva puede empezar exactamente cuando termina otra. La búsqueda preliminar no bloquea mesas ni garantiza disponibilidad hasta confirmar la transacción.

Los horarios se interpretan en America/Bogota. Los instantes de reserva se convertirán a UTC y se guardarán como texto ISO 8601 de longitud y formato uniformes. La interfaz los convertirá a hora local. La duración aplicada se conserva mediante inicio y fin, aunque cambie la configuración para futuras reservas.

Casos de uso principales

CU01 Iniciar sesión

Actor: cliente o administrador. Precondición: existe una cuenta. El usuario envía correo y contraseña; el sistema valida el formulario, consulta la cuenta, verifica su estado y compara el hash. Si procede, crea la sesión y redirige al área del rol. Si no procede, muestra un mensaje genérico sin revelar si el correo existe. La poscondición es una sesión autenticada o ninguna sesión nueva.

CU02 Consultar disponibilidad

Actor: cliente o administrador autorizado. El usuario filtra restaurante, inicio y número de personas. El sistema verifica el formato, el horario y la capacidad, y muestra si existe al menos una mesa utilizable. Si el restaurante no corresponde al ámbito del administrador, se rechaza la operación. Una consulta sin mesas libres ofrece cambiar los criterios; no registra una reserva.

CU03 Crear una reserva

Precondición: actor autenticado y formulario completo. El cliente se toma de la sesión, salvo que un administrador autorizado seleccione un cliente activo existente. La capa de negocio abre una transacción de escritura, revalida permisos, consulta el token de operación y comprueba horario y mesas. El director y el builder construyen el objeto, el DAO lo guarda y se confirma la transacción. Se muestra identificador, restaurante, mesa, intervalo, personas y estado.

Alternativas: datos inválidos, recurso fuera del ámbito, cliente inactivo, horario cerrado, falta de capacidad o pérdida de disponibilidad producen rechazo sin inserción parcial. Ante un bloqueo que exceda el tiempo de espera, se conserva el formulario y se informa que puede reintentarse. La poscondición de éxito es exactamente una reserva confirmada para la solicitud.

CU04 Consultar y cancelar reservas

El sistema limita la consulta a las reservas del cliente o a los restaurantes del administrador. Para cancelar vuelve a comprobar propiedad, estado y hora actual dentro de la transacción. Cambia el estado a CANCELADA y conserva los demás datos. Una cancelación ya aplicada no debe repetirse como un nuevo efecto; una reserva iniciada se rechaza.

CU05 Repetir una reserva

El actor abre una reserva permitida y solicita repetirla. El sistema clona únicamente DatosReserva y precarga el formulario. El usuario debe seleccionar un inicio futuro y confirmar explícitamente. El formulario recibe un token nuevo; crear la reserva sigue íntegramente CU03. La fecha antigua puede mostrarse para editarla, pero nunca se acepta si ya pasó.

CU06 Gestionar mesas y horarios

El administrador selecciona uno de sus restaurantes. Para modificar la configuración se comprueban número de mesa único, capacidad positiva y franjas válidas. Dentro de una transacción se simula el efecto del cambio sobre las reservas confirmadas aún no finalizadas. Si alguna queda inválida, se rechaza todo el cambio y se explica el conflicto. La configuración inicial también debe respetar estas reglas.

Arquitectura y responsabilidades

La Figura 1 muestra las dependencias principales. MVC organiza la presentación: las vistas renderizan resultados y los controladores traducen solicitudes HTTP. Los servicios concentran los casos de uso y las entidades representan el dominio. Los DAO aíslan las consultas y la unidad de trabajo controla la transacción.

Figura 1

Arquitectura en tres capas con MVC en la presentación

Nota. Elaboración propia. Adapter integra la autenticación en el límite entre Flask Login y el dominio. Las flechas muestran llamadas principales; los resultados regresan al llamador.

Justificación tecnológica y de diseño

Flask ofrece una base web ligera para organizar rutas, plantillas y extensiones (Pallets, s. f.-b). Para este alcance se elige HTML renderizado en el servidor, de modo que login, formularios y navegación compartan una sola aplicación. Python permite definir contratos mediante clases abstractas y comprobación estática opcional con anotaciones de tipos (Python Software Foundation, s. f.-a).

SQLite simplifica la instalación y permite distribuir una base local reproducible. Su límite de un escritor simultáneo requiere transacciones cortas y una política de concurrencia explícita; resulta adecuado para la demostración académica prevista (SQLite, s. f.-a). Si el proyecto necesitara varios servidores o alta concurrencia de escritura, habría que evaluar otro motor y adaptar la persistencia.

El acceso a datos utilizará sqlite3 con SQL parametrizado y clases DAO explícitas, en lugar de mezclar consultas en controladores. El módulo permite administrar conexiones, consultas y transacciones desde Python (Python Software Foundation, s. f.-b). La migración futura de motor exigiría revisar SQL y transacciones aunque se conservaran los contratos de negocio.

Principios de orientación a objetos

Responsabilidad única: ServicioAcceso autoriza, ServicioDisponibilidad calcula opciones, ServicioReserva ejecuta operaciones y los DAO persisten. Encapsulación: Reserva controla su estado y conserva una copia propia de sus datos. Composición: la reserva contiene DatosReserva y el adapter contiene un Usuario. Se usa herencia para contratos explícitos, no para duplicar funciones por rol.

Inversión de dependencias: los servicios dependen de contratos DAO y de unidad de trabajo, con implementaciones SQLite suministradas al construir la aplicación. Interfaces específicas evitan imponer un CRUD completo a componentes de solo consulta. Las implementaciones deberán respetar los mismos significados de retorno y errores para permitir sustituciones en pruebas.

La aplicación tendrá un punto de composición create_app que registre rutas, extensiones y dependencias. Esa función de configuración no se contará como Factory Method. Tampoco se contarán los decoradores de rutas o autenticación como el patrón estructural Decorator. Los cuatro patrones evaluados tendrán participantes propios y pruebas de su comportamiento.

Organización prevista

Tabla 4

Paquetes y responsabilidades

Ubicación

Contenido

presentacion/

Controladores formularios plantillas y recursos estáticos.

dominio/

Usuario Restaurante Mesa HorarioAtencion Reserva DatosReserva y enumeraciones.

aplicacion/

Fachada servicios casos de uso y contratos de persistencia.

patrones/

Builder Prototype y adapter de sesión; fachada en aplicacion/.

infraestructura/

DAO SQLite unidad de trabajo esquema y datos iniciales.

tests/ y docs/

Pruebas diagramas y guion de demostración.

Modelo de clases del dominio

Usuario representa la identidad y el rol. Restaurante agrupa su configuración; Mesa aporta la capacidad física y HorarioAtencion define las franjas semanales. AsignacionAdministrador expresa qué restaurantes puede gestionar cada administrador. Reserva conserva identidad, cliente, creador, mesa, intervalo y estado; DatosReserva reúne los valores editables que se reutilizan al repetir una solicitud.

La Figura 2 separa entidades con identidad de datos copiables. El cliente y el creador pueden coincidir, pero son relaciones distintas. La asociación con Mesa determina el restaurante de la reserva. Esta estructura permite que el historial se conserve al cancelar y que el formulario trabaje sobre una copia independiente.

Figura 2

Entidades y composición del dominio

Nota. Elaboración propia. Reserva se relaciona con Usuario como cliente y como creador. Un administrador puede tener varias asignaciones. DatosReserva es un objeto del dominio y no una tabla independiente.

Modelo relacional

Figura 3

Tablas claves y relaciones del sistema

Nota. Elaboración propia. PK identifica una clave primaria y FK una clave foránea. Las relaciones 1 a N permiten cero registros dependientes. Los detalles y restricciones se precisan en el diccionario de datos.

Diccionario de datos

Todos los identificadores son INTEGER. Los campos indicados son obligatorios, salvo observaciones, que se normaliza a texto vacío. Los booleanos se almacenan como INTEGER restringido a 0 o 1. Los nombres de campos constituyen el contrato inicial del esquema.

Tabla 5

Usuarios restaurantes y asignaciones

Tabla y campo

Tipo

Restricción o significado

usuario.id

INTEGER

PK generada al insertar.

usuario.nombre

TEXT

Nombre visible obligatorio.

usuario.correo

TEXT

UNIQUE; normalizado a minúsculas.

usuario.hash_clave

TEXT

Hash con sal; nunca la contraseña original.

usuario.rol

TEXT

CHECK CLIENTE o ADMINISTRADOR.

usuario.activo

INTEGER

CHECK 0 o 1.

restaurante.id

INTEGER

PK.

restaurante.nombre

TEXT

Nombre obligatorio.

restaurante.ciudad

TEXT

Filtro de búsqueda.

restaurante.direccion

TEXT

Dirección visible.

restaurante.activo

INTEGER

CHECK 0 o 1.

administrador_restaurante.usuario_id

INTEGER

FK usuario; parte de PK compuesta.

administrador_restaurante.restaurante_id

INTEGER

FK restaurante; parte de PK compuesta.

La asignación solo puede vincular cuentas de rol ADMINISTRADOR. Esa condición entre tablas se verificará en el servicio y en la carga inicial. La tabla asociativa evita almacenar listas de restaurantes dentro de una columna de usuario.

Tabla 6

Mesas y horarios de atención

Tabla y campo

Tipo

Restricción o significado

mesa.id

INTEGER

PK.

mesa.restaurante_id

INTEGER

FK restaurante.

mesa.numero

TEXT

Único junto con restaurante_id.

mesa.capacidad

INTEGER

CHECK mayor que cero.

mesa.activa

INTEGER

CHECK 0 o 1.

horario_atencion.id

INTEGER

PK.

horario_atencion.restaurante_id

INTEGER

FK restaurante.

horario_atencion.dia_semana

INTEGER

CHECK entre 1 lunes y 7 domingo.

horario_atencion.apertura

TEXT

Hora local HH:MM válida.

horario_atencion.cierre

TEXT

Hora local HH:MM; posterior a apertura.

Cada fila de horario representa una franja. Un día cerrado no tiene franjas. Se admiten, por ejemplo, dos servicios separados por un cierre intermedio; una reserva no puede atravesar ese cierre. No se modelan festivos ni excepciones por fecha en esta primera versión.

Tabla 7

Reservas

Campo de reserva

Tipo

Restricción o significado

id

INTEGER

PK generada; ausente antes de persistir.

cliente_id

INTEGER

FK usuario con rol CLIENTE.

creado_por_id

INTEGER

FK usuario que realizó la operación.

mesa_id

INTEGER

FK mesa; determina el restaurante.

inicio

TEXT

Instante UTC ISO 8601 uniforme.

fin

TEXT

Mismo formato; CHECK fin > inicio.

personas

INTEGER

CHECK mayor que cero.

observaciones

TEXT

Hasta 500 caracteres; vacío permitido.

estado

TEXT

CHECK CONFIRMADA o CANCELADA.

fecha_creacion

TEXT

Instante UTC de registro.

token_operacion

TEXT

UNIQUE; identifica un envío lógico.

El modelo separa las entidades y evita repetir el nombre del cliente, la dirección del restaurante o la capacidad de la mesa en cada reserva. El restaurante se obtiene mediante mesa_id. Al reconstruir DatosReserva, el DAO incorpora restaurante_id desde esa relación; no se guarda una segunda referencia que pueda discrepar. Fin es un dato del intervalo contratado, no se recalcula al consultar el historial.

Integridad e índices

Se habilitará PRAGMA foreign_keys = ON para cada conexión. Las eliminaciones referenciadas se restringirán; la desactivación conservará el historial. SQLite requiere activar explícitamente la comprobación de claves foráneas según la configuración de conexión (SQLite, s. f.-c).

Se crearán índices para reservas por mesa estado e intervalo, por cliente e inicio y por restaurante y día en los horarios. Las restricciones UNIQUE protegerán correo, número de mesa por restaurante, asignación administrativa y token de operación. El control de solapamientos se realizará bajo la transacción de escritura y se reforzará mediante disparadores de inserción y actualización de reservas confirmadas.

Diseño DAO y unidad de trabajo

Los DAO traducen entre filas y entidades; no deciden permisos ni reglas del restaurante. El servicio utiliza sus contratos y recibe errores de dominio estables, sin depender de mensajes específicos del motor. Las Figuras 4 y 5 dividen el diagrama DAO para conservar la legibilidad. Una línea discontinua con triángulo representa la implementación de un contrato.

Figura 4

DAO de reservas y mesas con unidad de trabajo

Nota. Elaboración propia. UnidadTrabajoSqlite proporciona una misma conexión a los DAO de una operación. Guardar dentro de un DAO no realiza un commit independiente.

Figura 5

DAO de usuarios restaurantes horarios y asignaciones

Nota. Elaboración propia. ServicioAutenticacion consume UsuarioDAO; ServicioAcceso consume AsignacionAdminDAO; los servicios de consulta y configuración utilizan RestauranteDAO y HorarioDAO.

Contratos transaccionales

UnidadTrabajo define iniciar_escritura, confirmar y revertir, y expone los DAO vinculados a la operación. UnidadTrabajoSqlite implementa ese contrato. Ningún DAO abre una segunda conexión durante una reserva. Se evita compartir una conexión mutable global entre solicitudes.

buscar_por_id devuelve una entidad o ausencia; listar devuelve una colección, incluso vacía; guardar devuelve la entidad con identificador. Los filtros de consulta se reciben como valores. Los nombres de columna permitidos para ordenación se seleccionan mediante una lista cerrada y nunca se concatenan desde entradas libres del usuario.

Control de disponibilidad y concurrencia

La secuencia de escritura comenzará con BEGIN IMMEDIATE antes de consultar la disponibilidad definitiva. SQLite serializa las escrituras y este inicio reserva el acceso de escritura para evitar que otra operación se inserte entre la comprobación y el registro (SQLite, s. f.-b). No se utilizará SELECT FOR UPDATE, que no corresponde a este mecanismo de SQLite.

Validar formato y convertir fecha y hora a un instante consciente de zona horaria.

Abrir la unidad de trabajo e iniciar la transacción de escritura.

Releer actor cliente restaurante y asignaciones; comprobar permisos y estados activos.

Buscar el token. Si ya existe para el mismo actor y contenido, devolver esa reserva; si discrepa, rechazar el uso del token.

Comprobar futuro duración franja completa y candidatos por capacidad; consultar superposiciones confirmadas.

Construir la reserva mediante DirectorReserva y ReservaBuilder; insertar con los DAO de la misma conexión.

Confirmar si todos los pasos finalizan; revertir ante cualquier fallo y traducir el error a un mensaje seguro.

Las cancelaciones y los cambios de mesas u horarios utilizarán la misma política de escritura. El tiempo máximo inicial de espera por bloqueo será de cinco segundos. Agotado el plazo se devolverá un error recuperable; reintentar conservará el token de la operación. La exclusión de escrituras no sustituye las reglas ni elimina la necesidad de probar dos conexiones independientes.

Para editar capacidad, desactivar una mesa o cambiar un horario se cargarán las reservas confirmadas con fin posterior a la hora actual. Se comprobará el resultado propuesto antes de guardar. Las reservas ya finalizadas conservarán su información histórica. Desactivar una mesa con una reserva vigente incompatible se rechazará sin efectuar el cambio.

Patrones creacionales y estructurales

Los patrones documentan soluciones reutilizables a problemas recurrentes de colaboración entre objetos (Gamma et al., 1995). En este proyecto se eligen cuatro por su participación concreta en los casos de uso. Su clasificación y demostración se resumen en la Tabla 8; la correspondencia se validará contra las clases finalmente implementadas.

Tabla 8

Patrones seleccionados y evidencia prevista

Patrón

Problema resuelto

Demostración

Builder creacional

Construcción ordenada de una reserva completa.

Rechazar construcción incompleta y crear una reserva válida.

Prototype creacional

Preparar una reserva similar sin mutar la original.

Modificar la copia y verificar original intacto.

Facade estructural

Coordinar acceso disponibilidad y operaciones.

Seguir una llamada del controlador a los servicios.

Adapter estructural

Compatibilizar Usuario con Flask Login.

Iniciar sesión a través de UsuarioSesionAdapter.

Builder

Builder separa los pasos de construcción de un objeto de su representación final. Aquí el producto es Reserva; ConstructorReserva define los pasos, ReservaBuilder los implementa y DirectorReserva fija el orden. ServicioReserva entrega un contexto ya autorizado con la mesa seleccionada. La Figura 6 muestra estos participantes.

El director reinicia el builder, añade cliente, mesa, intervalo, detalles y auditoría, y solicita construir. El producto nace con estado CONFIRMADA e id ausente hasta la inserción. La construcción comprueba campos obligatorios, personas positivas, coherencia de intervalo y capacidad suministrada. No consulta la base de datos ni decide permisos.

Se utilizará una instancia nueva por operación para impedir que valores de una reserva pasen a otra. El constructor del producto también conservará sus invariantes básicas. La ventaja es un proceso explícito y extensible; el costo es incorporar director y contrato para un único producto inicial. Esa estructura tiene un propósito didáctico y permite futuras variantes sin alterar al cliente.

Figura 6

Diagrama de control del patrón Builder

Nota. Elaboración propia. ConstructorReserva es una clase abstracta. El director depende del contrato y el builder concreto crea Reserva. Las flechas discontinuas simples representan dependencias.

Verificación de Builder

Se probará que omitir mesa o cliente impide construir, que un intervalo incoherente se rechaza y que dos usos sucesivos no comparten datos. La evidencia mostrará el contrato, el director, el builder y la llamada real desde ServicioReserva, además del resultado del formulario.

Prototype

Prototype obtiene nuevos objetos a partir de la copia de un objeto existente. El prototipo será DatosReserva, compuesto por restaurante, inicio, personas y observaciones; Prototipo define clonar. Reserva conservará una instancia propia y la fachada preparará una copia para el formulario de repetición. La Figura 7 representa esta colaboración.

Figura 7

Diagrama de control del patrón Prototype

Nota. Elaboración propia. El rombo lleno representa composición. Solo se clonan los datos editables; identidad estado mesa y auditoría pertenecen a Reserva.

Los campos actuales contienen valores inmutables; se crea un contenedor independiente. Si se añaden colecciones mutables, clonar deberá copiarlas de forma profunda. Las pruebas comprobarán igual contenido inicial, identidad distinta y ausencia de cambios en el original. La copia siempre vuelve a pasar por disponibilidad y Builder antes de persistir.

Facade

Facade ofrece un punto de entrada coherente a un conjunto de servicios. ReservaFacade expone operaciones de reserva y coordina ServicioAcceso, ServicioDisponibilidad y ServicioReserva. Los controladores no necesitan conocer sus colaboraciones internas. La Figura 8 muestra la fachada y su subsistema.

Figura 8

Diagrama de control del patrón Facade

Nota. Elaboración propia. El recuadro Disponibilidad representa ServicioDisponibilidad. La fachada coordina; las reglas permanecen en los servicios especializados.

La fachada facilita reutilizar los mismos casos de uso desde las vistas de cliente y administrador. El servicio transaccional mantiene la autorización definitiva dentro de la operación para evitar que una llamada directa omita controles. Se evitará convertir la fachada en una clase que contenga SQL, construcción HTML y todas las validaciones.

Adapter

Adapter traduce entre interfaces diferentes. Flask Login espera get_id e indicadores de autenticación y actividad; nuestro Usuario conserva un identificador entero, rol y estado propios (Flask-Login contributors, s. f.). UsuarioSesionAdapter envolverá la entidad y ofrecerá ese contrato, como muestra la Figura 9.

Figura 9

Diagrama de control del patrón Adapter

Nota. Elaboración propia. El contrato externo representa los miembros esperados por Flask Login; no implica que la biblioteca proporcione una clase abstracta con ese nombre.

get_id devolverá el identificador como cadena; is_active reflejará la cuenta y los demás indicadores describirán un usuario autenticado real. El adapter se creará después de verificar credenciales. No autorizará restaurantes ni validará reservas. La entidad Usuario seguirá libre de dependencias de Flask. La prueba verificará la conversión del identificador y el rechazo de cuentas inactivas.

Colaboración durante una reserva

Figura 10

Secuencia simplificada para crear una reserva

Nota. Elaboración propia. En cada error entre BEGIN IMMEDIATE y COMMIT se ejecuta ROLLBACK. La consulta de token precede a la nueva inserción. El éxito vuelve al controlador para mostrar la confirmación.

Diseño de interfaz y navegación

Las vistas comparten navegación y componentes del formulario. El diseño evita exigir que el cliente conozca la numeración de mesas: la asignación se calcula en el servidor. La disponibilidad se presenta como resultado provisional hasta confirmar la reserva. El listado distingue próximas, anteriores y canceladas a partir de inicio fin y estado.

Tabla 9

Pantallas y contenido

Vista

Contenido y acciones

Login

Correo contraseña entrar y mensaje genérico de error. El rol no es un campo editable.

Buscar y reservar

Nombre o ciudad restaurante fecha hora personas y observaciones. Consultar disponibilidad y confirmar.

Mis reservas

Listado y detalle; cancelar cuando procede; volver a reservar.

Reservas del administrador

Restaurante autorizado filtros por fecha y estado cliente existente y formulario de creación.

Mesas y horarios

Pestañas con número capacidad activación día apertura y cierre. Los conflictos se muestran antes de guardar.

Rutas previstas

Tabla 10

Contratos HTTP

Método y ruta

Responsabilidad

GET y POST /login

Mostrar formulario y autenticar.

POST /logout

Cerrar sesión con protección CSRF.

GET /restaurantes

Buscar opciones según el actor.

GET /reservas/nueva

Mostrar formulario y consulta de disponibilidad.

POST /reservas

Crear con identidad y permisos comprobados.

GET /reservas

Listar únicamente reservas permitidas.

GET /reservas/<id>

Mostrar detalle autorizado.

POST /reservas/<id>/cancelar

Cancelar una reserva permitida.

GET /reservas/<id>/repetir

Preparar copia sin persistirla.

GET y POST /admin/mesas

Consultar y guardar configuración autorizada.

GET y POST /admin/horarios

Consultar y guardar franjas autorizadas.

Las acciones que modifican datos usarán POST y CSRF. Al completar un envío se redirigirá a una vista de resultado para evitar que actualizar la página repita el POST. Los errores de permisos producirán rechazo; la falta de disponibilidad será un conflicto comprensible con los datos del formulario preservados.

Autenticación y seguridad del módulo

ServicioAutenticacion buscará al usuario mediante UsuarioDAO y verificará las credenciales con las funciones de hash y comparación de Werkzeug (Pallets, s. f.-a). Se utilizará la implementación de biblioteca y no un algoritmo casero. Flask Login administrará la sesión; los permisos por rol, propiedad y restaurante seguirán siendo responsabilidad de ServicioAcceso.

Flask-WTF protegerá los formularios con tokens CSRF (Flask-WTF contributors, s. f.). Ese token evita solicitudes falsificadas y es distinto de token_operacion, que previene duplicados. Se validarán también los campos en el servidor, se escaparán observaciones al mostrarlas y se mantendrán consultas parametrizadas. Las redirecciones después del login solo admitirán destinos internos.

La clave de sesión se suministrará mediante configuración local externa. Las cookies usarán HttpOnly y SameSite; Secure se activará al servir mediante HTTPS. El entorno de demostración funcionará de forma local. Las capturas y el video mostrarán cuentas de prueba, sin claves privadas, hashes completos ni datos personales reales.

Datos iniciales y ejecución prevista

El conjunto de demostración tendrá al menos dos restaurantes, dos administradores con ámbitos distintos y dos clientes. Habrá mesas con diferentes capacidades y horarios que permitan probar apertura, cierre intermedio y falta de disponibilidad. Las reservas de prueba se calcularán respecto de un reloj controlado para que el proyecto no dependa de fechas vencidas.

La implementación entregará instrucciones para crear un entorno virtual, instalar las dependencias fijadas, inicializar la base y ejecutar la aplicación. La inicialización será explícita y no borrará datos al arrancar. Las pruebas utilizarán una base temporal independiente. El ZIP contendrá código esquema datos iniciales diagramas y un README; no incluirá el entorno virtual ni secretos.

Plan de pruebas y criterios de aceptación

Las siguientes pruebas son planificadas y no se presentan como ejecutadas. Se combinarán pruebas unitarias de dominio y patrones, pruebas de integración de DAO y transacciones, y pruebas HTTP de los dos roles. El reloj se inyectará para verificar límites temporales de forma reproducible.

Tabla 11

Casos de prueba funcionales e integridad

ID

Escenario

Resultado esperado

P01

Login válido y cuenta activa.

Sesión y área del rol correctas.

P02

Clave incorrecta o cuenta inactiva.

Rechazo sin sesión nueva.

P03

Cliente intenta ruta administrativa.

Acceso denegado.

P04

Administrador A usa recurso de B.

Rechazo y ningún cambio.

P05

Cliente consulta reserva ajena.

Rechazo sin exponer los detalles.

P06

Reserva válida y mesa suficiente.

Una confirmación y mesa mínima adecuada.

P07

Personas cero negativo o texto.

Validación y ninguna inserción.

P08

Inicio pasado o exactamente actual.

Rechazo por tiempo inválido.

P09

Intervalo supera el cierre o cruza descanso.

Rechazo por horario.

P10

No existe mesa de capacidad suficiente.

Mensaje de falta de capacidad.

P11

Dos intervalos superpuestos en una mesa.

Solo uno puede quedar confirmado.

P12

Una reserva empieza al terminar otra.

Se permite si cumple las demás reglas.

P13

Cancelar reserva futura.

Estado CANCELADA y mesa liberada.

P14

Cancelar después del inicio.

Rechazo y estado conservado.

P15

Desactivar o reducir mesa incompatible.

Rechazo sin invalidar reservas.

P16

Eliminar o reducir horario incompatible.

Rechazo del cambio completo.

P17

Dos solicitudes simultáneas por última mesa.

Exactamente una confirmación.

P18

Repetir POST con mismo token y contenido.

Misma reserva sin duplicado.

P19

Mismo token con actor o contenido distinto.

Rechazo y sin revelar reserva ajena.

P20

Fallo durante una escritura.

Rollback y ausencia de cambios parciales.

P21

Reiniciar la aplicación.

Datos persistentes conservados.

P22

POST sin CSRF o con token inválido.

Rechazo de la solicitud.

P23

Observaciones con etiquetas HTML.

Se muestran como texto sin ejecutarse.

P24

Número de mesa o correo duplicados.

Restricción aplicada.

Tabla 12

Pruebas de patrones

ID

Prueba

Resultado esperado

P25

Builder incompleto e intervalo inválido.

Construcción rechazada.

P26

Builder usado para dos operaciones.

Objetos independientes sin datos residuales.

P27

Clonar y modificar DatosReserva.

Original intacto y copia distinta.

P28

Repetir una reserva sin cupo actual.

Formulario precargado y confirmación rechazada.

P29

Llamada a la fachada desde ambos roles.

Servicios coordinados con permisos correctos.

P30

Adapter con id entero y usuario inactivo.

Id cadena y actividad coherente.

La prueba P17 utilizará un archivo temporal compartido y dos conexiones independientes sincronizadas para competir. Se verificará el número de reservas confirmadas y la respuesta de cada solicitud. Una prueba secuencial de dos inserciones no reemplaza esta prueba de concurrencia.

Trazabilidad de los entregables

Tabla 13

Correspondencia entre enunciado diseño y evidencia

Exigencia

Diseño incluido

Evidencia posterior

Análisis orientado a objetos

Actores RF01 a RF12 RN01 a RN14 y CU01 a CU06.

Casos de prueba P01 a P24.

Tres capas o MVC

Arquitectura responsabilidades y Figura 1.

Paquetes y recorrido del controlador al DAO.

Modelo relacional

Figura 3 diccionario integridad e índices.

Esquema SQL y base inicial.

Diagrama DAO

Figuras 4 y 5 y contratos transaccionales.

Clases abstractas e implementaciones SQLite.

Dos creacionales

Builder y Prototype; Figuras 6 y 7.

Código y pruebas P25 a P28.

Dos estructurales

Facade y Adapter; Figuras 8 y 9.

Código y pruebas P29 y P30.

Login y reservas por rol

Pantallas rutas y casos de uso.

Capturas de cliente administrador y rechazos.

Documento APA

Portada estructura citas referencias figuras y tablas.

Completar datos académicos y evidencias reales.

Código fuente

Organización y contratos definidos.

ZIP reproducible con README y dependencias.

Video en YouTube

Guion propuesto en el siguiente apartado.

Enlace real tras grabar y publicar.

Criterio de cierre de la implementación

La aplicación estará lista para la entrega cuando los requisitos del alcance estén implementados, los cuatro patrones participen en los flujos reales, las pruebas previstas tengan resultados registrados y el proyecto se ejecute desde una instalación limpia. Antes de documentar se compararán nombres, métodos y relaciones de los diagramas con el código final.

Evidencias por incorporar tras la implementación

Este apartado define las evidencias que completarán el informe. Su estado actual es pendiente de implementación. Cada captura deberá llevar número de figura, título y una nota que explique qué requisito demuestra; se usará tamaño suficiente para leer el fragmento relevante.

Tabla 14

Capturas de código y ejecución previstas

ID

Evidencia

Qué debe demostrar

E01

Estructura y llamada entre capas.

Separación presentación negocio y persistencia.

E02

Contrato y DAO SQLite de reservas.

SQL parametrizado y conexión de la unidad de trabajo.

E03

Director contrato y builder.

Pasos reales de construcción y validaciones.

E04

clonar y su llamada desde repetición.

Copia independiente usada por el formulario.

E05

Fachada y controlador.

Coordinación efectiva del caso de uso.

E06

Adapter y autenticación.

Contrato de sesión aplicado al Usuario.

E07

Login cliente y administrador.

Acceso diferenciado con datos de prueba.

E08

Reserva válida y listado.

Persistencia y mesa asignada.

E09

Sin disponibilidad o fuera de horario.

Rechazo con mensaje útil.

E10

Cancelación y nueva disponibilidad.

Liberación sin borrar historial.

E11

Mesas horarios y permisos.

Configuración protegida y ámbitos distintos.

E12

Salida de pruebas y concurrencia.

Resultados reales y detalle de P17.

Se incorporará una tabla de resultados con prueba, resultado obtenido, estado, evidencia y observaciones. No se declararán pruebas aprobadas antes de ejecutarlas. Los defectos encontrados y su corrección se documentarán si afectan las decisiones del diseño.

Guion del video de sustentación

Se propone un video de 8 a 10 minutos, ajustable a la indicación del docente. El equipo deberá explicar decisiones y recorrer código y aplicación. Aunque el enunciado del video menciona expresamente los dos creacionales, se mostrarán también los dos estructurales para cubrir el proyecto completo.

Tabla 15

Recorrido sugerido del video

Tiempo aproximado

Contenido

0 a 1 minuto

Problema alcance roles y arquitectura.

1 a 2 minutos

Modelo relacional y diagrama DAO.

2 a 4 minutos

Builder y Prototype con clases y uso real.

4 a 5 minutos

Facade y Adapter con dependencias.

5 a 8 minutos

Login por rol reserva válida rechazo repetición cancelación y administración.

8 a 10 minutos

Pruebas relevantes concurrencia y explicación de ejecución local.

Enlace de YouTube: pendiente de grabación y publicación. Antes de entregar se comprobará que el enlace abre y tiene los permisos necesarios para la revisión del docente.

Conclusiones del diseño

La propuesta vincula cada patrón con un caso de uso identificable y separa las reglas del acceso a datos. La reserva se trata como una operación transaccional, con controles de ámbito e integridad que se pueden probar. Este diseño constituye la base para implementar la aplicación y completar posteriormente las evidencias del informe.

El formato sigue la guía estudiantil de la American Psychological Association (2025), con espaciado adaptado en tablas y figuras para facilitar la lectura.

Referencias

American Psychological Association. (2025). Student paper setup guide. https://apastyle.apa.org/instructional-aids/student-paper-setup-guide.pdf

Flask-Login contributors. (s. f.). Flask-Login documentation. https://flask-login.readthedocs.io/en/latest/

Flask-WTF contributors. (s. f.). CSRF protection. https://flask-wtf.readthedocs.io/en/latest/csrf/

Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1995). Design patterns: Elements of reusable object-oriented software. Addison-Wesley. https://www.informit.com/store/design-patterns-elements-of-reusable-object-oriented-9780201633610

Pallets. (s. f.-a). Utilities. Werkzeug documentation. https://werkzeug.palletsprojects.com/en/stable/utils/

Pallets. (s. f.-b). Welcome to Flask. https://flask.palletsprojects.com/en/stable/

Python Software Foundation. (s. f.-a). abc — Abstract base classes. https://docs.python.org/3/library/abc.html

Python Software Foundation. (s. f.-b). sqlite3 — DB-API 2.0 interface for SQLite databases. https://docs.python.org/3/library/sqlite3.html

SQLite. (s. f.-a). Appropriate uses for SQLite. https://www.sqlite.org/whentouse.html

SQLite. (s. f.-b). Isolation in SQLite. https://sqlite.org/isolation.html

SQLite. (s. f.-c). SQLite foreign key support. https://sqlite.org/foreignkeys.html
