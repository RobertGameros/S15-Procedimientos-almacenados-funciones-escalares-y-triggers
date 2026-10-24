-- ====================================================================
-- Tarea No. 7: Base de Datos 1
-- Archivo: 04_procedimiento_almacenado.sql
-- Motor: PostgreSQL 18 (Docker Compose)
-- Propósito: Implementación del procedimiento aplicar_ajuste_precio.
-- ====================================================================

/*
=======================================================================
ARQUITECTURA DEL PROCEDIMIENTO ALMACENADO:
=======================================================================
1. Orquestación de Lógica de Negocio:
   Este procedimiento actúa como la capa de servicio u orquestación:
   - Valida la existencia del producto en el catálogo (tabla track).
   - Reutiliza obligatoriamente la función escalar calcular_precio_ajustado
     sin duplicar la fórmula matemática ni sus validaciones.
   - Aplica el cambio únicamente sobre la fila indicada mediante WHERE.

2. Desacoplamiento de la Auditoría:
   El procedimiento NO realiza sentencias INSERT en la tabla auditoria_precios.
   Esta separación de responsabilidades asegura que:
   - Si se actualiza el precio vía CALL, el trigger audita.
   - Si se actualiza el precio vía UPDATE directo, el trigger también audita.
   - Si el procedimiento falla a medio camino, no quedan registros huérfanos.

3. Integridad Transaccional:
   No incluye sentencias COMMIT ni ROLLBACK explícitas, delegando el
   control transaccional al llamador (sesión de usuario, script o DataGrip),
   lo cual permite pruebas de reversión atómica (BEGIN ... ROLLBACK).
=======================================================================
*/

CREATE OR REPLACE PROCEDURE aplicar_ajuste_precio(
    p_id_producto INTEGER, 
    p_porcentaje  NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_precio_actual NUMERIC(10, 2);
    v_precio_nuevo  NUMERIC(10, 2);
BEGIN
    -- 1. Validación de identificador no nulo
    IF p_id_producto IS NULL THEN
        RAISE EXCEPTION 'Parámetro inválido: El identificador del producto no puede ser nulo (NULL).'
            USING ERRCODE = 'check_violation';
    END IF;

    -- 2. Validación defensiva de porcentaje no nulo
    IF p_porcentaje IS NULL THEN
        RAISE EXCEPTION 'Parámetro inválido: El porcentaje de ajuste no puede ser nulo (NULL).'
            USING ERRCODE = 'check_violation';
    END IF;

    -- 3. Verificación de existencia del producto y obtención del precio actual
    SELECT unit_price
    INTO v_precio_actual
    FROM track
    WHERE track_id = p_id_producto;

    -- Si la consulta no devolvió ninguna tupla
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Producto no encontrado: No existe ningún producto o pista con identificador (ID = %).', p_id_producto
            USING ERRCODE = 'data_exception';
    END IF;

    -- 4. Invocación de la función escalar (reutilización obligatoria de lógica pura)
    -- Si el porcentaje está fuera de [-50, 100], la función escalar lanza la excepción
    -- y aborta la ejecución antes de modificar la base de datos.
    v_precio_nuevo := calcular_precio_ajustado(v_precio_actual, p_porcentaje);

    -- 5. Actualización exclusiva del registro correspondiente
    UPDATE track
    SET unit_price = v_precio_nuevo
    WHERE track_id = p_id_producto;

    -- 6. Notificación informativa en la consola de resultados
    RAISE NOTICE 'Ajuste completado para Producto/Track ID %: Precio previo = %, Precio nuevo = % (Ajuste: % %%)',
        p_id_producto, v_precio_actual, v_precio_nuevo, p_porcentaje;
END;
$$;

COMMENT ON PROCEDURE aplicar_ajuste_precio(INTEGER, NUMERIC)
IS 'Procedimiento orquestador que valida el producto, calcula el nuevo precio con la función escalar y ejecuta el UPDATE sin intervenir en la auditoría.';

