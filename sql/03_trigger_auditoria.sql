-- ====================================================================
-- Tarea No. 7: Base de Datos 1
-- Archivo: 03_trigger_auditoria.sql
-- Motor: PostgreSQL 18 (Docker Compose)
-- Propósito: Implementación de la función trigger y el disparador
--            AFTER UPDATE para auditoría automática e ineludible.
-- ====================================================================

/*
=======================================================================
ARQUITECTURA DEL DISPARADOR (TRIGGER):
=======================================================================
1. Ejecución Autónoma:
   El trigger opera en la capa del motor de base de datos de manera 
   automática ante cualquier sentencia UPDATE que modifique la columna 
   unit_price de la tabla track, ya sea originada por el procedimiento 
   almacenado aplicar_ajuste_precio o mediante consultas UPDATE directas.

2. Filtro Anti-Redundancia (IS DISTINCT FROM):
   Evalúa la condición "OLD.unit_price IS DISTINCT FROM NEW.unit_price".
   Si una actualización asigna exactamente el mismo precio que ya existía,
   la condición evalúa a FALSO y el trigger NO genera ninguna fila en 
   auditoria_precios, preservando la eficiencia y limpieza del histórico.

3. Trazabilidad Completa:
   Registra el identificador del producto (track_id), el precio anterior 
   (OLD), el nuevo precio (NEW), la estampa de tiempo actual del servidor 
   (CURRENT_TIMESTAMP) y el usuario de base de datos autenticado 
   (CURRENT_USER).
=======================================================================
*/

-- 1. Función de soporte para el disparador
CREATE OR REPLACE FUNCTION fn_auditar_cambio_precio()
RETURNS TRIGGER 
LANGUAGE plpgsql
AS $$
BEGIN
    -- Se intercepta únicamente si el precio realmente cambió
    IF OLD.unit_price IS DISTINCT FROM NEW.unit_price THEN
        INSERT INTO auditoria_precios (
            id_producto,
            precio_anterior,
            precio_nuevo,
            fecha_cambio,
            usuario_bd
        ) VALUES (
            OLD.track_id,
            OLD.unit_price,
            NEW.unit_price,
            CURRENT_TIMESTAMP,
            CURRENT_USER
        );
    END IF;

    -- En triggers AFTER UPDATE de fila, se retorna NEW
    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION fn_auditar_cambio_precio()
IS 'Función de disparo que evalúa diferencias de precio e inserta el registro histórico en auditoria_precios.';

-- 2. Eliminación previa del trigger para garantizar idempotencia
DROP TRIGGER IF EXISTS trg_auditar_cambio_precio ON track;

-- 3. Creación del disparador AFTER UPDATE FOR EACH ROW sobre la tabla del catálogo
CREATE TRIGGER trg_auditar_cambio_precio
AFTER UPDATE OF unit_price ON track
FOR EACH ROW
EXECUTE FUNCTION fn_auditar_cambio_precio();

COMMENT ON TRIGGER trg_auditar_cambio_precio ON track
IS 'Disparador que audita automáticamente cualquier cambio efectivo en unit_price.';
