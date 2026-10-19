# Diagramas de la implementación

Los nombres corresponden a las clases del código entregado. GitHub renderiza los bloques Mermaid. Cada bloque también está disponible como `.mmd` en `docs/diagramas/` para editarlo o importarlo en una herramienta compatible. Se incluyen también versiones SVG y PNG renderizadas y verificadas de los diez diagramas.

## 1. Arquitectura en tres capas

```mermaid
flowchart TB
  subgraph P["Presentación · MVC"]
    C["Controladores Flask y formularios"]
    V["Plantillas Jinja y recursos locales"]
    C --> V
  end
  subgraph A["Aplicación y dominio"]
    F["ReservaFacade y servicios"]
    D["Entidades y patrones creacionales"]
    I["Contratos DAO y UnidadTrabajo"]
    F --> D
    F --> I
  end
  subgraph X["Infraestructura"]
    Q["DAO SQLite y UnidadTrabajoSqlite"]
    B[("SQLite")]
    Q --> B
  end
  C --> F
  Q -. implementa .-> I
```

`create_app` conecta los contratos con SQLite mediante una función que construye una unidad de trabajo nueva. El dominio no importa Flask. La interfaz depende de los casos de uso, no de SQL.

## 2. Clases del dominio

```mermaid
classDiagram
  direction TB
  class Usuario {
    +int id
    +str nombre
    +str correo
    +Rol rol
    +bool activo
  }
  class Restaurante {
    +int id
    +str nombre
    +str ciudad
    +bool activo
  }
  class AsignacionAdministrador {
    +int usuario_id
    +int restaurante_id
  }
  class Mesa {
    +int id
    +int restaurante_id
    +str numero
    +int capacidad
    +bool activa
  }
  class HorarioAtencion {
    +int id
    +int restaurante_id
    +int dia_semana
    +time apertura
    +time cierre
  }
  class Reserva {
    +int id
    +int cliente_id
    +int creado_por_id
    +int mesa_id
    -DatosReserva _datos
    -EstadoReserva _estado
    +datetime fin
    +datetime fecha_creacion
    +str token_operacion
    +cancelar(ahora) bool
  }
  class DatosReserva {
    +int restaurante_id
    +datetime inicio
    +int personas
    +str observaciones
    +validar()
    +clonar() DatosReserva
  }
  Usuario "1" --> "0..*" AsignacionAdministrador
  Restaurante "1" --> "0..*" AsignacionAdministrador
  Restaurante "1" --> "0..*" Mesa
  Restaurante "1" --> "0..*" HorarioAtencion
  Usuario "1" --> "0..*" Reserva : cliente
  Usuario "1" --> "0..*" Reserva : creador
  Mesa "1" --> "0..*" Reserva
  Reserva "1" *-- "1" DatosReserva
```

Las asociaciones se representan mediante identificadores al persistir. `Reserva.datos` expone una copia para proteger su composición; `cancelar` controla la transición a CANCELADA.

## 3. Modelo relacional

```mermaid
erDiagram
  direction TB
  usuario {
    INTEGER id PK
    TEXT nombre
    TEXT correo UK
    TEXT hash_clave
    TEXT rol
    INTEGER activo
  }
  restaurante {
    INTEGER id PK
    TEXT nombre
    TEXT ciudad
    TEXT direccion
    INTEGER activo
  }
  administrador_restaurante {
    INTEGER usuario_id PK,FK
    INTEGER restaurante_id PK,FK
  }
  mesa {
    INTEGER id PK
    INTEGER restaurante_id FK
    TEXT numero
    INTEGER capacidad
    INTEGER activa
  }
  horario_atencion {
    INTEGER id PK
    INTEGER restaurante_id FK
    INTEGER dia_semana
    TEXT apertura
    TEXT cierre
  }
  reserva {
    INTEGER id PK
    INTEGER cliente_id FK
    INTEGER creado_por_id FK
    INTEGER mesa_id FK
    TEXT inicio
    TEXT fin
    INTEGER personas
    TEXT observaciones
    TEXT estado
    TEXT fecha_creacion
    TEXT token_operacion UK
  }
  usuario ||--o{ administrador_restaurante : administra
  restaurante ||--o{ administrador_restaurante : asigna
  restaurante ||--o{ mesa : contiene
  restaurante ||--o{ horario_atencion : atiende
  mesa ||--o{ reserva : ocupa
  usuario ||--o{ reserva : cliente
  usuario ||--o{ reserva : creador
```

Además de lo indicado, `UNIQUE(restaurante_id, numero)` protege el número de mesa. `schema.sql` contiene los CHECK, índices y triggers. `DatosReserva` se reconstruye mediante un JOIN con mesa; no existe una tabla adicional ni un restaurante duplicado en reserva.

## 4. DAO de reservas, mesas y unidad de trabajo

```mermaid
classDiagram
  direction TB
  class UnidadTrabajo {
    <<abstract>>
    +ReservaDAO reservas
    +MesaDAO mesas
    +UsuarioDAO usuarios
    +RestauranteDAO restaurantes
    +HorarioDAO horarios
    +AsignacionAdminDAO asignaciones
    +iniciar_escritura()
    +confirmar()
    +revertir()
  }
  class ReservaDAO {
    <<abstract>>
    +buscar_por_id(id)
    +buscar_por_token(token)
    +buscar_solapadas(mesa_id, inicio, fin)
    +listar(cliente_id, restaurante_ids)
    +listar_vigentes(restaurante_id, ahora)
    +guardar(reserva)
    +cancelar(reserva)
  }
  class MesaDAO {
    <<abstract>>
    +buscar_por_id(id)
    +listar(restaurante_id)
    +listar_candidatas(restaurante_id, personas)
    +guardar(mesa)
  }
  class UnidadTrabajoSqlite {
    +Connection conexion
    +iniciar_escritura()
    +confirmar()
    +revertir()
  }
  class SqliteReservaDAO {
    +Connection conexion
  }
  class SqliteMesaDAO {
    +Connection conexion
  }
  UnidadTrabajo <|-- UnidadTrabajoSqlite
  ReservaDAO <|-- SqliteReservaDAO
  MesaDAO <|-- SqliteMesaDAO
  UnidadTrabajoSqlite *-- SqliteReservaDAO
  UnidadTrabajoSqlite *-- SqliteMesaDAO
```

La unidad de trabajo implementa un administrador de contexto (`__enter__`, `__exit__`). Crea sus DAO y les entrega una sola conexión. Desactivar una mesa se expresa mediante `guardar` con `activa=False`, sin borrar la fila.

## 5. DAO de catálogos y autorización

```mermaid
classDiagram
  direction TB
  class UsuarioDAO {
    <<abstract>>
    +buscar_por_id(id)
    +buscar_por_correo(correo)
    +listar_clientes()
  }
  class RestauranteDAO {
    <<abstract>>
    +buscar_por_id(id)
    +buscar(nombre, ciudad)
  }
  class HorarioDAO {
    <<abstract>>
    +listar_por_dia(restaurante_id, dia)
    +listar(restaurante_id)
    +buscar_por_id(id)
    +guardar(horario)
    +eliminar_franja(id)
  }
  class AsignacionAdminDAO {
    <<abstract>>
    +puede_gestionar(usuario_id, restaurante_id)
    +listar_restaurantes(usuario_id)
  }
  UsuarioDAO <|-- SqliteUsuarioDAO
  RestauranteDAO <|-- SqliteRestauranteDAO
  HorarioDAO <|-- SqliteHorarioDAO
  AsignacionAdminDAO <|-- SqliteAsignacionAdminDAO
```

Todos los DAO SQLite reciben la conexión de `UnidadTrabajoSqlite`; no abren conexiones secundarias ni confirman transacciones. Las clases de servicios establecen los permisos.

## 6. Builder

```mermaid
classDiagram
  direction TB
  class ConstructorReserva {
    <<abstract>>
    +reiniciar()
    +con_cliente(cliente_id)
    +con_mesa(mesa)
    +con_intervalo(inicio, fin)
    +con_detalles(personas, observaciones)
    +con_auditoria(creado_por_id, fecha_creacion, token)
    +construir() Reserva
  }
  class ReservaBuilder {
    -dict _valores
    +construir() Reserva
  }
  class DirectorReserva {
    +ConstructorReserva constructor
    +preparar(contexto) Reserva
  }
  class ContextoReserva {
    +int cliente_id
    +int creado_por_id
    +Mesa mesa
    +DatosReserva datos
    +datetime fin
    +datetime ahora
    +str token
  }
  ServicioReserva ..> DirectorReserva : utiliza
  ServicioReserva ..> ContextoReserva : crea
  DirectorReserva --> ConstructorReserva
  DirectorReserva ..> ContextoReserva
  ConstructorReserva <|-- ReservaBuilder
  ReservaBuilder ..> Reserva : construye
```

`ServicioReserva` valida permisos y disponibilidad antes de construir. El director depende del contrato. El builder valida completitud e invariantes y entrega una reserva sin ID; SQLite asigna su identidad al guardar.

## 7. Prototype

```mermaid
classDiagram
  direction TB
  class Prototipo~T~ {
    <<abstract>>
    +clonar() T
  }
  class DatosReserva {
    +int restaurante_id
    +datetime inicio
    +int personas
    +str observaciones
    +clonar() DatosReserva
  }
  class Reserva {
    -DatosReserva _datos
    +datos() DatosReserva
  }
  class ReservaFacade {
    +preparar_repeticion(actor_id, reserva_id) DatosReserva
  }
  Prototipo <|-- DatosReserva
  Reserva *-- DatosReserva
  ReservaFacade ..> Reserva : autoriza y consulta
  ReservaFacade ..> DatosReserva : solicita copia
  ReservaForm ..> DatosReserva : precarga valores
```

`datos` es una propiedad de Python, representada aquí como acceso de lectura. La copia tiene identidad propia como objeto; no contiene ID ni estado de la reserva anterior. Actualmente todos sus atributos son inmutables: basta construir otro contenedor mediante `dataclasses.replace`.

## 8. Facade y servicios

```mermaid
classDiagram
  direction TB
  class ReservaFacade {
    +consultar_disponibilidad(actor_id, datos)
    +horarios_disponibles(actor_id, restaurante_id, fecha, personas)
    +crear_reserva(actor_id, datos, token, cliente_id)
    +listar_reservas(actor_id, restaurante_id, fecha, estado)
    +obtener_detalle(actor_id, reserva_id)
    +cancelar_reserva(actor_id, reserva_id)
    +preparar_repeticion(actor_id, reserva_id)
  }
  class ServicioReserva {
    +crear(actor_id, datos, token, cliente_id)
    +cancelar(actor_id, reserva_id)
  }
  class ServicioDisponibilidad {
    +seleccionar(uow, datos, ahora)
    +horarios_del_dia(uow, restaurante_id, fecha, personas, ahora)
    +cabe_en_franjas(inicio, fin, franjas, comprobar_paso)
  }
  class ServicioAcceso {
    +actor(uow, actor_id)
    +administrador(actor)
    +restaurante(uow, actor, restaurante_id)
    +reserva(uow, actor, reserva_id)
  }
  ControladoresFlask ..> ReservaFacade
  ReservaFacade --> ServicioReserva
  ReservaFacade --> ServicioDisponibilidad
  ReservaFacade --> ServicioAcceso
  ServicioReserva --> ServicioDisponibilidad
  ServicioReserva --> ServicioAcceso
  ServicioReserva ..> UnidadTrabajo
```

La fachada conserva la autorización de lectura y delega la creación y cancelación al servicio transaccional. Los servicios de catálogos y configuración tienen casos de uso separados para mantener acotada la fachada.

## 9. Adapter de sesión

```mermaid
classDiagram
  direction TB
  class Usuario {
    +int id
    +str nombre
    +Rol rol
    +bool activo
  }
  class UsuarioSesionAdapter {
    +Usuario usuario
    +get_id() str
    +is_active bool
    +is_authenticated bool
    +is_anonymous bool
  }
  class ServicioAutenticacion {
    +autenticar(correo, clave)
    +cargar_sesion(identificador)
  }
  class LoginManager {
    <<FlaskLogin>>
  }
  UsuarioSesionAdapter *-- Usuario
  ServicioAutenticacion ..> UsuarioSesionAdapter : crea después de verificar
  LoginManager ..> UsuarioSesionAdapter : consume contrato de sesión
```

`LoginManager` es una clase real de Flask-Login. El contrato esperado por la biblioteca se cumple por los miembros del adaptador; no se inventa una interfaz abstracta externa.

## 10. Secuencia de creación de reserva

```mermaid
sequenceDiagram
  participant C as Controlador
  participant F as ReservaFacade
  participant S as ServicioReserva
  participant U as UnidadTrabajoSqlite
  participant D as DAO SQLite
  C->>F: crear_reserva(actor, datos, token, cliente)
  F->>S: crear(...)
  S->>U: abrir conexión e iniciar_escritura
  U->>D: BEGIN IMMEDIATE en conexión compartida
  S->>D: releer actor, cliente, restaurante y permisos
  S->>D: buscar_por_token
  alt mismo actor y contenido
    D-->>S: reserva existente
    S->>U: confirmar
  else solicitud nueva
    S->>D: consultar horario, capacidad y solapamientos
    S->>S: DirectorReserva y ReservaBuilder construyen producto
    S->>D: guardar reserva
    D-->>S: reserva con ID
    S->>U: confirmar
  end
  S-->>F: reserva
  F-->>C: resultado
  C-->>C: redirigir al detalle
```

BEGIN, INSERT y COMMIT operan sobre la conexión de la unidad de trabajo. Si falla cualquier paso, su salida revierte y cierra. En el diagrama, la columna DAO representa el acceso SQLite compartido; el dueño de la transacción es UoW, no un DAO. La disponibilidad consultada antes de este flujo no reserva la mesa.
