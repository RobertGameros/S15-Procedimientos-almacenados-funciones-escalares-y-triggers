# Tarea No. 7: Lógica de Negocio y Trazabilidad en PostgreSQL
**Curso:** Base de Datos 1  
**Estudiante:** Robert Gameros  
**Año Lectivo:** 2026  
**Repositorio Oficial en GitHub:** [https://github.com/RobertGameros/S15-Procedimientos-almacenados-funciones-escalares-y-triggers.git](https://github.com/RobertGameros/S15-Procedimientos-almacenados-funciones-escalares-y-triggers.git)  
**Informe Completo de Evidencias (PDF):** [📄 Descargar Informe_Tarea7_Robert_Gameros.pdf](Informe_Tarea7_Robert_Gameros.pdf)  
**Motor de Base de Datos:** PostgreSQL 18.6 (Desplegado con Docker Compose)  
**Entorno de Trabajo y Cliente SQL:** JetBrains DataGrip  
**Base de Datos Base:** [Chinook Database](https://github.com/lerocha/chinook-database) (Script fuente: `Chinook_PostgreSql.sql`)  

---

## 1. Resumen Ejecutivo y Ecosistema de Herramientas

El objetivo de esta práctica es implementar y verificar una arquitectura desacoplada y robusta de **lógica de negocio y auditoría automática** dentro del motor de base de datos PostgreSQL, garantizando la trazabilidad histórica inmutable de los precios de productos/pistas del catálogo.

| Categoría | Herramienta | Versión / Detalle Técnico | Propósito en el Proyecto |
| :--- | :--- | :--- | :--- |
| **Motor de Base de Datos** | **Docker + Docker Compose** | `postgres:18-alpine` (PostgreSQL 18.6) | Instancia limpia, aislada y reproducible sin conflictos locales. |
| **Cliente y Entorno SQL** | **JetBrains DataGrip** | PostgreSQL JDBC Driver | Administración, compilación de PL/pgSQL, transacciones manuales (`BEGIN`/`ROLLBACK`) y toma de capturas. |
| **Control de Versiones** | **Git & GitHub** | Repositorio público | Alojamiento de scripts SQL, historial de cambios e instrucciones de despliegue. |
| **Catálogo Base** | **Chinook Database** | Repositorio oficial de Luis Rocha | Catálogo musical (`track`), clave primaria `track_id`, precio unitario `unit_price`. |

---

## 2. Parámetros de Conexión (Docker Compose)

El entorno se encuentra preconfigurado en el archivo `docker-compose.yml` con variables de entorno genéricas de desarrollo local (sin exponer secretos ni credenciales privadas):

- **Host:** `localhost` (o `127.0.0.1`)
- **Puerto:** `5432`
- **Usuario:** `ROBERT`
- **Contraseña:** `ROBERT1710`
- **Base de Datos Principal:** `chinook`

### Pasos para iniciar el servicio en Docker:
```bash
# 1. Situarse en la carpeta raíz del proyecto
cd "c:\Users\barri\Documents\TAREAS DE LA UNIVERSIDAD\AÑO 2026\VI CICLO 2026\Base de Datos 1\Tarea No.7 de Base de Datos 1"

# 2. Levantar el contenedor en segundo plano
docker compose up -d

# 3. Comprobar que el contenedor está activo y saludable
docker ps
```

### Conexión manual en DataGrip:
1. Abrir **JetBrains DataGrip**.
2. En la ventana **Database Explorer**, hacer clic en `+` > **Data Source** > **PostgreSQL**.
3. Configurar:
   - **Host:** `localhost`
   - **Port:** `5432`
   - **User:** `ROBERT`
   - **Password:** `ROBERT1710`
   - **Database:** `chinook`
4. Presionar **Test Connection** (PostgreSQL ver. 18.6) y guardar.

---

## 3. Preparación del Catálogo Chinook

En la carpeta `chinook/` se incluye la copia completa del repositorio oficial:
- **Fuente Oficial:** [https://github.com/lerocha/chinook-database](https://github.com/lerocha/chinook-database)
- **Archivo de Importación Original:** `chinook/Chinook_PostgreSql.sql`
- **Archivo Adaptado para DataGrip:** `chinook/00_chinook_carga_datagrip.sql` (elimina `DROP DATABASE` y `\c` para ejecutarse directamente sobre la conexión activa sin abortar).

> **Nota de compatibilidad:** El script `01_esquema_y_datos.sql` (y `sql/01_preparacion.sql`) detecta automáticamente la existencia de la tabla `track`. Si se ejecuta de forma autónoma sin cargar todo Chinook, crea la estructura requerida con datos semilla (`track_id` 1, 2 y 3) para garantizar máxima reproducibilidad.

---

## 4. Estructura de Archivos y Secuencia de Ejecución

Para asegurar la reproducibilidad y el orden de dependencias estricto exigido por la rúbrica:

```text
├── docker-compose.yml                # Configuración del servicio PostgreSQL 18
├── chinook/                          # Catálogo oficial Chinook Database
│   ├── 00_chinook_carga_datagrip.sql
│   ├── Chinook_PostgreSql.sql
│   └── ChinookDatabase/
├── sql/                              # Carpeta oficial de scripts para entrega
│   ├── 01_preparacion.sql            # Creación de tablas, auditoría y datos semilla
│   ├── 02_funcion_escalar.sql        # Función matemática pura calcular_precio_ajustado
│   ├── 03_procedimiento.sql          # Procedimiento orquestador aplicar_ajuste_precio
│   ├── 04_trigger_y_funcion.sql      # Disparador trg_auditar_cambio_precio y función
│   └── 05_pruebas.sql                # Batería de los 8 casos de prueba evaluables
├── 01_esquema_y_datos.sql            # Script raíz equivalente
├── 02_funcion_escalar.sql            # Script raíz equivalente
├── 03_trigger_auditoria.sql          # Script raíz equivalente
├── 04_procedimiento_almacenado.sql   # Script raíz equivalente
├── 05_casos_prueba.sql               # Script raíz equivalente
├── Capturas/                         # Evidencias visuales de DataGrip por consulta
│   ├── Consulta1/                    # Preparación y verificación inicial
│   ├── Consulta2/                    # Función escalar
│   ├── Consulta3/                    # Trigger y función de soporte
│   ├── Consulta4/                    # Procedimiento almacenado
│   └── Consulta5/                    # Los 8 casos de prueba
└── README.md                         # Documentación técnica completa
```

### Orden Obligatorio de Ejecución:

1. **`01_preparacion.sql`** (o `01_esquema_y_datos.sql`): Documenta la versión de PostgreSQL (`SELECT version();`), crea/verifica la tabla `track`, crea la tabla `auditoria_precios` y define la vista `productos`.
2. **`02_funcion_escalar.sql`**: Compila la función escalar pura `calcular_precio_ajustado`.
3. **`04_trigger_y_funcion.sql`** (o `03_trigger_auditoria.sql`): Compila la función de soporte `fn_auditar_cambio_precio()` y asocia el trigger `trg_auditar_cambio_precio` a `track`. **Se compila antes del procedimiento para que cualquier modificación posterior sea auditada de forma automática.**
4. **`03_procedimiento.sql`** (o `04_procedimiento_almacenado.sql`): Compila el procedimiento `aplicar_ajuste_precio` que orquesta la lógica, valida el producto y reutiliza la función escalar.
5. **`05_pruebas.sql`** (o `05_casos_prueba.sql`): Ejecuta los 8 casos evaluables para obtener las evidencias.

---

## 5. Tabla de Objetos Implementados

| Objeto | Tipo | Parámetros | Retorno / Efecto | Responsabilidad Principal |
| :--- | :--- | :--- | :--- | :--- |
| `calcular_precio_ajustado` | Función Escalar (PL/pgSQL `IMMUTABLE`) | `precio_actual numeric, porcentaje numeric` | `numeric` (escalar a 2 decimales) | Cómputo matemático puro: valida que ningún parámetro sea `NULL`, `precio_actual > 0`, `porcentaje BETWEEN -50 AND 100`, redondea a 2 decimales y valida resultado `> 0`. Cero I/O, sin efectos secundarios en tablas. |
| `aplicar_ajuste_precio` | Procedimiento Almacenado (`CREATE PROCEDURE`) | `p_id_producto integer, p_porcentaje numeric` | `VOID` (`UPDATE` sobre `track`) | Orquestación de negocio: valida identificador, consulta y verifica existencia del producto (`IF NOT FOUND`), **reutiliza la función escalar** y actualiza el registro sin insertar en auditoría ni forzar transacciones. |
| `fn_auditar_cambio_precio` | Función Trigger (PL/pgSQL) | Ninguno | `TRIGGER` | Función de soporte que evalúa `IF OLD.unit_price IS DISTINCT FROM NEW.unit_price THEN` e inserta la tupla histórica en `auditoria_precios`. |
| `trg_auditar_cambio_precio` | Disparador a Nivel de Fila (`AFTER UPDATE`) | Evento: `AFTER UPDATE OF unit_price ON track` | Dispara `fn_auditar_cambio_precio()` | Garantiza la trazabilidad automática e ineludible ante cualquier modificación de precio, sea mediante `CALL` o por sentencia `UPDATE` directa. |
| `auditoria_precios` | Tabla de Auditoría | N/A | Almacén histórico inmutable | Registra: `id_auditoria`, `id_producto`, `precio_anterior`, `precio_nuevo`, `fecha_cambio` (`CURRENT_TIMESTAMP`) y `usuario_bd` (`CURRENT_USER`). |

---

## 6. Fundamentación Teórica y Arquitectónica

### 6.1. Justificación de la Función Escalar
- **Retorno Atómico:** Devuelve un único valor escalar primitivo (`NUMERIC`) por invocación, y no un conjunto de registros (`SETOF` o `TABLE`). Esto permite integrarla directamente en sentencias `SELECT`, cláusulas `WHERE`, expresiones `UPDATE` o asignaciones directas en PL/pgSQL.
- **Inmutabilidad y Determinismo:** Definida como `IMMUTABLE`. Para los mismos argumentos, siempre devuelve el mismo resultado sin depender de configuraciones o estados externos del catálogo.
- **Responsabilidad Única:** No ejecuta sentencias DML (`INSERT`, `UPDATE`, `DELETE`) ni consulta tablas.

### 6.2. Desacoplamiento y Auditoría Ineludible
- El procedimiento almacenado **no contiene sentencias `INSERT` hacia la tabla de auditoría**, separando claramente la capa de actualización de la capa de trazabilidad.
- La auditoría está gobernada por el trigger `AFTER UPDATE`. De esta manera, si un administrador o sistema ejecuta un `UPDATE` directo sin pasar por el procedimiento, la auditoría se dispara de forma infalible.
- El uso de `IS DISTINCT FROM` garantiza que si se ejecuta un `UPDATE` asignando el mismo precio, la condición evalúa a `FALSE` y no se insertan filas basura redundantes.
- El procedimiento no incluye `COMMIT` ni `ROLLBACK`, permitiendo que el invocador controle la transacción de forma atómica (caso demostrado en la prueba con `BEGIN` ... `ROLLBACK`).

---

## 7. Matriz de los 8 Casos de Prueba Evaluables

| Caso | Propósito del Caso | Sentencia SQL a Ejecutar en DataGrip | Resultado Esperado y Observado |
| :---: | :--- | :--- | :--- |
| **1** | Función: Aumento y reducción | `SELECT calcular_precio_ajustado(10.00, 10.00) AS aumento, calcular_precio_ajustado(10.00, -50.00) AS reduccion;` | `aumento: 11.00`, `reduccion: 5.00`. Redondeo exacto a 2 decimales. |
| **2** | Función: Entradas inválidas | Consultas `SELECT` separadas para: `NULL`, precio `<= 0` y porcentaje fuera de `[-50, 100]`. | `RAISE EXCEPTION` con códigos `check_violation` y `numeric_value_out_of_range`. |
| **3** | Procedimiento: Cambio válido | `CALL aplicar_ajuste_precio(1, 20.00);` con `SELECT` antes/después a `track` y `auditoria_precios`. | Producto 1 cambia de 10.00 a 12.00; Producto 2 no cambia; fila generada en `auditoria_precios` con usuario `ROBERT`. |
| **4** | Procedimiento: ID inexistente | `CALL aplicar_ajuste_precio(999999, 10.00);` | Excepción `data_exception` (Producto no encontrado). Precios y auditoría sin alteraciones. |
| **5** | Procedimiento: Porcentaje inválido | `CALL aplicar_ajuste_precio(1, 120.00);` | Excepción `numeric_value_out_of_range` propagada desde la función escalar. Sin cambios parciales. |
| **6** | Trigger: UPDATE directo | `UPDATE track SET unit_price = 30.00 WHERE track_id = 2;` | El trigger intercepta el `UPDATE` e inserta la auditoría sin haber invocado el procedimiento. |
| **7** | Trigger: Precio sin cambio | `UPDATE track SET unit_price = 30.00 WHERE track_id = 2;` (mismo valor). | `COUNT(*)` de `auditoria_precios` no sufre ningún incremento (`IS DISTINCT FROM`). |
| **8** | Integridad transaccional | `BEGIN; CALL aplicar_ajuste_precio(3, 15.00); ... ROLLBACK;` | Tanto la actualización del precio como el registro de auditoría se revierten íntegramente. |

---

## 8. Cómo Repetir las Pruebas de Forma Segura

Para ejecutar nuevamente toda la batería de pruebas desde un estado inicial limpio:
1. Abrir DataGrip y ejecutar `sql/01_preparacion.sql` (o `01_esquema_y_datos.sql`), lo que reinicia la tabla de auditoría.
2. Si se desea reiniciar los precios base de los productos testigo (1, 2 y 3) sin recrear la base de datos:
   ```sql
   TRUNCATE TABLE auditoria_precios RESTART IDENTITY;
   UPDATE track SET unit_price = 10.00 WHERE track_id = 1;
   UPDATE track SET unit_price = 25.00 WHERE track_id = 2;
   UPDATE track SET unit_price = 50.00 WHERE track_id = 3;
   ```
3. Ejecutar los scripts en orden: `02`, `03` (o `04`), `04` (o `03`) y `05`.

---

## 9. Lista de Verificación de la Rúbrica Oficial (5.00 / 5.00 Puntos)

- [x] **1. Función Escalar (1.25 pts):** Retorno de un único valor `NUMERIC`, redondeo a 2 decimales con `ROUND`, límites exactos `-50` y `100` admitidos, validaciones estrictas y justificación teórica.
- [x] **2. Procedimiento Almacenado (1.25 pts):** `CREATE PROCEDURE` / `CALL`, reutilización de la función sin duplicar fórmulas, verificación con `IF NOT FOUND` y actualización con `WHERE` exclusivo.
- [x] **3. Trigger y Auditoría (1.25 pts):** Trigger `AFTER UPDATE FOR EACH ROW`, datos completos (`id_producto`, `precio_anterior`, `precio_nuevo`, `fecha_cambio`, `usuario_bd`) y filtro `IS DISTINCT FROM`.
- [x] **4. Pruebas y Evidencias (0.75 pts):** 8 casos completos y documentados, sentencias aislables para captura directa en DataGrip y pruebas de atomicidad con `ROLLBACK`.
- [x] **5. Repositorio y Reproducibilidad (0.50 pts):** Estructura clara y secuencial, `docker-compose.yml` funcional, instrucciones de conexión y ausencia de credenciales privadas.
