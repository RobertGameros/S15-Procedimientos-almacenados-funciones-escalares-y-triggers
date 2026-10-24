-- ====================================================================
-- Tarea No. 7: Base de Datos 1
-- Archivo: 01_esquema_y_datos.sql
-- Motor: PostgreSQL 18 (Docker Compose)
-- Propósito: Verificación del catálogo Chinook (tabla track),
--            creación de la tabla de auditoría (auditoria_precios)
--            y vista de compatibilidad (productos).
-- ====================================================================

-- 1. Documentar versión del motor PostgreSQL
SELECT version() AS version_postgresql;

-- 2. Asegurar existencia de la tabla del catálogo (track de Chinook)
-- Si ya ejecutó chinook/00_chinook_carga_datagrip.sql, la tabla ya existirá con 3,503 filas.
-- Si ejecuta este script en una base limpia, se crea la estructura base con datos semilla.
CREATE TABLE IF NOT EXISTS track (
    track_id      INT NOT NULL,
    name          VARCHAR(200) NOT NULL,
    album_id      INT,
    media_type_id INT DEFAULT 1,
    genre_id      INT DEFAULT 1,
    composer      VARCHAR(220),
    milliseconds  INT DEFAULT 250000,
    bytes         INT DEFAULT 5000000,
    unit_price    NUMERIC(10, 2) NOT NULL CHECK (unit_price > 0),
    CONSTRAINT track_pkey PRIMARY KEY (track_id)
);

-- Inserción de pistas semilla en caso de que la tabla esté vacía
INSERT INTO track (track_id, name, composer, milliseconds, bytes, unit_price)
VALUES 
    (1, 'For Those About To Rock (We Salute You)', 'Angus Young, Malcolm Young, Brian Johnson', 343719, 11170334, 0.99),
    (2, 'Balls to the Wall', 'U. Dirkschneider, W. Hoffmann, H. Frank', 342562, 5510424, 0.99),
    (3, 'Fast As a Shark', 'F. Baltes, S. Kaufman, U. Dirkscneider', 230619, 3990994, 0.99)
ON CONFLICT (track_id) DO NOTHING;

-- 3. Creación de la tabla de auditoría (auditoria_precios)
-- Cumple estrictamente con las especificaciones de la rúbrica y el enunciado
DROP TABLE IF EXISTS auditoria_precios CASCADE;

CREATE TABLE auditoria_precios (
    id_auditoria     SERIAL PRIMARY KEY,
    id_producto      INTEGER NOT NULL,
    precio_anterior  NUMERIC(10, 2) NOT NULL,
    precio_nuevo     NUMERIC(10, 2) NOT NULL,
    fecha_cambio     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    usuario_bd       TEXT NOT NULL DEFAULT CURRENT_USER
);

COMMENT ON TABLE auditoria_precios IS 'Almacén de trazabilidad histórica inmutable para modificaciones de precios';
COMMENT ON COLUMN auditoria_precios.id_auditoria IS 'Clave primaria autoincrementable del registro de auditoría';
COMMENT ON COLUMN auditoria_precios.id_producto IS 'Identificador del producto/pista afectado (track_id)';
COMMENT ON COLUMN auditoria_precios.precio_anterior IS 'Valor histórico del precio antes de la modificación (OLD)';
COMMENT ON COLUMN auditoria_precios.precio_nuevo IS 'Nuevo valor asignado al precio tras la modificación (NEW)';
COMMENT ON COLUMN auditoria_precios.fecha_cambio IS 'Marca temporal de la ejecución de la actualización';
COMMENT ON COLUMN auditoria_precios.usuario_bd IS 'Usuario de base de datos que ejecutó la instrucción';

-- 4. Vista de compatibilidad y desacoplamiento (productos)
-- Permite consultar o manipular el catálogo utilizando tanto la terminología estándar
-- (productos / id_producto / precio_actual) como la de Chinook (track / track_id / unit_price)
CREATE OR REPLACE VIEW productos AS
SELECT 
    track_id   AS id_producto,
    name       AS nombre,
    unit_price AS precio_actual
FROM track;

-- 5. Verificación de estado inicial
SELECT track_id, name, unit_price 
FROM track 
WHERE track_id IN (1, 2, 3)
ORDER BY track_id;

SELECT * FROM auditoria_precios;
