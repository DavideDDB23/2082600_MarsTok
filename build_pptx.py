"""
Mars Operations — Styled PPTX builder
Produces a fully themed presentation matching the Marp dark-space design.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
import pptx.oxml.ns as nsmap
from lxml import etree
import copy

# ── Colour palette ────────────────────────────────────────────────────────────
BG       = RGBColor(0x0f, 0x17, 0x2a)   # slide background
BG_CARD  = RGBColor(0x1e, 0x29, 0x3b)   # card / code background
BG_CARD2 = RGBColor(0x16, 0x21, 0x31)   # slightly darker card
BORDER   = RGBColor(0x33, 0x41, 0x55)   # subtle borders
ORANGE   = RGBColor(0xf9, 0x73, 0x16)   # accent / titles
ORANGE_L = RGBColor(0xfb, 0x92, 0x3c)   # lighter orange (h3)
WHITE    = RGBColor(0xff, 0xff, 0xff)
TEXT     = RGBColor(0xe2, 0xe8, 0xf0)   # body text
MUTED    = RGBColor(0x94, 0xa3, 0xb8)   # muted text
GREEN    = RGBColor(0x22, 0xc5, 0x5e)
AMBER    = RGBColor(0xf5, 0x9e, 0x0b)
CYAN     = RGBColor(0x06, 0xb6, 0xd4)
BLUE     = RGBColor(0x60, 0xa5, 0xfa)
PURPLE   = RGBColor(0xa8, 0x55, 0xf7)
GREEN_C  = RGBColor(0x34, 0xd3, 0x99)   # code text

# Slide dimensions: 16:9 standard (12192000 x 6858000 EMU = 33.87 × 19.05 cm)
W = Inches(13.33)
H = Inches(7.5)

prs = Presentation()
prs.slide_width  = W
prs.slide_height = H

BLANK = prs.slide_layouts[6]   # completely blank layout

# ── Helper utilities ──────────────────────────────────────────────────────────

def rgb_hex(r: RGBColor) -> str:
    return f"{r[0]:02X}{r[1]:02X}{r[2]:02X}"

def fill_slide(slide, color: RGBColor):
    """Set slide background to a solid colour."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_rect(slide, x, y, w, h, fill_color, line_color=None, line_width=Pt(0.5)):
    """Add a filled rectangle shape."""
    shape = slide.shapes.add_shape(1, x, y, w, h)  # MSO_SHAPE_TYPE.RECTANGLE = 1
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = line_width
    else:
        shape.line.fill.background()
    return shape

def add_textbox(slide, x, y, w, h, text, font_size=Pt(16), bold=False,
                color=TEXT, align=PP_ALIGN.LEFT, font_name="Calibri",
                wrap=True, italic=False):
    txb = slide.shapes.add_textbox(x, y, w, h)
    txb.word_wrap = wrap
    tf = txb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = font_size
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = font_name
    return txb

def add_multiline_textbox(slide, x, y, w, h, lines, default_size=Pt(15),
                          default_color=TEXT, default_bold=False, spacing_after=Pt(4),
                          font_name="Calibri"):
    """
    lines = list of dicts:
        { text, size, color, bold, italic, align, bullet }
    or plain strings (use defaults).
    """
    txb = slide.shapes.add_textbox(x, y, w, h)
    txb.word_wrap = True
    tf = txb.text_frame
    tf.word_wrap = True

    first = True
    for line in lines:
        if isinstance(line, str):
            line = {"text": line}
        text   = line.get("text", "")
        size   = line.get("size", default_size)
        color  = line.get("color", default_color)
        bold   = line.get("bold", default_bold)
        italic = line.get("italic", False)
        align  = line.get("align", PP_ALIGN.LEFT)
        bullet = line.get("bullet", False)

        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()

        p.alignment = align
        p.space_after = spacing_after

        if bullet:
            prefix = "  • "
            text = prefix + text

        run = p.add_run()
        run.text = text
        run.font.size = size
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = color
        run.font.name = font_name

    return txb

def add_title_bar(slide, title: str, subtitle: str = ""):
    """Add the orange bottom bar with title used on content slides."""
    # Top orange accent line
    add_rect(slide, 0, 0, W, Inches(0.07), ORANGE)
    # Title text
    add_textbox(slide, Inches(0.55), Inches(0.12), Inches(11.5), Inches(0.55),
                title, font_size=Pt(28), bold=True, color=ORANGE)
    # Orange underline below title
    add_rect(slide, Inches(0.55), Inches(0.7), Inches(12.23), Inches(0.025), ORANGE)
    if subtitle:
        add_textbox(slide, Inches(0.55), Inches(0.72), Inches(12), Inches(0.35),
                    subtitle, font_size=Pt(13), color=MUTED)

def card(slide, x, y, w, h, accent_color=None):
    """Draw a card rectangle with optional left accent bar."""
    r = add_rect(slide, x, y, w, h, BG_CARD, BORDER, Pt(0.75))
    if accent_color:
        add_rect(slide, x, y, Inches(0.07), h, accent_color)
    return r

def add_table(slide, x, y, w, rows_data, col_widths=None, header=True):
    """
    rows_data = list of rows, each row = list of cell strings.
    """
    rows  = len(rows_data)
    cols  = len(rows_data[0])
    row_h = Inches(0.38)
    total_h = row_h * rows

    tbl = slide.shapes.add_table(rows, cols, x, y, w, total_h).table

    # Column widths
    if col_widths:
        for i, cw in enumerate(col_widths):
            tbl.columns[i].width = cw
    else:
        cw = int(w / cols)
        for i in range(cols):
            tbl.columns[i].width = cw

    for r_idx, row in enumerate(rows_data):
        for c_idx, cell_text in enumerate(row):
            cell = tbl.cell(r_idx, c_idx)
            cell.text = cell_text
            # styling via XML
            tc = cell._tc
            tcPr = tc.get_or_add_tcPr()

            # background
            if r_idx == 0 and header:
                bg_hex = rgb_hex(BG_CARD)
            elif r_idx % 2 == 0:
                bg_hex = rgb_hex(BG_CARD)
            else:
                bg_hex = "162131"

            solidFill = etree.SubElement(tcPr, '{http://schemas.openxmlformats.org/drawingml/2006/main}solidFill')
            srgb = etree.SubElement(solidFill, '{http://schemas.openxmlformats.org/drawingml/2006/main}srgbClr')
            srgb.set('val', bg_hex)

            # bottom border
            lnB = etree.SubElement(tcPr, '{http://schemas.openxmlformats.org/drawingml/2006/main}lnB',
                                   w="9525", cap="flat", cmpd="sng")
            sF2 = etree.SubElement(lnB, '{http://schemas.openxmlformats.org/drawingml/2006/main}solidFill')
            sC2 = etree.SubElement(sF2, '{http://schemas.openxmlformats.org/drawingml/2006/main}srgbClr')
            sC2.set('val', rgb_hex(BORDER))

            # text
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            if p.runs:
                run = p.runs[0]
            else:
                run = p.add_run()
                run.text = cell_text
            run.font.name = "Calibri"
            if r_idx == 0 and header:
                run.font.bold = True
                run.font.color.rgb = ORANGE
                run.font.size = Pt(11)
            else:
                run.font.bold = False
                run.font.color.rgb = TEXT
                run.font.size = Pt(12)
            p.alignment = PP_ALIGN.LEFT

    return tbl

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — TITLE
# ═════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
fill_slide(sl, BG)

# Vertical orange accent on left
add_rect(sl, 0, 0, Inches(0.12), H, ORANGE)

# Big red dot / icon area
add_rect(sl, Inches(0.55), Inches(1.8), Inches(0.5), Inches(0.5), ORANGE)

# Title
add_textbox(sl, Inches(0.55), Inches(2.5), Inches(9), Inches(1.4),
            "🔴  Mars Operations",
            font_size=Pt(52), bold=True, color=ORANGE, font_name="Calibri")

# Subtitle
add_textbox(sl, Inches(0.55), Inches(3.85), Inches(9), Inches(0.6),
            "Distributed IoT Automation Platform",
            font_size=Pt(26), color=TEXT, font_name="Calibri")

# Thin divider
add_rect(sl, Inches(0.55), Inches(4.55), Inches(6), Inches(0.03), ORANGE)

# Meta line
add_textbox(sl, Inches(0.55), Inches(4.7), Inches(9), Inches(0.4),
            "Lab of Advanced Programming 2025/2026  ·  Hackathon — March 2026",
            font_size=Pt(14), color=MUTED, font_name="Calibri")

# Pills area
card(sl, Inches(0.55), Inches(5.25), Inches(2.1), Inches(0.42), ORANGE)
add_textbox(sl, Inches(0.62), Inches(5.3), Inches(2.0), Inches(0.35),
            "Student ID: 2082600", font_size=Pt(13), bold=True, color=ORANGE)

card(sl, Inches(2.85), Inches(5.25), Inches(1.8), Inches(0.42), ORANGE)
add_textbox(sl, Inches(2.92), Inches(5.3), Inches(1.7), Inches(0.35),
            "Project: MarsTok", font_size=Pt(13), bold=True, color=ORANGE)

# Right side geometric deco
add_rect(sl, Inches(10.2), Inches(0.5), Inches(2.8), Inches(6.5), BG_CARD, BORDER)
add_rect(sl, Inches(10.2), Inches(0.5), Inches(2.8), Inches(0.06), ORANGE)
for i, (label, val) in enumerate([("Containers","8"),("Backend Services","3"),
                                    ("User Stories","20"),("Startup command","1"),
                                    ("Days to build","5")]):
    y_off = Inches(1.2 + i * 1.1)
    add_textbox(sl, Inches(10.4), y_off, Inches(2.4), Inches(0.5),
                val, font_size=Pt(36), bold=True, color=ORANGE, align=PP_ALIGN.CENTER)
    add_textbox(sl, Inches(10.4), y_off + Inches(0.45), Inches(2.4), Inches(0.3),
                label, font_size=Pt(10), color=MUTED, align=PP_ALIGN.CENTER)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — PROBLEM & SOLUTION
# ═════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
fill_slide(sl, BG)
add_title_bar(sl, "🚨  Problem & Solution")

# Quote box
add_rect(sl, Inches(0.55), Inches(1.05), Inches(12.23), Inches(0.72), BG_CARD, BORDER)
add_rect(sl, Inches(0.55), Inches(1.05), Inches(0.09), Inches(0.72), ORANGE)
add_textbox(sl, Inches(0.75), Inches(1.12), Inches(12.0), Inches(0.6),
            '"Mars 2036. Your automation stack is partially destroyed. Devices speak incompatible dialects.'
            ' Rebuild it — or face thermodynamic consequences."',
            font_size=Pt(13), italic=True, color=MUTED)

# Left column header
add_textbox(sl, Inches(0.55), Inches(1.92), Inches(5.9), Inches(0.38),
            "❌  The Challenge", font_size=Pt(15), bold=True, color=RGBColor(0xef,0x44,0x44))

challenges = [
    "15 devices,  8 raw JSON schemas,  two transport protocols",
    "REST polling + persistent SSE streams — no unified format",
    "Operators face a blank dashboard on page load",
    "Automation must fire without human intervention",
    "Configuration must survive service restarts",
]
for i, ch in enumerate(challenges):
    card(sl, Inches(0.55), Inches(2.38 + i*0.82), Inches(5.9), Inches(0.72),
         RGBColor(0xef,0x44,0x44))
    add_textbox(sl, Inches(0.75), Inches(2.47 + i*0.82), Inches(5.65), Inches(0.58),
                ch, font_size=Pt(12.5), color=TEXT)

# Right column header
add_textbox(sl, Inches(6.88), Inches(1.92), Inches(5.9), Inches(0.38),
            "✅  Our Solution", font_size=Pt(15), bold=True, color=GREEN)

solutions = [
    ("Unified  InternalEvent  normalisation layer", ORANGE),
    ("Event-driven pipeline via  RabbitMQ  fanout", ORANGE),
    ("IF-THEN rule engine — auto-triggers actuators", ORANGE),
    ("React dashboard with  live SSE push", ORANGE),
    ("Full Docker Compose IaC — one command start", ORANGE),
]
for i, (sol, acc) in enumerate(solutions):
    card(sl, Inches(6.88), Inches(2.38 + i*0.82), Inches(5.9), Inches(0.72), GREEN)
    add_textbox(sl, Inches(7.08), Inches(2.47 + i*0.82), Inches(5.65), Inches(0.58),
                sol, font_size=Pt(12.5), color=TEXT)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — SYSTEM ARCHITECTURE
# ═════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
fill_slide(sl, BG)
add_title_bar(sl, "🏗️  System Architecture")

arch_layers = [
    ("🔴  mars-iot-simulator :8080",
     "8 REST sensors (poll 5 s)  ·  7 SSE telemetry topics",
     RGBColor(0xef,0x44,0x44)),
    ("🔵  collector  — Python 3.12 asyncio",
     "polls + streams + normalises (8 schemas) + publishes",
     BLUE),
    ("🟣  RabbitMQ 3.13  — fanout exchange mars.events",
     "durable · persistent delivery",
     PURPLE),
    ("🟠  rules-engine  — Python 3.12 asyncio",
     "cache state → evaluate rules → actuate → persist alerts → publish",
     ORANGE),
    ("🩵  api — FastAPI :8000   |   🟢  frontend — React 18 :3000",
     "REST + SSE gateway  ·  7-page React SPA",
     CYAN),
]

arrow_labels = [
    "↓  HTTP GET every 5 s  +  SSE EventSource",
    "↓  AMQP PERSISTENT publish",
    "↓  exclusive anonymous queue consume",
    "↓  REST  ·  ↓  Redis  ·  ↓  PostgreSQL",
]

y_start = Inches(1.05)
box_h   = Inches(0.7)
arr_h   = Inches(0.35)
gap     = box_h + arr_h

for i, (title, sub, acc) in enumerate(arch_layers):
    y = y_start + i * gap
    card(sl, Inches(0.55), y, Inches(7.8), box_h, acc)
    add_textbox(sl, Inches(0.75), y + Inches(0.06), Inches(7.6), Inches(0.32),
                title, font_size=Pt(13), bold=True, color=WHITE)
    add_textbox(sl, Inches(0.75), y + Inches(0.36), Inches(7.6), Inches(0.28),
                sub, font_size=Pt(11), color=MUTED)
    if i < len(arrow_labels):
        add_textbox(sl, Inches(0.55), y + box_h, Inches(7.8), arr_h,
                    arrow_labels[i], font_size=Pt(11), color=ORANGE, align=PP_ALIGN.CENTER)

# Right: infrastructure sidebar
add_textbox(sl, Inches(9.0), Inches(1.0), Inches(3.9), Inches(0.38),
            "Infrastructure", font_size=Pt(15), bold=True, color=ORANGE_L)

infra = [
    ("📨 RabbitMQ 3.13", "fanout mars.events\ndurable · persistent", PURPLE),
    ("⚡ Redis 7", "state:{id} TTL=3600 s\npub/sub channels", CYAN),
    ("🐘 PostgreSQL 16", "rules + alerts tables\nJSONB · Alembic migrations", BLUE),
]
for i, (name, detail, acc) in enumerate(infra):
    y = Inches(1.5 + i * 1.7)
    card(sl, Inches(9.0), y, Inches(3.9), Inches(1.5), acc)
    add_textbox(sl, Inches(9.18), y + Inches(0.1), Inches(3.65), Inches(0.38),
                name, font_size=Pt(13), bold=True, color=WHITE)
    add_textbox(sl, Inches(9.18), y + Inches(0.46), Inches(3.65), Inches(0.8),
                detail, font_size=Pt(11.5), color=MUTED)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — DATA PIPELINE & UNIFIED SCHEMA
# ═════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
fill_slide(sl, BG)
add_title_bar(sl, "⚡  Data Pipeline & Unified Schema")

# Left — 7 steps
add_textbox(sl, Inches(0.55), Inches(1.05), Inches(5.8), Inches(0.35),
            "7-Step Pipeline", font_size=Pt(14), bold=True, color=ORANGE_L)

steps = [
    ("Ingest",   "Poll 8 REST sensors every 5 s; maintain 7 persistent SSE connections"),
    ("Normalise","8 raw schemas → 1 InternalEvent via dispatcher"),
    ("Publish",  "PERSISTENT to RabbitMQ fanout  mars.events"),
    ("Process",  "Write state:{id} to Redis TTL=1 h; evaluate all enabled rules"),
    ("Alert",    "POST actuator to simulator + INSERT PostgreSQL + PUBLISH Redis"),
    ("Stream",   "API subscribes Redis pub/sub → relays named SSE events"),
    ("Render",   "useSSE pre-fetches state on load, then merges live stream"),
]
for i, (num_label, desc) in enumerate(steps):
    y = Inches(1.5 + i * 0.73)
    # Step number badge
    add_rect(sl, Inches(0.55), y, Inches(0.36), Inches(0.38), ORANGE)
    add_textbox(sl, Inches(0.55), y + Inches(0.04), Inches(0.36), Inches(0.32),
                str(i+1), font_size=Pt(13), bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_textbox(sl, Inches(1.0), y, Inches(1.2), Inches(0.38),
                num_label, font_size=Pt(12.5), bold=True, color=WHITE)
    add_textbox(sl, Inches(2.25), y, Inches(4.1), Inches(0.38),
                desc, font_size=Pt(11.5), color=MUTED)

# Right — InternalEvent schema
add_textbox(sl, Inches(6.9), Inches(1.05), Inches(5.9), Inches(0.35),
            "InternalEvent Schema", font_size=Pt(14), bold=True, color=ORANGE_L)

schema_box = card(sl, Inches(6.9), Inches(1.5), Inches(5.9), Inches(4.0))
schema_lines = [
    '  "event_id":    "550e8400-...",',
    '  "timestamp":   "2026-03-06T12:00:00Z",',
    '  "source_id":   "greenhouse_temperature",',
    '  "source_type": "rest_sensor",',
    '  "category":    "environment",',
    '  "metrics": [',
    '    { "name": "value", "value": 22.5, "unit": "degC" }',
    '  ],',
    '  "status":     "ok | warning | null",',
    '  "raw_schema": "rest.scalar.v1"',
]
schema_text = "{\n" + "\n".join(schema_lines) + "\n}"
add_textbox(sl, Inches(7.05), Inches(1.6), Inches(5.6), Inches(3.8),
            schema_text, font_size=Pt(11), color=GREEN_C, font_name="Courier New")

# 8 schemas label
add_textbox(sl, Inches(6.9), Inches(5.62), Inches(5.9), Inches(0.28),
            "8 schemas handled:", font_size=Pt(11), bold=True, color=WHITE)
add_textbox(sl, Inches(6.9), Inches(5.92), Inches(5.9), Inches(0.45),
            "rest.scalar.v1  ·  rest.chemistry.v1  ·  rest.level.v1  ·  rest.particulate.v1\n"
            "topic.power.v1  ·  topic.environment.v1  ·  topic.thermal_loop.v1  ·  topic.airlock.v1",
            font_size=Pt(10.5), color=MUTED)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — AUTOMATION ENGINE
# ═════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
fill_slide(sl, BG)
add_title_bar(sl, "⚙️  Automation Engine")

# Left: Rule JSON
add_textbox(sl, Inches(0.55), Inches(1.05), Inches(6.0), Inches(0.35),
            "Rule Model", font_size=Pt(14), bold=True, color=ORANGE_L)

rule_json = '''{
  "name": "High Temp → Cooling Fan ON",
  "enabled": true,
  "condition": {
    "source_id": "greenhouse_temperature",
    "metric":    "value",
    "operator":  ">",
    "threshold": 35.0
  },
  "action": {
    "actuator_name": "cooling_fan",
    "state":         "ON"
  }
}'''

card(sl, Inches(0.55), Inches(1.48), Inches(6.0), Inches(2.85))
add_textbox(sl, Inches(0.7), Inches(1.56), Inches(5.75), Inches(2.7),
            rule_json, font_size=Pt(12), color=GREEN_C, font_name="Courier New")

# Evaluation note
card(sl, Inches(0.55), Inches(4.42), Inches(6.0), Inches(0.58), ORANGE)
add_textbox(sl, Inches(0.73), Inches(4.5), Inches(5.78), Inches(0.42),
            "🔁  Evaluated on every incoming event\n"
            "SELECT * FROM rules WHERE enabled = true",
            font_size=Pt(12), color=WHITE)

# Right: Operators + lifecycle table
add_textbox(sl, Inches(7.1), Inches(1.05), Inches(5.7), Inches(0.35),
            "Supported Operators", font_size=Pt(14), bold=True, color=ORANGE_L)

ops = [">  (gt)", "<  (lt)", ">=  (gte)", "<=  (lte)", "=  (eq)", "!=  (neq)"]
for i, op in enumerate(ops):
    col = i % 3
    row = i // 3
    bx = Inches(7.1 + col * 1.95)
    by = Inches(1.5 + row * 0.55)
    add_rect(sl, bx, by, Inches(1.75), Inches(0.42), BG_CARD, BORDER)
    add_rect(sl, bx, by, Inches(0.07), Inches(0.42), ORANGE)
    add_textbox(sl, bx + Inches(0.15), by + Inches(0.06), Inches(1.55), Inches(0.32),
                op, font_size=Pt(13), bold=True, color=ORANGE)

add_textbox(sl, Inches(7.1), Inches(2.72), Inches(5.7), Inches(0.35),
            "Rule Lifecycle (CRUD)", font_size=Pt(14), bold=True, color=ORANGE_L)

table_rows = [
    ["Action", "Endpoint", "US"],
    ["Create", "POST  /api/rules", "13"],
    ["List / Get", "GET  /api/rules", "14"],
    ["Edit", "PUT  /api/rules/{id}", "15"],
    ["Toggle", "PATCH  /api/rules/{id}/toggle", "16"],
    ["Delete", "DELETE  /api/rules/{id}", "17"],
]
col_ws = [Inches(1.2), Inches(3.2), Inches(0.7)]
add_table(sl, Inches(7.1), Inches(3.1), Inches(5.7 - 0.27), table_rows, col_ws)

card(sl, Inches(7.1), Inches(5.62), Inches(5.58), Inches(0.58), GREEN)
add_textbox(sl, Inches(7.28), Inches(5.7), Inches(5.35), Inches(0.42),
            "✅  Persisted in PostgreSQL — survive  docker compose down\n"
            "     Alembic migration runs automatically on every boot",
            font_size=Pt(11.5), color=WHITE)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — FRONTEND DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
fill_slide(sl, BG)
add_title_bar(sl, "🖥️  Frontend Dashboard — 7 Pages")

table_rows = [
    ["Page", "Key Features", "User Stories"],
    ["Dashboard",      "All sensor cards · live SSE · ok/warning status badges",                        "1, 2, 3, 4"],
    ["Power",          "6 live Recharts line charts (solar array, power bus, consumption)",              "5"],
    ["Environment",    "Radiation + life support cards at top · REST sensor widgets below",              "6, 9, 10"],
    ["Airlock&Thermal","State badge IDLE / PRESSURIZING / DEPRESSURIZING · thermal charts",              "7, 8"],
    ["Actuators",      "ON/OFF toggle cards for all 4 actuators · 5 s auto-refresh",                    "11, 12"],
    ["Rules",          "RuleForm dialog + RuleTable · full CRUD + enable/disable toggle",                "13–18"],
    ["Alerts",         "Timeline · rule/source dropdowns · SSE live prepend · pagination",               "19, 20"],
]
col_ws = [Inches(1.65), Inches(8.25), Inches(1.5)]
add_table(sl, Inches(0.55), Inches(1.05), Inches(12.23), table_rows, col_ws)

add_textbox(sl, Inches(0.55), Inches(5.08), Inches(12.23), Inches(0.35),
            "Real-time Data Flow", font_size=Pt(14), bold=True, color=ORANGE_L)

flow_items = [
    ("Page load", WHITE),
    ("GET /api/state/\n(pre-fetch)", CYAN),
    ("EventSource /api/stream\n(persistent SSE)", ORANGE),
    ("sensor_update\n(update state)", GREEN),
    ("alert\n(prepend list)", AMBER),
    ("3 s auto-reconnect\non disconnect", BLUE),
]
arrow_x = Inches(0.55)
for i, (label, col) in enumerate(flow_items):
    bw = Inches(1.88)
    bx = arrow_x + i * (bw + Inches(0.22))
    add_rect(sl, bx, Inches(5.5), bw, Inches(0.78), BG_CARD, BORDER)
    add_rect(sl, bx, Inches(5.5), Inches(0.07), Inches(0.78), col)
    add_textbox(sl, bx + Inches(0.14), Inches(5.56), bw - Inches(0.2), Inches(0.68),
                label, font_size=Pt(10.5), color=col, align=PP_ALIGN.CENTER)
    if i < len(flow_items) - 1:
        add_textbox(sl, bx + bw + Inches(0.01), Inches(5.75), Inches(0.2), Inches(0.35),
                    "→", font_size=Pt(16), bold=True, color=ORANGE, align=PP_ALIGN.CENTER)

add_textbox(sl, Inches(0.55), Inches(6.38), Inches(12.23), Inches(0.28),
            "React 18 · TypeScript · Vite · TailwindCSS · Recharts · lucide-react · react-router-dom v6",
            font_size=Pt(11), color=MUTED, align=PP_ALIGN.CENTER)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — TECHNOLOGY STACK
# ═════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
fill_slide(sl, BG)
add_title_bar(sl, "🔧  Technology Stack")

table_rows = [
    ["Layer", "Technology"],
    ["Ingestion",       "Python 3.12 · asyncio · httpx · aio-pika · pydantic v2"],
    ["Message Broker",  "RabbitMQ 3.13 · fanout exchange · durable · persistent delivery"],
    ["Processing",      "Python 3.12 · SQLAlchemy 2 async · asyncpg · alembic · httpx"],
    ["State Cache",     "Redis 7 · state:{id} TTL=3600 s · pub/sub channels"],
    ["Database",        "PostgreSQL 16 · rules + alerts tables · JSONB columns"],
    ["API Gateway",     "FastAPI · Uvicorn · sse-starlette · CORS middleware · pydantic v2"],
    ["Frontend",        "React 18 · TypeScript · Vite · TailwindCSS · Recharts · lucide-react"],
    ["IaC / Serving",   "Docker Compose · nginx · 8 containers · named volumes · healthchecks"],
]
col_ws = [Inches(2.0), Inches(10.23)]
add_table(sl, Inches(0.55), Inches(1.05), Inches(12.23), table_rows, col_ws)

# Stat strip
stats = [("8","Containers"),("3","Backend Services"),
         ("20","User Stories"),("1","docker compose up"),("5","Days")]
sw = Inches(12.23 / len(stats))
for i, (num, lbl) in enumerate(stats):
    bx = Inches(0.55) + i * sw
    add_rect(sl, bx + Inches(0.06), Inches(5.72), sw - Inches(0.12), Inches(0.98), BG_CARD, BORDER)
    add_textbox(sl, bx + Inches(0.06), Inches(5.8), sw - Inches(0.12), Inches(0.45),
                num, font_size=Pt(28), bold=True, color=ORANGE, align=PP_ALIGN.CENTER)
    add_textbox(sl, bx + Inches(0.06), Inches(6.25), sw - Inches(0.12), Inches(0.32),
                lbl, font_size=Pt(10), color=MUTED, align=PP_ALIGN.CENTER)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — INFRASTRUCTURE AS CODE
# ═════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
fill_slide(sl, BG)
add_title_bar(sl, "🐳  Infrastructure as Code")

# Left
add_textbox(sl, Inches(0.55), Inches(1.05), Inches(6.2), Inches(0.35),
            "One Command Start", font_size=Pt(14), bold=True, color=ORANGE_L)

bash_code = ("# One-time: load the simulator OCI image\n"
             "./source/load-image.sh\n\n"
             "# Start the entire platform\n"
             "cd source && docker compose up")
card(sl, Inches(0.55), Inches(1.48), Inches(6.2), Inches(1.42))
add_textbox(sl, Inches(0.7), Inches(1.55), Inches(5.95), Inches(1.3),
            bash_code, font_size=Pt(12.5), color=GREEN_C, font_name="Courier New")

add_textbox(sl, Inches(0.55), Inches(3.05), Inches(6.2), Inches(0.35),
            "Startup Dependency Chain", font_size=Pt(14), bold=True, color=ORANGE_L)

chain = [
    ("🟣 rabbitmq  ⚡ redis  🐘 postgres  🔴 simulator", PURPLE),
    ("🔵 collector   🟠 rules-engine", BLUE),
    ("🩵 api  :8000", CYAN),
    ("🟢 frontend  :3000", GREEN),
]
for i, (lbl, acc) in enumerate(chain):
    y = Inches(3.5 + i * 0.73)
    card(sl, Inches(0.55), y, Inches(6.2), Inches(0.58), acc)
    add_textbox(sl, Inches(0.73), y + Inches(0.1), Inches(6.0), Inches(0.38),
                lbl, font_size=Pt(12.5), color=WHITE, align=PP_ALIGN.CENTER)
    if i < len(chain) - 1:
        add_textbox(sl, Inches(2.5), y + Inches(0.58), Inches(1.5), Inches(0.2),
                    "↓  condition: service_healthy", font_size=Pt(9.5), color=MUTED,
                    align=PP_ALIGN.CENTER)

# Right
add_textbox(sl, Inches(7.2), Inches(1.05), Inches(5.5), Inches(0.35),
            "Named Volumes", font_size=Pt(14), bold=True, color=ORANGE_L)

volumes = [
    ("🗄️  pg_data",
     "Rules + alerts persist across restarts\nUS 18 — rule persistence", ORANGE),
    ("📨  rabbitmq_data",
     "Durable messages survive broker restart", ORANGE),
    ("⚡  redis_data",
     "Cache repopulates within seconds on loss", ORANGE),
]
for i, (name, desc, acc) in enumerate(volumes):
    y = Inches(1.5 + i * 1.42)
    card(sl, Inches(7.2), y, Inches(5.5), Inches(1.25), acc)
    add_textbox(sl, Inches(7.38), y + Inches(0.1), Inches(5.25), Inches(0.35),
                name, font_size=Pt(13), bold=True, color=WHITE)
    add_textbox(sl, Inches(7.38), y + Inches(0.45), Inches(5.25), Inches(0.7),
                desc, font_size=Pt(12), color=MUTED)

card(sl, Inches(7.2), Inches(5.78), Inches(5.5), Inches(0.52), ORANGE)
add_textbox(sl, Inches(7.38), Inches(5.86), Inches(5.3), Inches(0.38),
            "No manual steps after  docker compose up\n"
            "Alembic migrations run automatically on boot",
            font_size=Pt(12), color=WHITE)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — LESSONS LEARNED
# ═════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
fill_slide(sl, BG)
add_title_bar(sl, "💡  Lessons Learned")

add_textbox(sl, Inches(0.55), Inches(1.05), Inches(6.2), Inches(0.35),
            "⚠️  Challenges", font_size=Pt(14), bold=True, color=AMBER)

challenges2 = [
    ("Schema diversity",
     "8 raw formats → dispatcher pattern; each schema maps to its own handler function."),
    ("SSE double reconnection",
     "Both collector (→ simulator) and frontend (→ API) needed independent 3 s auto-retry loops."),
    ("Blank dashboard on load",
     "Opening SSE first = empty cards for 5 s. Fix: pre-fetch GET /api/state/ before EventSource."),
    ("JSONB alert filtering",
     "Used PostgreSQL @> containment operator to filter source_id inside stored JSONB events."),
]
for i, (title, desc) in enumerate(challenges2):
    y = Inches(1.5 + i * 1.3)
    card(sl, Inches(0.55), y, Inches(6.2), Inches(1.15), AMBER)
    add_textbox(sl, Inches(0.73), y + Inches(0.08), Inches(5.95), Inches(0.35),
                title, font_size=Pt(13), bold=True, color=WHITE)
    add_textbox(sl, Inches(0.73), y + Inches(0.45), Inches(5.95), Inches(0.65),
                desc, font_size=Pt(12), color=MUTED)

add_textbox(sl, Inches(7.15), Inches(1.05), Inches(5.7), Inches(0.35),
            "✅  Design Decisions", font_size=Pt(14), bold=True, color=GREEN)

decisions = [
    ("Fanout exchange",
     "Collector publishes once → any consumer binds its own queue. Zero changes to add a new service."),
    ("Redis pub/sub relay",
     "True zero-latency push from rules-engine to API SSE clients — no polling needed."),
    ("Alembic on boot",
     "alembic upgrade head runs at rules-engine startup — schema always in sync, no manual step."),
    ("Exclusive anonymous queues",
     "No stale messages accumulate on consumer restart. Broker stays clean automatically."),
]
for i, (title, desc) in enumerate(decisions):
    y = Inches(1.5 + i * 1.3)
    card(sl, Inches(7.15), y, Inches(5.7), Inches(1.15), GREEN)
    add_textbox(sl, Inches(7.33), y + Inches(0.08), Inches(5.45), Inches(0.35),
                title, font_size=Pt(13), bold=True, color=WHITE)
    add_textbox(sl, Inches(7.33), y + Inches(0.45), Inches(5.45), Inches(0.65),
                desc, font_size=Pt(12), color=MUTED)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — LIVE DEMO
# ═════════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
fill_slide(sl, BG)
add_title_bar(sl, "🎬  Live Demo")

# Left: demo script
add_textbox(sl, Inches(0.55), Inches(1.05), Inches(7.2), Inches(0.35),
            "Demo Script", font_size=Pt(14), bold=True, color=ORANGE_L)

demo_steps = [
    ("docker compose up",
     "— watch all 8 containers reach healthy state"),
    ("Dashboard",
     "— cards populate instantly (US 4 pre-fetch); values update every 5 s"),
    ("Power page",
     "— 6 live line charts; rolling window updating in real-time"),
    ("Actuators",
     "— manually toggle  cooling_fan  ON → OFF; verify optimistic update"),
    ("Rules",
     "— create:  greenhouse_temperature > 28 → cooling_fan ON"),
    ("Alerts page",
     "— alert appears live; filter by rule and source dropdowns"),
    ("Persistence",
     "— docker compose down && docker compose up → rules still there ✅ (US 18)"),
]
for i, (label, desc) in enumerate(demo_steps):
    y = Inches(1.5 + i * 0.69)
    add_rect(sl, Inches(0.55), y + Inches(0.04), Inches(0.34), Inches(0.34), ORANGE)
    add_textbox(sl, Inches(0.55), y + Inches(0.04), Inches(0.34), Inches(0.34),
                str(i+1), font_size=Pt(12), bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_textbox(sl, Inches(1.0), y, Inches(1.65), Inches(0.38),
                label, font_size=Pt(12), bold=True, color=WHITE)
    add_textbox(sl, Inches(2.7), y, Inches(5.05), Inches(0.38),
                desc, font_size=Pt(12), color=MUTED)

# Right: endpoints + stats
add_textbox(sl, Inches(8.3), Inches(1.05), Inches(4.5), Inches(0.35),
            "Endpoints", font_size=Pt(14), bold=True, color=ORANGE_L)

endpoints = [
    ("🖥️  http://localhost:3000",       "React dashboard", CYAN),
    ("📖  http://localhost:8000/docs",   "FastAPI interactive docs", BLUE),
    ("📨  http://localhost:15672",       "RabbitMQ Management UI  (guest / guest)", PURPLE),
]
for i, (url, label, acc) in enumerate(endpoints):
    y = Inches(1.5 + i * 1.1)
    card(sl, Inches(8.3), y, Inches(4.5), Inches(0.92), acc)
    add_textbox(sl, Inches(8.48), y + Inches(0.08), Inches(4.28), Inches(0.38),
                url, font_size=Pt(12), bold=True, color=acc, font_name="Courier New")
    add_textbox(sl, Inches(8.48), y + Inches(0.52), Inches(4.28), Inches(0.3),
                label, font_size=Pt(11), color=MUTED)

# Stat row
stats2 = [("20","User Stories"),("8","Containers"),("5","Days")]
sw2 = Inches(4.5 / 3)
for i, (num, lbl) in enumerate(stats2):
    bx = Inches(8.3) + i * sw2
    add_rect(sl, bx + Inches(0.06), Inches(4.88), sw2 - Inches(0.12), Inches(0.78), BG_CARD, BORDER)
    add_textbox(sl, bx + Inches(0.06), Inches(4.96), sw2 - Inches(0.12), Inches(0.4),
                num, font_size=Pt(24), bold=True, color=ORANGE, align=PP_ALIGN.CENTER)
    add_textbox(sl, bx + Inches(0.06), Inches(5.36), sw2 - Inches(0.12), Inches(0.25),
                lbl, font_size=Pt(10), color=MUTED, align=PP_ALIGN.CENTER)

# Closing banner
add_rect(sl, Inches(8.3), Inches(5.85), Inches(4.5), Inches(0.68), ORANGE)
add_textbox(sl, Inches(8.3), Inches(5.92), Inches(4.5), Inches(0.52),
            "1 command  ·  0 manual setup  ·  No blank screens.",
            font_size=Pt(13.5), bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# ─────────────────────────────────────────────────────────────────────────────
out = "/Users/davide/Desktop/Mars/presentation_editable.pptx"
prs.save(out)
print(f"Saved → {out}")
