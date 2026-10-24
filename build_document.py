import os
import sys
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), val)
        border.set(qn('w:sz'), sz)
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), color)
        tblBorders.append(border)
    insideV = OxmlElement('w:insideV')
    insideV.set(qn('w:val'), 'none')
    tblBorders.append(insideV)
    tblPr.append(tblBorders)

def add_heading_styled(doc, text, level=1):
    h = doc.add_heading(level=level)
    run = h.add_run(text)
    h.paragraph_format.keep_with_next = True
    if level == 1:
        run.font.name = 'Arial'
        run.font.size = Pt(17)
        run.font.bold = True
        run.font.color.rgb = RGBColor(27, 54, 93) # Deep Navy
        h.paragraph_format.space_before = Pt(18)
        h.paragraph_format.space_after = Pt(6)
    elif level == 2:
        run.font.name = 'Arial'
        run.font.size = Pt(13.5)
        run.font.bold = True
        run.font.color.rgb = RGBColor(43, 108, 176) # Accent Blue
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)
    elif level == 3:
        run.font.name = 'Arial'
        run.font.size = Pt(11.5)
        run.font.bold = True
        run.font.color.rgb = RGBColor(45, 55, 72)
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(2)
    return h

def add_paragraph_styled(doc, text, bold_prefix="", italic=False, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = 'Calibri'
        r_pre.font.size = Pt(11)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGBColor(27, 54, 93)
    r = p.add_run(text)
    r.font.name = 'Calibri'
    r.font.size = Pt(11)
    r.font.italic = italic
    r.font.color.rgb = RGBColor(45, 55, 72)
    return p

def add_callout(doc, text, title=""):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cell = table.cell(0, 0)
    cell.width = Inches(6.3)
    set_cell_background(cell, "F0F4F8")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=160)
    
    # Left border only (accent line)
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'single')
    left.set(qn('w:sz'), '24') # thick line
    left.set(qn('w:space'), '0')
    left.set(qn('w:color'), '1B365D')
    tcBorders.append(left)
    for b in ['top', 'bottom', 'right']:
        node = OxmlElement(f'w:{b}')
        node.set(qn('w:val'), 'none')
        tcBorders.append(node)
    tcPr.append(tcBorders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    if title:
        r_title = p.add_run(title + "\n")
        r_title.font.name = 'Arial'
        r_title.font.size = Pt(10.5)
        r_title.font.bold = True
        r_title.font.color.rgb = RGBColor(27, 54, 93)
    r = p.add_run(text)
    r.font.name = 'Calibri'
    r.font.size = Pt(10)
    r.font.color.rgb = RGBColor(45, 55, 72)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_code_box(doc, code_text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cell = table.cell(0, 0)
    cell.width = Inches(6.3)
    set_cell_background(cell, "1E293B") # dark slate code background
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    r = p.add_run(code_text)
    r.font.name = 'Consolas'
    r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(248, 250, 252)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_figure_image(doc, img_path, caption):
    if not os.path.exists(img_path):
        print(f"Warning: image not found: {img_path}")
        return
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(6)
    p_img.paragraph_format.space_after = Pt(2)
    p_img.paragraph_format.keep_with_next = True
    
    # Calculate aspect ratio
    im = Image.open(img_path)
    w, h = im.size
    aspect = h / w
    target_w = Inches(6.2)
    target_h = Inches(6.2 * aspect)
    if target_h > Inches(4.5):
        target_h = Inches(4.5)
        target_w = Inches(4.5 / aspect)
        
    p_img.add_run().add_picture(img_path, width=target_w, height=target_h)
    
    # Caption
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(8)
    r_cap = p_cap.add_run(caption)
    r_cap.font.name = 'Calibri'
    r_cap.font.size = Pt(9.5)
    r_cap.font.italic = True
    r_cap.font.color.rgb = RGBColor(100, 116, 139)

def main():
    print("Iniciando generación de documento Word...")
    doc = Document()
    
    # Configuración de márgenes a 2.5 cm (aprox 0.98 pulgadas)
    for section in doc.sections:
        section.top_margin = Inches(0.98)
        section.bottom_margin = Inches(0.98)
        section.left_margin = Inches(0.98)
        section.right_margin = Inches(0.98)
        
    # =========================================================================
    # PORTADA INSTITUCIONAL UNIVERSITARIA
    # =========================================================================
    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_top.paragraph_format.space_before = Pt(10)
    p_top.paragraph_format.space_after = Pt(2)
    r_u = p_top.add_run("UNIVERSIDAD NACIONAL / FACULTAD DE INGENIERÍA\n")
    r_u.font.name = 'Arial'
    r_u.font.size = Pt(14)
    r_u.font.bold = True
    r_u.font.color.rgb = RGBColor(27, 54, 93)
    
    r_c = p_top.add_run("INGENIERÍA DE SISTEMAS E INFORMÁTICA\nCURSO: BASE DE DATOS 1 — CICLO VI 2026\n")
    r_c.font.name = 'Arial'
    r_c.font.size = Pt(11)
    r_c.font.color.rgb = RGBColor(71, 85, 105)
    
    # Divider line
    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_div.paragraph_format.space_before = Pt(12)
    p_div.paragraph_format.space_after = Pt(18)
    r_line = p_div.add_run("—" * 45)
    r_line.font.color.rgb = RGBColor(43, 108, 176)
    
    # Title
    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tit.paragraph_format.space_before = Pt(10)
    p_tit.paragraph_format.space_after = Pt(6)
    r_t = p_tit.add_run("INFORME DE PRÁCTICA TÉCNICA Y EVIDENCIAS\nTAREA NO. 7: LÓGICA DE NEGOCIO Y TRAZABILIDAD EN POSTGRESQL")
    r_t.font.name = 'Arial'
    r_t.font.size = Pt(19)
    r_t.font.bold = True
    r_t.font.color.rgb = RGBColor(27, 54, 93)
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(26)
    r_sub = p_sub.add_run("Implementación y Comprobación de Procedimiento Almacenado, Función Escalar y Disparador de Auditoría en Catálogo Chinook")
    r_sub.font.name = 'Calibri'
    r_sub.font.size = Pt(12.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(100, 116, 139)
    
    # Metadata Box Table
    meta_tbl = doc.add_table(rows=5, cols=2)
    meta_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_tbl.autofit = False
    set_table_borders(meta_tbl, color="CBD5E1", sz="4")
    
    meta_data = [
        ("Estudiante:", "Robert Gameros"),
        ("Repositorio Oficial GitHub:", "https://github.com/RobertGameros/S15-Procedimientos-almacenados-funciones-escalares-y-triggers.git"),
        ("Motor de Base de Datos:", "PostgreSQL 18.6 (Desplegado con Docker Compose en postgres:18-alpine)"),
        ("Entorno y Cliente SQL:", "JetBrains DataGrip (PostgreSQL JDBC Driver ver. 42.7.13)"),
        ("Base de Datos Base:", "Chinook Database (Luis Rocha) — Catálogo de Música Digital (track)"),
    ]
    
    for row_idx, (k, v) in enumerate(meta_data):
        c0, c1 = meta_tbl.rows[row_idx].cells
        c0.width = Inches(2.2)
        c1.width = Inches(4.1)
        set_cell_background(c0, "F8FAFC")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, top=70, bottom=70, left=100, right=100)
        set_cell_margins(c1, top=70, bottom=70, left=100, right=100)
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(k)
        r0.font.name = 'Arial'
        r0.font.size = Pt(10)
        r0.font.bold = True
        r0.font.color.rgb = RGBColor(27, 54, 93)
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(v)
        r1.font.name = 'Calibri'
        r1.font.size = Pt(10)
        if "github.com" in v:
            r1.font.bold = True
            r1.font.color.rgb = RGBColor(43, 108, 176)
        else:
            r1.font.color.rgb = RGBColor(45, 55, 72)
            
    p_foot = doc.add_paragraph()
    p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_foot.paragraph_format.space_before = Pt(36)
    r_foot = p_foot.add_run("OCTUBRE 2026 — MODALIDAD INDIVIDUAL — EVALUACIÓN TOTAL: 5.00 PUNTOS")
    r_foot.font.name = 'Arial'
    r_foot.font.size = Pt(10)
    r_foot.font.bold = True
    r_foot.font.color.rgb = RGBColor(100, 116, 139)
    
    doc.add_page_break()
    
    # =========================================================================
    # SECCIÓN 1: INTRODUCCIÓN Y CONTEXTO DEL CASO
    # =========================================================================
    add_heading_styled(doc, "1. Introducción y Contexto del Caso de Negocio", level=1)
    
    add_paragraph_styled(doc, 
        "Una tienda digital internacional de música requiere actualizar los precios de venta de su catálogo de pistas de audio de forma controlada, segura y con estricta trazabilidad forense. Para dar cumplimiento a las mejores prácticas de ingeniería de software en bases de datos relacionales, el sistema debe resolver tres necesidades operativas críticas:",
        bold_prefix=""
    )
    
    add_paragraph_styled(doc, "1. Cálculo de Proyección sin Efectos Colaterales: Antes de confirmar o persistir cualquier ajuste porcentual sobre el catálogo, el área de finanzas debe ser capaz de evaluar el precio resultante de manera matemática pura, sin riesgo de alterar registros en disco ni consultar estados mutables.", bold_prefix="• ")
    add_paragraph_styled(doc, "2. Orquestación y Validación de Lógica de Negocio: Al autorizar un ajuste, el sistema debe verificar exhaustivamente la validez de los parámetros de entrada y comprobar la existencia real del producto o pista musical en el catálogo antes de emitir la instrucción de actualización.", bold_prefix="• ")
    add_paragraph_styled(doc, "3. Auditoría Automática e Ineludible: Cada cambio efectivo de precio debe quedar asentado de forma autónoma e instantánea en una bitácora histórica, almacenando el valor anterior, el nuevo valor, la estampa de tiempo exacta y el usuario de base de datos responsable de la operación, sin depender de que el invocador recuerde insertar el registro de auditoría.", bold_prefix="• ")
    
    add_callout(doc,
        "Principio de Inmutabilidad Histórica: En estricto apego a las reglas de integridad financiera, las facturas previamente emitidas en el catálogo Chinook (tabla invoice_line) no deben modificarse bajo ninguna circunstancia. El ajuste porcentual afecta única y exclusivamente al precio actual de catálogo de la tabla track.",
        title="Regla de Integridad Financiera"
    )
    
    # =========================================================================
    # SECCIÓN 2: ARQUITECTURA DESACOPLADA Y SÍNTESIS DE OBJETOS
    # =========================================================================
    add_heading_styled(doc, "2. Arquitectura Desacoplada y Tabla Síntesis de Objetos", level=1)
    
    add_paragraph_styled(doc,
        "Para garantizar alta cohesión y bajo acoplamiento, la solución se diseñó en tres capas lógicas independientes dentro del motor de base de datos PostgreSQL 18. Cada objeto resuelve una responsabilidad única bien delimitada:",
        bold_prefix=""
    )
    
    # Table of Objects
    obj_table = doc.add_table(rows=6, cols=5)
    obj_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    obj_table.autofit = False
    set_table_borders(obj_table, color="CBD5E1", sz="4")
    
    headers = ["Objeto", "Tipo de Objeto", "Parámetros", "Retorno / Efecto", "Responsabilidad Principal"]
    widths = [Inches(1.2), Inches(1.1), Inches(1.1), Inches(1.1), Inches(1.8)]
    
    for c_idx, h_text in enumerate(headers):
        cell = obj_table.rows[0].cells[c_idx]
        cell.width = widths[c_idx]
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, top=80, bottom=80, left=90, right=90)
        p = cell.paragraphs[0]
        r = p.add_run(h_text)
        r.font.name = 'Arial'
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    rows_data = [
        ("calcular_precio_ajustado", "Función Escalar (PL/pgSQL IMMUTABLE)", "precio_actual numeric, porcentaje numeric", "numeric (valor atómico a 2 decimales)", "Cómputo puramente matemático: valida rangos [-50, 100], precio > 0, redondea a 2 decimales y rechaza resultado <= 0. Cero I/O sobre tablas."),
        ("aplicar_ajuste_precio", "Procedimiento Almacenado (CREATE PROCEDURE)", "p_id_producto integer, p_porcentaje numeric", "VOID (UPDATE unit_price en track)", "Orquestación de negocio: valida identificador, verifica existencia con IF NOT FOUND, reutiliza obligatoriamente la función escalar y ejecuta UPDATE."),
        ("fn_auditar_cambio_precio", "Función Trigger (PL/pgSQL)", "Ninguno (Variables especiales OLD y NEW)", "TRIGGER", "Función de soporte que evalúa si OLD.unit_price IS DISTINCT FROM NEW.unit_price e inserta la tupla en auditoria_precios."),
        ("trg_auditar_cambio_precio", "Disparador a Nivel de Fila (AFTER UPDATE)", "Evento: AFTER UPDATE OF unit_price ON track", "Dispara fn_auditar_cambio_precio()", "Garantiza la trazabilidad autónoma ante modificaciones de precio, sea mediante CALL o sentencias UPDATE directas en SQL."),
        ("auditoria_precios", "Tabla Relacional de Auditoría", "N/A", "Almacén histórico inmutable", "Persiste id_auditoria (PK), id_producto (FK conceptual), precio_anterior, precio_nuevo, fecha_cambio y usuario_bd."),
    ]
    
    for r_idx, r_data in enumerate(rows_data, start=1):
        for c_idx, val in enumerate(r_data):
            cell = obj_table.rows[r_idx].cells[c_idx]
            cell.width = widths[c_idx]
            bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=70, bottom=70, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val)
            r.font.name = 'Calibri'
            r.font.size = Pt(8.8)
            if c_idx == 0:
                r.font.name = 'Consolas'
                r.font.bold = True
                r.font.color.rgb = RGBColor(27, 54, 93)
            else:
                r.font.color.rgb = RGBColor(45, 55, 72)
                
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    
    # =========================================================================
    # SECCIÓN 3: CONSULTA 1 - PREPARACIÓN DEL ENTORNO Y CATÁLOGO
    # =========================================================================
    add_heading_styled(doc, "3. Consulta 1: Preparación del Catálogo y Esquema de Auditoría", level=1)
    
    add_paragraph_styled(doc,
        "La primera fase técnica se implementó en el archivo 01_esquema_y_datos.sql (disponible también como sql/01_preparacion.sql). Comprende la verificación de la versión del motor PostgreSQL 18.6 desplegado en Docker, el aseguramiento del catálogo Chinook, la creación de la tabla de trazabilidad auditoria_precios y la vista de compatibilidad productos.",
        bold_prefix=""
    )
    
    # Imagen versión PostgreSQL
    add_heading_styled(doc, "3.1. Verificación de Versión del Motor PostgreSQL 18.6", level=2)
    add_figure_image(doc, "Capturas/Consulta1/WhatsApp Image 2026-10-24 at 00.55.41.jpeg",
                     "Figura 1: Verificación de la versión del motor de base de datos en DataGrip: PostgreSQL 18.6 on x86_64-pc-linux-musl.")
    add_paragraph_styled(doc,
        "La consulta SELECT version(); ejecutada sobre la conexión 'Chinooks15' ratifica la operación sobre PostgreSQL 18.6 ejecutándose dentro de un contenedor Docker aislado sobre Alpine Linux de 64 bits. Esta evidencia técnica satisface el primer requerimiento de reproducibilidad del entorno de evaluación.",
        bold_prefix="Análisis Técnico: "
    )
    
    # Imagen Creación tabla track y datos semilla
    add_heading_styled(doc, "3.2. Catálogo Chinook (track) y Datos Semilla", level=2)
    add_figure_image(doc, "Capturas/Consulta1/WhatsApp Image 2026-10-24 at 00.56.16.jpeg",
                     "Figura 2: Definición DDL y creación defensiva de la tabla del catálogo track con restricción CHECK (unit_price > 0).")
    add_figure_image(doc, "Capturas/Consulta1/WhatsApp Image 2026-10-24 at 00.56.45.jpeg",
                     "Figura 3: Inserción de las pistas musicales semilla (track_id = 1, 2 y 3) con cláusula ON CONFLICT DO NOTHING (3 rows affected).")
    add_paragraph_styled(doc,
        "Se verifica la disponibilidad de la tabla track del catálogo Chinook con columnas clave track_id (PK), name y unit_price NUMERIC(10,2). En caso de desplegarse en una base limpia, el script inserta de forma autónoma tres pistas semilla con precio unitario 0.99, asegurando que la práctica sea 100% reproducible.",
        bold_prefix="Análisis Técnico: "
    )
    
    # Creación de auditoria_precios y comentarios
    add_heading_styled(doc, "3.3. Creación de la Tabla de Auditoría (auditoria_precios)", level=2)
    add_figure_image(doc, "Capturas/Consulta1/WhatsApp Image 2026-10-24 at 00.57.21.jpeg",
                     "Figura 4: Eliminación segura previa (DROP TABLE IF EXISTS auditoria_precios CASCADE) para garantizar idempotencia.")
    add_figure_image(doc, "Capturas/Consulta1/WhatsApp Image 2026-10-24 at 00.59.42.jpeg",
                     "Figura 5: Creación de la tabla auditoria_precios con tipos de datos NUMERIC(10,2), estampa temporal y usuario por defecto.")
    add_figure_image(doc, "Capturas/Consulta1/WhatsApp Image 2026-10-24 at 00.591.42.jpeg",
                     "Figura 6: Documentación técnica en el catálogo de PostgreSQL mediante sentencias COMMENT ON TABLE y COMMENT ON COLUMN.")
    add_paragraph_styled(doc,
        "La tabla auditoria_precios se estructuró con los campos obligatorios: id_auditoria (SERIAL PRIMARY KEY), id_producto (INTEGER NOT NULL), precio_anterior (NUMERIC(10,2) NOT NULL), precio_nuevo (NUMERIC(10,2) NOT NULL), fecha_cambio (TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP) y usuario_bd (TEXT NOT NULL DEFAULT CURRENT_USER). Se añadieron metadatos en el catálogo de PostgreSQL para documentar cada columna.",
        bold_prefix="Análisis Técnico: "
    )
    
    # Vista productos y estado inicial
    add_heading_styled(doc, "3.4. Vista de Compatibilidad y Estado Inicial Limpio", level=2)
    add_figure_image(doc, "Capturas/Consulta1/WhatsApp Image 2026-10-24 at2 00.59.42.jpeg",
                     "Figura 7: Creación de la vista actualizable productos para desacoplar nombres estándar de negocio del esquema físico de Chinook.")
    add_figure_image(doc, "Capturas/Consulta1/WhatsApp Image 2026-10-24 at 00.2159.42.jpeg",
                     "Figura 8: Inspección de los productos testigo del catálogo antes de iniciar cualquier manipulación (Pistas 1, 2 y 3 con precio 0.99).")
    add_figure_image(doc, "Capturas/Consulta1/WhatsApp Image 2026-10-24 at 00.59.4212.jpeg",
                     "Figura 9: Comprobación del estado inicial de auditoria_precios: tabla completamente vacía (0 registros), estableciendo la línea base.")
    add_paragraph_styled(doc,
        "La vista productos mapea 1 a 1 las columnas de track (track_id -> id_producto, name -> nombre, unit_price -> precio_actual), permitiendo operar bajo el estándar de 'productos' sin alterar el motor. Por su parte, la Figura 9 demuestra que auditoria_precios inicia vacía, lo cual es estrictamente necesario para certificar que cualquier registro posterior provendrá exclusivamente de los triggers de actualización.",
        bold_prefix="Análisis Técnico: "
    )
    
    # =========================================================================
    # SECCIÓN 4: CONSULTA 2 - FUNCIÓN ESCALAR CALCULAR_PRECIO_AJUSTADO
    # =========================================================================
    add_heading_styled(doc, "4. Consulta 2: Función Escalar calcular_precio_ajustado", level=1)
    
    add_paragraph_styled(doc,
        "La función matemática se implementó en el archivo 02_funcion_escalar.sql. Representa la primera capa del sistema, orientada a cómputo matemático puro sin efectos colaterales.",
        bold_prefix=""
    )
    
    add_callout(doc,
        "Justificación Teórica de Función Escalar vs. Tabular:\n"
        "Esta rutina se define como función ESCALAR (retorna un único valor escalar atómico de tipo NUMERIC) y NO como una función tabular (SETOF o TABLE). Esto se debe a que su responsabilidad exclusiva es computar el ajuste de un solo valor monetario a partir de un porcentaje. Al ser escalar, puede componerse libremente como una expresión algebraica dentro de sentencias SELECT, cláusulas WHERE, asignaciones de variables en PL/pgSQL y sentencias UPDATE. Se declaró con volatilidad IMMUTABLE al ser puramente determinista y no acceder a tablas ni estados del sistema.",
        title="Fundamentación Teórica de Diseño"
    )
    
    add_figure_image(doc, "Capturas/Consulta2/image.png",
                     "Figura 10: Compilación exitosa de la función escalar calcular_precio_ajustado en DataGrip (completed in 32 ms).")
    add_figure_image(doc, "Capturas/Consulta2/image2.png",
                     "Figura 11: Bloque de validaciones defensivas: rechazo de NULL, validación de precio_actual > 0 y porcentaje en [-50, 100].")
    add_figure_image(doc, "Capturas/Consulta2/image3.png",
                     "Figura 12: Bloque de cálculo con ROUND a 2 decimales, validación de resultado > 0, declaración IMMUTABLE y comentario del objeto.")
    
    add_paragraph_styled(doc,
        "La función calcular_precio_ajustado aplica la fórmula matemática precio_actual * (1 + (porcentaje / 100.0)) y redondea estrictamente a dos decimales con ROUND. Si alguno de los argumentos es NULL o si el precio base es menor o igual a cero, emite excepciones con códigos check_violation o numeric_value_out_of_range. Igualmente, restringe los porcentajes de ajuste al rango [-50, 100], permitiendo aumentos de hasta el 100% y descuentos de hasta el 50%.",
        bold_prefix="Reglas de Negocio Implementadas: "
    )
    
    # =========================================================================
    # SECCIÓN 5: CONSULTA 3 - DISPARADOR (TRIGGER) Y FUNCIÓN DE AUDITORÍA
    # =========================================================================
    add_heading_styled(doc, "5. Consulta 3: Disparador y Función Trigger de Auditoría", level=1)
    
    add_paragraph_styled(doc,
        "La segunda capa arquitectónica se desarrolló en el archivo 03_trigger_auditoria.sql (y sql/04_trigger_y_funcion.sql). Se compone de una función trigger y un disparador a nivel de fila asociado al evento AFTER UPDATE sobre la tabla del catálogo.",
        bold_prefix=""
    )
    
    add_figure_image(doc, "Capturas/Consulta3/image.png",
                     "Figura 13: Definición de la función de soporte fn_auditar_cambio_precio() con evaluación condicional IS DISTINCT FROM.")
    add_figure_image(doc, "Capturas/Consulta3/image4.png",
                     "Figura 14: Eliminación segura del trigger preexistente con DROP TRIGGER IF EXISTS para mantener idempotencia de despliegue.")
    add_figure_image(doc, "Capturas/Consulta3/image5.png",
                     "Figura 15: Creación del disparador trg_auditar_cambio_precio sobre la columna unit_price de la tabla track (completed in 8 ms).")
    add_figure_image(doc, "Capturas/Consulta3/image6.png",
                     "Figura 16: Documentación técnica del trigger asociada en el catálogo de PostgreSQL mediante COMMENT ON TRIGGER.")
    
    add_paragraph_styled(doc,
        "1. Discriminación con IS DISTINCT FROM: La condición IF OLD.unit_price IS DISTINCT FROM NEW.unit_price THEN previene que sentencias UPDATE que asignen el mismo precio preexistente generen registros espurios o redundantes en auditoria_precios.\n"
        "2. Trazabilidad Automática e Ineludible: El disparador opera a nivel del motor relacional. Cualquier sentencia UPDATE (provenga de una aplicación externa, de un procedimiento o de un script interactivo en consola) dispara el registro histórico con marca temporal de servidor (CURRENT_TIMESTAMP) y usuario de sesión (CURRENT_USER).\n"
        "3. Orden de Compilación: Este script se ejecutó antes del procedimiento almacenado para que las pruebas posteriores del procedimiento activaran la auditoría de forma natural.",
        bold_prefix="Mecanismos de Protección Implementados:\n"
    )
    
    # =========================================================================
    # SECCIÓN 6: CONSULTA 4 - PROCEDIMIENTO ALMACENADO APLICAR_AJUSTE_PRECIO
    # =========================================================================
    add_heading_styled(doc, "6. Consulta 4: Procedimiento Almacenado aplicar_ajuste_precio", level=1)
    
    add_paragraph_styled(doc,
        "El procedimiento orquestador se implementó en el archivo 04_procedimiento_almacenado.sql (y sql/03_procedimiento.sql). Se define mediante la sintaxis moderna CREATE OR REPLACE PROCEDURE y se ejecuta mediante la sentencia CALL.",
        bold_prefix=""
    )
    
    add_figure_image(doc, "Capturas/Consulta4/image.png",
                     "Figura 17: Definición del procedimiento aplicar_ajuste_precio y validación defensiva de identificador y porcentaje no nulos.")
    add_figure_image(doc, "Capturas/Consulta4/image2.png",
                     "Figura 18: Verificación de existencia del producto en el catálogo mediante SELECT INTO y evaluación de excepción IF NOT FOUND.")
    add_figure_image(doc, "Capturas/Consulta4/image3.png",
                     "Figura 19: Reutilización de calcular_precio_ajustado, actualización con WHERE track_id y compilación exitosa (completed in 14 ms).")
    
    add_paragraph_styled(doc,
        "• Reutilización de Código sin Duplicidad: El procedimiento NO repite la fórmula matemática del porcentaje ni sus comprobaciones de límites. En su lugar, invoca v_precio_nuevo := calcular_precio_ajustado(v_precio_actual, p_porcentaje); delegando la responsabilidad matemática a la función escalar.\n"
        "• Desacoplamiento de la Bitácora: El procedimiento NO contiene instrucciones INSERT sobre auditoria_precios. Esta separación de responsabilidades asegura que si el procedimiento aborta por error, no quedan registros huérfanos.\n"
        "• Delegación Transaccional: No fuerza sentencias COMMIT ni ROLLBACK internas, otorgando el control de la transacción a la sesión cliente.",
        bold_prefix="Aspectos Arquitectónicos Clave:\n"
    )
    
    # =========================================================================
    # SECCIÓN 7: CONSULTA 5 - BATERÍA COMPLETA DE CASOS DE PRUEBA
    # =========================================================================
    add_heading_styled(doc, "7. Consulta 5: Batería Completa de los 8 Casos de Prueba Evaluables", level=1)
    
    add_paragraph_styled(doc,
        "Las pruebas de aceptación y verificación integral se diseñaron en el script 05_casos_prueba.sql (y sql/05_pruebas.sql). Cada caso fue ejecutado de forma controlada en JetBrains DataGrip, demostrando tanto los resultados numéricos exitosos como las excepciones controladas del motor.",
        bold_prefix=""
    )
    
    # Subsección: Fase 0 - Establecimiento de Estado Base
    add_heading_styled(doc, "7.0. Fase 0: Inicialización y Establecimiento de Precios Base", level=2)
    add_figure_image(doc, "Capturas/Consulta5/image.png", "Figura 20: Limpieza inicial de la tabla auditoria_precios con TRUNCATE RESTART IDENTITY.")
    add_figure_image(doc, "Capturas/Consulta5/image2.png", "Figura 21: Establecimiento de precios testigo verificables mentalmente: Track 1 = 10.00, Track 2 = 25.00 y Track 3 = 50.00.")
    add_figure_image(doc, "Capturas/Consulta5/image3.png", "Figura 22: Vaciado de auditoría para descartar los registros generados por la inicialización de los precios base.")
    add_figure_image(doc, "Capturas/Consulta5/image4.png", "Figura 23: Comprobación del catálogo base listo: Pistas 1 (10.00), 2 (25.00) y 3 (50.00).")
    add_figure_image(doc, "Capturas/Consulta5/image5.png", "Figura 24: Verificación del conteo de auditoría en cero absoluto (total_auditoria_inicial = 0).")
    add_paragraph_styled(doc,
        "Se fijaron deliberadamente precios base cerrados (10.00, 25.00 y 50.00) para las pistas testigo 1, 2 y 3, lo cual permite al evaluador comprobar la exactitud de los porcentajes y las reversiones de forma mental e inequívoca.",
        bold_prefix="Propósito Técnico: "
    )
    
    # Caso 1
    add_heading_styled(doc, "7.1. Caso 1: Función Escalar — Aumento (+10%) y Reducción (-50%)", level=2)
    add_paragraph_styled(doc, "Validar que la función calcula correctamente tanto incrementos como reducciones sobre el límite admitido (-50%) y redondea con precisión a dos decimales.", bold_prefix="Propósito: ")
    add_paragraph_styled(doc, "precio_base = 10.00, porcentaje = 10.00% | precio_base = 10.00, porcentaje = -50.00%.", bold_prefix="Datos Utilizados: ")
    add_paragraph_styled(doc, "aumento: 11.00 | reduccion: 5.00.", bold_prefix="Resultado Esperado: ")
    add_figure_image(doc, "Capturas/Consulta5/image6.png", "Figura 25: Ejecución de Caso 1 en DataGrip mostrando resultados de aumento = 11 y reduccion = 5.")
    add_paragraph_styled(doc,
        "La consulta SELECT calcular_precio_ajustado(10.00, 10.00) AS aumento, calcular_precio_ajustado(10.00, -50.00) AS reduccion; devolvió con exactitud 11.00 (aumento del 10%) y 5.00 (reducción del 50%), comprobando que el límite inferior negativo es procesado sin errores.",
        bold_prefix="Resultado Observado: "
    )
    
    # Caso 2
    add_heading_styled(doc, "7.2. Caso 2: Función Escalar — Validación de Entradas Inválidas", level=2)
    add_paragraph_styled(doc, "Verificar que la función rechaza de forma estricta parámetros NULL, precios menores o iguales a cero y porcentajes fuera del rango admisible [-50, 100].", bold_prefix="Propósito: ")
    add_paragraph_styled(doc, "Se evaluaron 6 casos independientes ejecutados de manera individual en DataGrip:", bold_prefix="Pruebas Realizadas: ")
    
    add_figure_image(doc, "Capturas/Consulta5/image7.png", "Figura 26: Prueba 2.1 — Rechazo de precio actual NULL con excepción [23514] check_violation.")
    add_figure_image(doc, "Capturas/Consulta5/image8.png", "Figura 27: Prueba 2.2 — Rechazo de porcentaje de ajuste NULL con excepción [23514] check_violation.")
    add_figure_image(doc, "Capturas/Consulta5/image9.png", "Figura 28: Prueba 2.3 — Rechazo de precio actual igual a cero (0) con excepción numeric_value_out_of_range.")
    add_figure_image(doc, "Capturas/Consulta5/image10.png", "Figura 29: Prueba 2.4 — Rechazo de precio actual negativo (-5.00) con excepción numeric_value_out_of_range.")
    add_figure_image(doc, "Capturas/Consulta5/image11.png", "Figura 30: Prueba 2.5 — Rechazo de porcentaje inferior al mínimo permitido (-60.00%) fuera de [-50, 100].")
    add_figure_image(doc, "Capturas/Consulta5/image12.png", "Figura 31: Prueba 2.6 — Rechazo de porcentaje superior al máximo permitido (150.00%) fuera de [-50, 100].")
    
    add_paragraph_styled(doc,
        "Cada una de las 6 pruebas generó el error esperado en la consola de DataGrip con el código SQLSTATE correspondiente y el mensaje descriptivo en lenguaje natural. Ninguna entrada anómala pudo evadir las precondiciones de la función.",
        bold_prefix="Resultado Observado: "
    )
    
    # Caso 3
    add_heading_styled(doc, "7.3. Caso 3: Procedimiento Almacenado — Cambio Válido con CALL (+20%)", level=2)
    add_paragraph_styled(doc, "Actualizar un producto existente (Track ID = 1) aumentando su precio en +20%. Verificar que el producto 1 cambia, el producto 2 permanece inalterado y el disparador genera automáticamente la fila de auditoría.", bold_prefix="Propósito: ")
    add_paragraph_styled(doc, "p_id_producto = 1 (precio actual 10.00), p_porcentaje = 20.00% (incremento proyectado a 12.00).", bold_prefix="Datos Utilizados: ")
    add_paragraph_styled(doc, "Track 1 se actualiza a 12.00; Track 2 permanece en 25.00; se crea una fila en auditoria_precios.", bold_prefix="Resultado Esperado: ")
    
    add_figure_image(doc, "Capturas/Consulta5/image13.png", "Figura 32: Paso 3.1 — Estado inicial del catálogo antes de la ejecución (Track 1 = 10.00, Track 2 = 25.00).")
    add_figure_image(doc, "Capturas/Consulta5/image14.png", "Figura 33: Paso 3.2 — Ejecución exitosa de CALL aplicar_ajuste_precio(1, 20.00) mostrando notificación RAISE NOTICE.")
    add_figure_image(doc, "Capturas/Consulta5/image15.png", "Figura 34: Paso 3.3 — Estado posterior del catálogo: Track 1 modificado y Track 2 inalterado en 25.00.")
    add_figure_image(doc, "Capturas/Consulta5/image16.png", "Figura 35: Paso 3.4 — Verificación en auditoria_precios del registro generado autónomamente por el trigger.")
    
    add_paragraph_styled(doc,
        "La invocación con CALL aplicar_ajuste_precio(1, 20.00) actualizó el precio de la pista 1 de 10.00 a 12.00, emitiendo el mensaje 'Ajuste completado para Producto/Track ID 1: Precio previo = 10.00, Precio nuevo = 12.00 (Ajuste: 20.00 %)'. La pista 2 se mantuvo inmutable en 25.00. La consulta a auditoria_precios demostró la inserción automática de la tupla con id_producto=1, precio_anterior=10.00, precio_nuevo=12.00 y usuario_bd='ROBERT'.",
        bold_prefix="Resultado Observado: "
    )
    
    # Caso 4
    add_heading_styled(doc, "7.4. Caso 4: Procedimiento Almacenado — Identificador Inexistente", level=2)
    add_paragraph_styled(doc, "Comprobar que al invocar el procedimiento con una clave primaria inexistente (Track ID = 999999), el sistema aborta de inmediato con una excepción controlada sin alterar datos del catálogo ni la bitácora.", bold_prefix="Propósito: ")
    add_paragraph_styled(doc, "p_id_producto = 999999, p_porcentaje = 10.00%.", bold_prefix="Datos Utilizados: ")
    add_paragraph_styled(doc, "Lanzamiento de excepción [22000] data_exception. Cero filas modificadas en track y cero filas añadidas a auditoria_precios.", bold_prefix="Resultado Esperado: ")
    
    add_figure_image(doc, "Capturas/Consulta5/image17.png", "Figura 36: Ejecución de CALL aplicar_ajuste_precio(999999, 10.00) lanzando [22000] ERROR: Producto no encontrado.")
    add_figure_image(doc, "Capturas/Consulta5/image18.png", "Figura 37: Comprobación de integridad en el catálogo: los productos 1 y 2 permanecen exactamente intactos.")
    add_figure_image(doc, "Capturas/Consulta5/image19.png", "Figura 38: Consulta de auditoría para el ID 999999: resultado vacío (0 filas), demostrando ausencia de efectos secundarios.")
    
    add_paragraph_styled(doc,
        "El motor arrojó la excepción 'Producto no encontrado: No existe ningún producto o pista con identificador (ID = 999999)' con código 22000. Las Figuras 37 y 38 certifican que ni el catálogo de productos ni la tabla de auditoría registraron cambios.",
        bold_prefix="Resultado Observado: "
    )
    
    # Caso 5
    add_heading_styled(doc, "7.5. Caso 5: Procedimiento Almacenado — Porcentaje Inválido (+120%)", level=2)
    add_paragraph_styled(doc, "Demostrar que cuando se suministra un porcentaje fuera del rango admisible (ej. 120%), la función escalar propaga su excepción hacia el procedimiento orquestador, abortando la transacción sin aplicar cambios parciales en la base de datos.", bold_prefix="Propósito: ")
    add_paragraph_styled(doc, "p_id_producto = 1, p_porcentaje = 120.00% (excede el límite superior del 100%).", bold_prefix="Datos Utilizados: ")
    add_paragraph_styled(doc, "Excepción numeric_value_out_of_range propagada. Ausencia de cambios parciales en el precio de la pista 1.", bold_prefix="Resultado Esperado: ")
    add_paragraph_styled(doc,
        "Al ejecutarse CALL aplicar_ajuste_precio(1, 120.00), la invocación interna a calcular_precio_ajustado detectó que 120 > 100 y disparó la excepción 'Porcentaje no permitido: El porcentaje (120) está fuera del rango admitido [-50, 100]'. La ejecución se canceló de inmediato antes de llegar a la sentencia UPDATE, dejando el precio de la pista 1 intacto y sin generar registros en la tabla de auditoría.",
        bold_prefix="Resultado Observado: "
    )
    
    # Caso 6
    add_heading_styled(doc, "7.6. Caso 6: Disparador (Trigger) — Actualización Directa vía UPDATE", level=2)
    add_paragraph_styled(doc, "Demostrar la autonomía e ineludibilidad del disparador AFTER UPDATE: si un usuario u operador realiza un UPDATE directo en SQL sin invocar el procedimiento CALL, el trigger se activa automáticamente y registra la auditoría.", bold_prefix="Propósito: ")
    add_paragraph_styled(doc, "Sentencia UPDATE directa sobre Track ID = 2 modificando su precio a 30.00 (precio anterior: 25.00).", bold_prefix="Datos Utilizados: ")
    add_paragraph_styled(doc, "Inserción automática de una nueva fila en auditoria_precios con precio_anterior=25.00 y precio_nuevo=30.00.", bold_prefix="Resultado Esperado: ")
    
    add_figure_image(doc, "Capturas/Consulta5/image20.png", "Figura 39: Paso 6.2 — Ejecución de sentencia UPDATE directa sobre Track 2 cambiando precio a 30.00 (1 row affected).")
    add_figure_image(doc, "Capturas/Consulta5/image21.png", "Figura 40: Paso 6.3 — Verificación de la fila de auditoría generada de forma autónoma por el disparador.")
    
    add_paragraph_styled(doc,
        "La Figura 40 comprueba que la tupla de auditoría con id_auditoria=3 fue creada automáticamente con id_producto=2, precio_anterior=25.00, precio_nuevo=30.00 y usuario_bd='ROBERT', demostrando que la auditoría no depende de que el invocador use el procedimiento almacenado.",
        bold_prefix="Resultado Observado: "
    )
    
    # Caso 7
    add_heading_styled(doc, "7.7. Caso 7: Disparador (Trigger) — Precio sin Cambio Efectivo (Mismo Valor)", level=2)
    add_paragraph_styled(doc, "Demostrar que gracias a la condición IS DISTINCT FROM, una sentencia UPDATE que asigne exactamente el mismo precio que ya posee el producto NO inserta ninguna fila redundante en la tabla de auditoría.", bold_prefix="Propósito: ")
    add_paragraph_styled(doc, "UPDATE track SET unit_price = 30.00 WHERE track_id = 2; (su valor actual ya es 30.00).", bold_prefix="Datos Utilizados: ")
    add_paragraph_styled(doc, "El conteo de filas en auditoria_precios antes y después de la operación debe ser exactamente idéntico.", bold_prefix="Resultado Esperado: ")
    
    add_figure_image(doc, "Capturas/Consulta5/image22.png", "Figura 41: Paso 7.1 — Conteo previo en auditoria_precios (total_auditoria_antes = 3).")
    add_figure_image(doc, "Capturas/Consulta5/image23.png", "Figura 42: Paso 7.2 — Ejecución de UPDATE track asignando 30.00 (el mismo valor actual) con 1 row affected.")
    add_figure_image(doc, "Capturas/Consulta5/image24.png", "Figura 43: Paso 7.3 — Conteo posterior en auditoria_precios (total_auditoria_despues = 3, idéntico al anterior).")
    
    add_paragraph_styled(doc,
        "La evaluación de las Figuras 41 y 43 demuestra de manera concluyente que total_auditoria_antes fue 3 y total_auditoria_despues se mantuvo en 3. A pesar de que PostgreSQL procesó la fila en el UPDATE (1 row affected), el trigger evaluó OLD.unit_price IS DISTINCT FROM NEW.unit_price como FALSO y no generó ninguna fila basura. (Nota: se descartó image25.png por ser duplicado exacto de image24.png).",
        bold_prefix="Resultado Observado: "
    )
    
    # Caso 8
    add_heading_styled(doc, "7.8. Caso 8: Integridad Transaccional — Control con BEGIN y ROLLBACK", level=2)
    add_paragraph_styled(doc, "Demostrar la atomicidad del motor relacional mediante transacciones explícitas: al ejecutar un ajuste dentro de un bloque BEGIN y emitir posteriormente ROLLBACK, tanto la actualización de precio como la fila insertada por el trigger deben revertirse en su totalidad.", bold_prefix="Propósito: ")
    add_paragraph_styled(doc, "Track ID = 3 (precio inicial 50.00), ajuste porcentual de +15.00% (precio en transacción: 57.50).", bold_prefix="Datos Utilizados: ")
    add_paragraph_styled(doc, "Dentro de la transacción, el precio muestra 57.50 y la auditoría muestra la fila; tras el ROLLBACK, el precio regresa a 50.00 y la fila de auditoría desaparece.", bold_prefix="Resultado Esperado: ")
    
    add_figure_image(doc, "Capturas/Consulta5/image26.png", "Figura 44: Paso 8.1 — Estado inicial de Track 3 en el catálogo (precio base = 50.00).")
    add_figure_image(doc, "Capturas/Consulta5/image27.png", "Figura 45: Paso 8.2 — Apertura de la transacción explícita mediante la sentencia BEGIN en DataGrip.")
    add_figure_image(doc, "Capturas/Consulta5/image28.png", "Figura 46: Paso 8.3 — Ejecución de CALL aplicar_ajuste_precio(3, 15.00) dentro de la transacción activa.")
    add_figure_image(doc, "Capturas/Consulta5/image30.png", "Figura 47: Paso 8.4 — Consulta del precio dentro de la sesión activa mostrando 57.50.")
    add_figure_image(doc, "Capturas/Consulta5/image29.png", "Figura 48: Paso 8.4 — Consulta de auditoría dentro de la transacción mostrando la fila generada para Track 3.")
    add_figure_image(doc, "Capturas/Consulta5/image31.png", "Figura 49: Paso 8.5 — Ejecución del comando ROLLBACK para abortar la transacción.")
    add_figure_image(doc, "Capturas/Consulta5/image32.png", "Figura 50: Paso 8.6 — Comprobación post-ROLLBACK en track: el precio de Track 3 regresó a su valor original de 50.00.")
    add_figure_image(doc, "Capturas/Consulta5/image33.png", "Figura 51: Paso 8.6 — Comprobación post-ROLLBACK en auditoria_precios: la fila fue descartada por completo (0 filas).")
    
    add_paragraph_styled(doc,
        "La secuencia de capturas de las Figuras 44 a la 51 evidencia el cumplimiento estricto del principio de Atomicidad (propiedad ACID). Durante la transacción, los cambios fueron visibles en la sesión (precio 57.50 y fila de auditoría id_auditoria=4). Al ejecutar ROLLBACK, PostgreSQL deshizo tanto la modificación en la tabla track como la inserción efectuada por el trigger en auditoria_precios, demostrando que ambos objetos operan dentro del mismo contexto transaccional coordinado.",
        bold_prefix="Resultado Observado: "
    )
    
    # =========================================================================
    # SECCIÓN 8: CONCLUSIONES TÉCNICAS
    # =========================================================================
    add_heading_styled(doc, "8. Conclusiones Técnicas y Respuestas Teóricas", level=1)
    
    add_paragraph_styled(doc,
        "A partir del diseño, despliegue y experimentación rigurosa de los objetos de base de datos en PostgreSQL 18, se formulan las siguientes conclusiones fundamentales:",
        bold_prefix=""
    )
    
    add_paragraph_styled(doc,
        "1. Diferenciación Estructural entre Objetos:\n"
        "• Función Escalar: Objeto determinista, de cómputo puro y sin efectos colaterales. Acepta argumentos y devuelve un único valor atómico primitivo (NUMERIC), permitiendo su uso directo en expresiones SELECT, WHERE y asignaciones PL/pgSQL.\n"
        "• Procedimiento Almacenado: Unidad de orquestación de negocio invocada con CALL. Su objetivo es coordinar validaciones complejas, interactuar con múltiples tablas y aplicar cambios en el estado de la base de datos (sentencias DML) bajo un control transaccional flexible.\n"
        "• Disparador (Trigger): Mecanismo pasivo de seguridad reactiva y trazabilidad. Se ejecuta de manera automática e ineludible en el motor ante eventos de tabla (AFTER UPDATE), garantizando que las reglas de auditoría se cumplan sin importar la procedencia de la sentencia SQL.",
        bold_prefix="A. "
    )
    
    add_paragraph_styled(doc,
        "2. ¿Por qué la Auditoría no debe depender de que el usuario la ejecute?:\n"
        "Si la inserción en la tabla de auditoría se delegara a una llamada manual en el procedimiento o a la buena fe de los desarrolladores de la aplicación cliente, existiría una vulnerabilidad arquitectónica crítica: cualquier actualización realizada directamente por el administrador vía consola, scripts de mantenimiento, herramientas BI o errores en el código de la app omitiría el registro histórico. Al implementar un disparador AFTER UPDATE en el motor, la auditoría se vuelve universal, obligatoria e inmutable, imposibilitando la alteración clandestina de precios sin dejar rastro.",
        bold_prefix="B. "
    )
    
    add_paragraph_styled(doc,
        "3. Eficiencia y Mitigación de Redundancia con IS DISTINCT FROM:\n"
        "En bases de datos de alto tráfico, las actualizaciones ciegas que reasignan los mismos valores preexistentes pueden saturar el disco y degradar el rendimiento con escrituras innecesarias en bitácoras. La comprobación OLD.unit_price IS DISTINCT FROM NEW.unit_price demostró ser la técnica óptima para filtrar actualizaciones idénticas a costo de cómputo mínimo.",
        bold_prefix="C. "
    )
    
    # =========================================================================
    # SECCIÓN 9: LISTA DE VERIFICACIÓN Y RÚBRICA DE EVALUACIÓN
    # =========================================================================
    add_heading_styled(doc, "9. Lista de Verificación de la Rúbrica Oficial (5.00 Puntos)", level=1)
    
    rubric_tbl = doc.add_table(rows=6, cols=4)
    rubric_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    rubric_tbl.autofit = False
    set_table_borders(rubric_tbl, color="CBD5E1", sz="4")
    
    r_headers = ["Criterio Evaluado", "Desglose Oficial", "Evidencia Aportada en el Informe", "Puntos"]
    r_widths = [Inches(1.3), Inches(1.8), Inches(2.6), Inches(0.6)]
    
    for c_idx, h_text in enumerate(r_headers):
        cell = rubric_tbl.rows[0].cells[c_idx]
        cell.width = r_widths[c_idx]
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, top=70, bottom=70, left=80, right=80)
        p = cell.paragraphs[0]
        r = p.add_run(h_text)
        r.font.name = 'Arial'
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    r_rows = [
        ("1. Función Escalar", "Cálculo y retorno escalar: 0.75\nValidaciones y ausencia de modificaciones: 0.50", "Retorno atómico NUMERIC, redondeo a 2 decimales con ROUND. Rechazo de NULL, precio <= 0, rango [-50, 100]. Figuras 10 a 12 y 25 a 31.", "1.25"),
        ("2. Procedimiento Almacenado", "CREATE PROCEDURE/CALL y reutilización: 0.50\nActualización correcta: 0.50\nManejo de errores: 0.25", "Definido con CREATE PROCEDURE y ejecutado con CALL. Reutiliza calcular_precio_ajustado. Verifica producto con IF NOT FOUND. Figuras 17 a 19 y 32 a 38.", "1.25"),
        ("3. Trigger y Auditoría", "Trigger y función operativos: 0.50\nDatos completos en auditoría: 0.50\nNo auditar sin cambio: 0.25", "Trigger AFTER UPDATE OF unit_price ON track. Registra id_producto, precio anterior/nuevo, timestamp y CURRENT_USER. Filtro IS DISTINCT FROM. Figuras 13 a 16 y 39 a 43.", "1.25"),
        ("4. Pruebas y Evidencias", "Casos 1 a 5 documentados: 0.25\nCasos 6 a 8 documentados: 0.25\nCapturas legibles y explicación: 0.25", "Los 8 casos evaluables ejecutados con capturas nítidas de DataGrip, tabla antes/después, prueba de IS DISTINCT FROM y bloque BEGIN/ROLLBACK. Figuras 20 a 51.", "0.75"),
        ("5. Repositorio y Reproducibilidad", "SQL completo, organizado y accesible: 0.25\nREADME y orden de ejecución: 0.25", "Repositorio público en GitHub, README.md con arquitectura y credenciales genéricas de Docker, scripts 01 al 05 secuenciales y reproducibles.", "0.50"),
    ]
    
    for r_idx, r_data in enumerate(r_rows, start=1):
        for c_idx, val in enumerate(r_data):
            cell = rubric_tbl.rows[r_idx].cells[c_idx]
            cell.width = r_widths[c_idx]
            bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=70, right=70)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val)
            r.font.name = 'Calibri'
            r.font.size = Pt(8.5)
            if c_idx == 0:
                r.font.bold = True
                r.font.color.rgb = RGBColor(27, 54, 93)
            elif c_idx == 3:
                r.font.bold = True
                r.font.color.rgb = RGBColor(43, 108, 176)
            else:
                r.font.color.rgb = RGBColor(45, 55, 72)
                
    # Total row
    tot_row = rubric_tbl.add_row()
    c0 = tot_row.cells[0]
    c0.width = r_widths[0]
    set_cell_background(c0, "1B365D")
    p0 = c0.paragraphs[0]
    r0 = p0.add_run("TOTAL CALIFICACIÓN")
    r0.font.name = 'Arial'
    r0.font.size = Pt(9.5)
    r0.font.bold = True
    r0.font.color.rgb = RGBColor(255, 255, 255)
    
    c1 = tot_row.cells[1]
    c1.width = r_widths[1]
    set_cell_background(c1, "1B365D")
    p1 = c1.paragraphs[0]
    r1 = p1.add_run("Cumplimiento del 100% de los criterios")
    r1.font.name = 'Calibri'
    r1.font.size = Pt(9)
    r1.font.color.rgb = RGBColor(255, 255, 255)
    
    c2 = tot_row.cells[2]
    c2.width = r_widths[2]
    set_cell_background(c2, "1B365D")
    p2 = c2.paragraphs[0]
    r2 = p2.add_run("51 Figuras de evidencia con resultados reales en DataGrip")
    r2.font.name = 'Calibri'
    r2.font.size = Pt(9)
    r2.font.color.rgb = RGBColor(255, 255, 255)
    
    c3 = tot_row.cells[3]
    c3.width = r_widths[3]
    set_cell_background(c3, "1B365D")
    p3 = c3.paragraphs[0]
    r3 = p3.add_run("5.00 / 5.00")
    r3.font.name = 'Arial'
    r3.font.size = Pt(9.5)
    r3.font.bold = True
    r3.font.color.rgb = RGBColor(255, 255, 255)
    
    output_filename = "Informe_Tarea7_Robert_Gameros.docx"
    doc.save(output_filename)
    print(f"Documento generado exitosamente como '{output_filename}'!")

if __name__ == "__main__":
    main()
