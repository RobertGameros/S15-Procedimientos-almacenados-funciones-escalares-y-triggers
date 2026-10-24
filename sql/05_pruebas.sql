-- ====================================================================
-- Tarea No. 7: Base de Datos 1
-- Archivo: 05_casos_prueba.sql
-- Motor: PostgreSQL 18 (Docker Compose)
-- Cliente recomendado: JetBrains DataGrip
-- Propósito: Batería completa de pruebas de los 8 Casos Evaluables.
-- ====================================================================

/*
=======================================================================
GUÍA DE EJECUCIÓN EN DATAGRIP:
=======================================================================
- Para tomar las capturas del PDF, seleccione con el cursor la sentencia 
  correspondiente a cada caso y presione Ctrl + Enter (o Cmd + Enter).
- Los Casos 2, 4 y 5 generan errores controlados por diseño de la base 
  de datos. DataGrip mostrará el panel inferior de salida/errores en rojo 
  con el mensaje exacto generado por RAISE EXCEPTION.
- Al final de cada caso con error se incluye un bloque anónimo DO $$ opcional
  por si prefiere ejecutar todo el script de forma secuencial sin detención.
=======================================================================
*/

-- ====================================================================
-- FASE 0: PREPARACIÓN Y ESTABLECIMIENTO DE ESTADO BASE
-- ====================================================================
-- Reiniciamos la tabla de auditoría para iniciar las pruebas desde cero
TRUNCATE TABLE auditoria_precios RESTART IDENTITY;

-- Establecemos precios base fáciles de verificar mentalmente en las pistas testigo
UPDATE track SET unit_price = 10.00 WHERE track_id = 1;
UPDATE track SET unit_price = 25.00 WHERE track_id = 2;
UPDATE track SET unit_price = 50.00 WHERE track_id = 3;

-- Vaciamos nuevamente la auditoría para descartar los registros de la inicialización
TRUNCATE TABLE auditoria_precios RESTART IDENTITY;

-- Verificación de estado base:
SELECT track_id, name, unit_price FROM track WHERE track_id IN (1, 2, 3) ORDER BY track_id;
SELECT COUNT(*) AS total_auditoria_inicial FROM auditoria_precios;


-- ====================================================================
-- CASO 1: FUNCIÓN ESCALAR - AUMENTO (+10%) Y REDUCCIÓN (-50%)
-- Propósito: Validar que el cálculo matemático redondea a 2 decimales 
--            y admite tanto aumentos (+10%) como el límite de reducción (-50%).
-- Datos de prueba: precio = 10.00, porcentaje = 10.00 | porcentaje = -50.00
-- Resultado esperado: 11.00 y 5.00 respectivamente.
-- ====================================================================

-- Sentencia para captura en DataGrip:
SELECT 
    calcular_precio_ajustado(10.00, 10.00)  AS aumento,
    calcular_precio_ajustado(10.00, -50.00) AS reduccion;


-- ====================================================================
-- CASO 2: FUNCIÓN ESCALAR - VALIDACIÓN DE ENTRADAS INVÁLIDAS
-- Propósito: Demostrar que la función rechaza de forma estricta:
--            - Parámetros NULL (precio o porcentaje)
--            - Precios base menores o iguales a cero
--            - Porcentajes fuera del rango admisible [-50, 100]
-- Ejecutar cada línea de forma individual en DataGrip para su captura:
-- ====================================================================

-- 2.1: Rechazo de precio actual NULL
-- Error esperado: check_violation -> El precio actual no puede ser nulo (NULL)
SELECT calcular_precio_ajustado(NULL, 10);

-- 2.2: Rechazo de porcentaje NULL
-- Error esperado: check_violation -> El porcentaje de ajuste no puede ser nulo (NULL)
SELECT calcular_precio_ajustado(10.00, NULL);

-- 2.3: Rechazo de precio actual igual a cero (0)
-- Error esperado: numeric_value_out_of_range -> debe ser estrictamente mayor que cero
SELECT calcular_precio_ajustado(0, 10);

-- 2.4: Rechazo de precio actual negativo (-5)
-- Error esperado: numeric_value_out_of_range -> debe ser estrictamente mayor que cero
SELECT calcular_precio_ajustado(-5.00, 10);

-- 2.5: Rechazo de porcentaje menor a -50% (-60%)
-- Error esperado: numeric_value_out_of_range -> fuera del rango admitido [-50, 100]
SELECT calcular_precio_ajustado(10.00, -60);

-- 2.6: Rechazo de porcentaje mayor a 100% (150%)
-- Error esperado: numeric_value_out_of_range -> fuera del rango admitido [-50, 100]
SELECT calcular_precio_ajustado(10.00, 150);


-- ====================================================================
-- CASO 3: PROCEDIMIENTO ALMACENADO - CAMBIO VÁLIDO CON CALL
-- Propósito: Actualizar un producto existente (Track ID = 1) aumentando su 
--            precio en +20%. Verificar que el producto 1 cambia, el producto 2 
--            permanece intacto y el trigger inserta la auditoría automáticamente.
-- Datos de prueba: ID = 1 (precio actual 10.00), Porcentaje = 20.00%
-- Resultado esperado: Precio final = 12.00. Registro generado en auditoria_precios.
-- ====================================================================

-- Paso 3.1: Estado inicial del catálogo antes de la ejecución
SELECT track_id, name, unit_price FROM track WHERE track_id IN (1, 2) ORDER BY track_id;

-- Paso 3.2: Invocación del procedimiento almacenado
CALL aplicar_ajuste_precio(1, 20.00);

-- Paso 3.3: Estado posterior del catálogo (solo Track 1 cambió de 10.00 a 12.00)
SELECT track_id, name, unit_price FROM track WHERE track_id IN (1, 2) ORDER BY track_id;

-- Paso 3.4: Verificación de la fila generada de forma autónoma en auditoría
SELECT id_auditoria, id_producto, precio_anterior, precio_nuevo, fecha_cambio, usuario_bd
FROM auditoria_precios
WHERE id_producto = 1;


-- ====================================================================
-- CASO 4: PROCEDIMIENTO ALMACENADO - IDENTIFICADOR INEXISTENTE
-- Propósito: Invocar el procedimiento con un ID que no existe en el catálogo.
--            Comprobar que lanza excepción y que no se altera ninguna tabla.
-- Datos de prueba: ID = 999999, Porcentaje = 10.00%
-- ====================================================================

-- Ejecutar la siguiente línea en DataGrip:
-- Error esperado: data_exception -> No existe ningún producto o pista con identificador (ID = 999999)
CALL aplicar_ajuste_precio(999999, 10.00);

-- Verificación de integridad: El catálogo y la auditoría permanecen sin alteraciones
SELECT track_id, name, unit_price FROM track WHERE track_id IN (1, 2) ORDER BY track_id;
SELECT * FROM auditoria_precios WHERE id_producto = 999999;


-- ====================================================================
-- CASO 5: PROCEDIMIENTO ALMACENADO - PORCENTAJE INVÁLIDO
-- Propósito: Invocar el procedimiento con porcentaje fuera de rango (ej. 120%).
--            Verificar que la excepción de la función escalar se propaga y
--            aborta el procedimiento sin aplicar cambios parciales.
-- Datos de prueba: ID = 1, Porcentaje = 120.00%
-- ====================================================================

-- Estado previo de Track 1
SELECT track_id, name, unit_price FROM track WHERE track_id = 1;

-- Ejecutar en DataGrip:
-- Error esperado: numeric_value_out_of_range -> porcentaje (120) está fuera del rango admitido [-50, 100]
CALL aplicar_ajuste_precio(1, 120.00);

-- Verificación de ausencia de cambios parciales tras el error
SELECT track_id, name, unit_price FROM track WHERE track_id = 1;


-- ====================================================================
-- CASO 6: DISPARADOR (TRIGGER) - ACTUALIZACIÓN DIRECTA VÍA UPDATE
-- Propósito: Demostrar que el trigger AFTER UPDATE es autónomo e ineludible:
--            un UPDATE SQL directo sin usar CALL también registra la auditoría.
-- Datos de prueba: Track ID = 2 modificado directamente a 30.00 (valor previo: 25.00).
-- ====================================================================

-- Paso 6.1: Estado previo del Producto 2
SELECT track_id, name, unit_price FROM track WHERE track_id = 2;

-- Paso 6.2: Sentencia UPDATE directa sobre el catálogo
UPDATE track 
SET unit_price = 30.00 
WHERE track_id = 2;

-- Paso 6.3: Verificación de la fila de auditoría generada por el UPDATE directo
SELECT id_auditoria, id_producto, precio_anterior, precio_nuevo, fecha_cambio, usuario_bd
FROM auditoria_precios
WHERE id_producto = 2
ORDER BY id_auditoria DESC
LIMIT 1;


-- ====================================================================
-- CASO 7: DISPARADOR (TRIGGER) - PRECIO SIN CAMBIO EFECTIVO (MISMO VALOR)
-- Propósito: Ejecutar un UPDATE asignando el mismo precio que ya posee el producto.
--            Demostrar que gracias a la condición IS DISTINCT FROM, el trigger
--            NO inserta ninguna fila redundante en la tabla de auditoría.
-- Datos de prueba: Track ID = 2 actualizado a 30.00 (su precio actual).
-- ====================================================================

-- Paso 7.1: Conteo de registros en auditoría antes del UPDATE
SELECT COUNT(*) AS total_auditoria_antes FROM auditoria_precios;

-- Paso 7.2: Ejecución del UPDATE con el mismo precio actual
UPDATE track 
SET unit_price = 30.00 
WHERE track_id = 2;

-- Paso 7.3: Conteo de registros en auditoría después del UPDATE
-- Demuestra que el conteo es IDÉNTICO y no hubo incremento
SELECT COUNT(*) AS total_auditoria_despues FROM auditoria_precios;


-- ====================================================================
-- CASO 8: INTEGRIDAD TRANSACCIONAL - CONTROL CON BEGIN Y ROLLBACK
-- Propósito: Demostrar la atomicidad e integridad transaccional del motor:
--            si se abre una transacción explícita (BEGIN), se ejecuta el 
--            procedimiento y luego se emite ROLLBACK, tanto la actualización 
--            del precio como el registro generado por el trigger se revierten.
-- Datos de prueba: Track ID = 3 (precio inicial 50.00), ajuste de +15% (nuevo: 57.50).
-- ====================================================================

-- Paso 8.1: Estado previo de Track 3
SELECT track_id, name, unit_price FROM track WHERE track_id = 3;

-- Paso 8.2: Inicio de la transacción explícita
BEGIN;

-- Paso 8.3: Ejecución del ajuste de precio dentro de la transacción
CALL aplicar_ajuste_precio(3, 15.00);

-- Paso 8.4: Consultas dentro de la transacción activa (visibles en la sesión)
-- El precio muestra 57.50 y la auditoría contiene la fila correspondiente
SELECT track_id, name, unit_price FROM track WHERE track_id = 3;
SELECT * FROM auditoria_precios WHERE id_producto = 3;

-- Paso 8.5: Reversión total de la transacción
ROLLBACK;

-- Paso 8.6: Comprobación posterior al ROLLBACK
-- El precio de Track 3 regresó a su valor original (50.00)
-- y la fila de auditoría para el producto 3 fue descartada por completo
SELECT track_id, name, unit_price FROM track WHERE track_id = 3;
SELECT * FROM auditoria_precios WHERE id_producto = 3;
