-- Se ejecuta explícitamente con init-db. Nunca se borra la base al arrancar.
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS usuario (
 id INTEGER PRIMARY KEY,
 nombre TEXT NOT NULL CHECK(length(trim(nombre)) > 0),
 correo TEXT NOT NULL UNIQUE CHECK(correo = lower(trim(correo))),
 hash_clave TEXT NOT NULL,
 rol TEXT NOT NULL CHECK(rol IN ('CLIENTE','ADMINISTRADOR')),
 activo INTEGER NOT NULL DEFAULT 1 CHECK(activo IN (0,1))
);
CREATE TABLE IF NOT EXISTS restaurante (
 id INTEGER PRIMARY KEY,
 nombre TEXT NOT NULL,
 ciudad TEXT NOT NULL,
 direccion TEXT NOT NULL,
 activo INTEGER NOT NULL DEFAULT 1 CHECK(activo IN (0,1))
);
CREATE TABLE IF NOT EXISTS administrador_restaurante (
 usuario_id INTEGER NOT NULL REFERENCES usuario(id) ON DELETE RESTRICT,
 restaurante_id INTEGER NOT NULL REFERENCES restaurante(id) ON DELETE RESTRICT,
 PRIMARY KEY(usuario_id, restaurante_id)
);
CREATE TABLE IF NOT EXISTS mesa (
 id INTEGER PRIMARY KEY,
 restaurante_id INTEGER NOT NULL REFERENCES restaurante(id) ON DELETE RESTRICT,
 numero TEXT NOT NULL CHECK(length(trim(numero)) BETWEEN 1 AND 20),
 capacidad INTEGER NOT NULL CHECK(typeof(capacidad) = 'integer' AND capacidad > 0),
 activa INTEGER NOT NULL DEFAULT 1 CHECK(activa IN (0,1)),
 UNIQUE(restaurante_id, numero)
);
CREATE TABLE IF NOT EXISTS horario_atencion (
 id INTEGER PRIMARY KEY,
 restaurante_id INTEGER NOT NULL REFERENCES restaurante(id) ON DELETE RESTRICT,
 dia_semana INTEGER NOT NULL CHECK(dia_semana BETWEEN 1 AND 7),
 apertura TEXT NOT NULL CHECK(apertura GLOB '[0-2][0-9]:[0-5][0-9]' AND apertura < '24:00'),
 cierre TEXT NOT NULL CHECK(cierre GLOB '[0-2][0-9]:[0-5][0-9]' AND cierre < '24:00'),
 CHECK(cierre > apertura)
);
CREATE TABLE IF NOT EXISTS reserva (
 id INTEGER PRIMARY KEY,
 cliente_id INTEGER NOT NULL REFERENCES usuario(id) ON DELETE RESTRICT,
 creado_por_id INTEGER NOT NULL REFERENCES usuario(id) ON DELETE RESTRICT,
 mesa_id INTEGER NOT NULL REFERENCES mesa(id) ON DELETE RESTRICT,
 inicio TEXT NOT NULL,
 fin TEXT NOT NULL CHECK(fin > inicio),
 personas INTEGER NOT NULL CHECK(typeof(personas) = 'integer' AND personas > 0),
 observaciones TEXT NOT NULL DEFAULT '' CHECK(length(observaciones) <= 500),
 estado TEXT NOT NULL CHECK(estado IN ('CONFIRMADA','CANCELADA')),
 fecha_creacion TEXT NOT NULL,
 token_operacion TEXT NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_reserva_mesa_intervalo ON reserva(mesa_id, estado, inicio, fin);
CREATE INDEX IF NOT EXISTS idx_reserva_cliente_inicio ON reserva(cliente_id, inicio);
CREATE INDEX IF NOT EXISTS idx_horario_dia ON horario_atencion(restaurante_id, dia_semana);
CREATE INDEX IF NOT EXISTS idx_mesa_restaurante ON mesa(restaurante_id);
CREATE TRIGGER IF NOT EXISTS reserva_sin_solapamiento_insert
BEFORE INSERT ON reserva WHEN NEW.estado = 'CONFIRMADA'
BEGIN
 SELECT RAISE(ABORT, 'reserva_solapada') WHERE EXISTS (
  SELECT 1 FROM reserva r WHERE r.mesa_id=NEW.mesa_id AND r.estado='CONFIRMADA'
  AND NEW.inicio < r.fin AND NEW.fin > r.inicio
 );
END;
CREATE TRIGGER IF NOT EXISTS reserva_sin_solapamiento_update
BEFORE UPDATE ON reserva WHEN NEW.estado = 'CONFIRMADA'
BEGIN
 SELECT RAISE(ABORT, 'reserva_solapada') WHERE EXISTS (
  SELECT 1 FROM reserva r WHERE r.id != NEW.id AND r.mesa_id=NEW.mesa_id
  AND r.estado='CONFIRMADA' AND NEW.inicio < r.fin AND NEW.fin > r.inicio
 );
END;
PRAGMA user_version = 1;
