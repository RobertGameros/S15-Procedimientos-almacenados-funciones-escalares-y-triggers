-- ====================================================================
-- Tarea No. 7: Base de Datos 1
-- Archivo: 02_funcion_escalar.sql
-- Motor: PostgreSQL 18 (Docker Compose)
-- Propósito: Definición de la función escalar calcular_precio_ajustado.
-- ====================================================================

/*
=======================================================================
JUSTIFICACIÓN TEÓRICA DE LA FUNCIÓN ESCALAR:
=======================================================================
1. Naturaleza Escalar:
   Esta función es ESCALAR porque acepta parámetros escalares de entrada 
   y devuelve un único valor atómico de tipo NUMERIC por cada invocación.
   A diferencia de las funciones tabulares (SETOF o RETURNS TABLE), no 
   retorna colecciones de filas ni estructuras complejas, lo que permite 
   integrarla directamente en cualquier expresión de consulta SQL 
   (cláusulas SELECT, WHERE, HAVING), expresiones UPDATE o asignaciones 
   de variables dentro de bloques y procedimientos PL/pgSQL.

2. Pureza y Determinismo (Inmutabilidad):
   La función está marcada como IMMUTABLE porque, para un mismo par de 
   argumentos (precio_actual, porcentaje), garantiza que siempre devolverá 
   exactamente el mismo resultado matemático sin depender de datos de 
   configuración o estados mutables de la base de datos.

3. Ausencia de Efectos Secundarios:
   Cumple con el principio de responsabilidad única al NO realizar 
   operaciones de modificación de datos (DML: INSERT, UPDATE, DELETE) ni 
   consultar tablas del catálogo. Se enfoca exclusivamente en la 
   validación de reglas de negocio de cálculo y el redondeo financiero a 
   2 decimales.
=======================================================================
*/

CREATE OR REPLACE FUNCTION calcular_precio_ajustado(
    precio_actual NUMERIC, 
    porcentaje    NUMERIC
)
RETURNS NUMERIC AS $$
DECLARE
    v_precio_calculado NUMERIC(12, 4);
    v_precio_final     NUMERIC(10, 2);
BEGIN
    -- 1. Validación contra valores nulos (NULL)
    IF precio_actual IS NULL THEN
        RAISE EXCEPTION 'Parámetro inválido: El precio actual no puede ser nulo (NULL).'
            USING ERRCODE = 'check_violation';
    END IF;

    IF porcentaje IS NULL THEN
        RAISE EXCEPTION 'Parámetro inválido: El porcentaje de ajuste no puede ser nulo (NULL).'
            USING ERRCODE = 'check_violation';
    END IF;

    -- 2. Validación de precio base estrictamente positivo
    IF precio_actual <= 0 THEN
        RAISE EXCEPTION 'Valor fuera de rango: El precio actual (%) debe ser estrictamente mayor que cero.', precio_actual
            USING ERRCODE = 'numeric_value_out_of_range';
    END IF;

    -- 3. Validación del rango permitido de ajuste [-50, 100]
    -- Se admiten explícitamente los extremos exactos: -50% y +100%
    IF porcentaje < -50 OR porcentaje > 100 THEN
        RAISE EXCEPTION 'Porcentaje no permitido: El porcentaje (%) está fuera del rango admitido [-50, 100].', porcentaje
            USING ERRCODE = 'numeric_value_out_of_range';
    END IF;

    -- 4. Cálculo matemático del nuevo precio
    v_precio_calculado := precio_actual * (1.0 + (porcentaje / 100.0));

    -- 5. Redondeo financiero estricto a 2 decimales
    v_precio_final := ROUND(v_precio_calculado, 2);

    -- 6. Verificación de que el valor resultante final sea estrictamente mayor a 0
    IF v_precio_final <= 0 THEN
        RAISE EXCEPTION 'Resultado inválido: El precio ajustado resultante (%), redondeado a dos decimales, debe ser mayor a cero.', v_precio_final
            USING ERRCODE = 'check_violation';
    END IF;

    -- 7. Retorno del valor escalar
    RETURN v_precio_final;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION calcular_precio_ajustado(NUMERIC, NUMERIC)
IS 'Función escalar pura que calcula el nuevo precio derivado con redondeo a 2 decimales dentro del rango [-50, 100].';
