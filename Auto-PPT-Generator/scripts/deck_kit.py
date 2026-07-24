"""deck_kit.py — core drawing helpers for Auto-PPT-Generator.

Everything that touches python-pptx primitives lives here so the builders in
builders.py stay declarative. The guiding idea is the same one that keeps
lecture decks from breaking: every element is placed in a *fixed region* (an
inch-based box), text word-wraps inside it, and callers respect the character
budgets documented in references/slide_types.md. That is what prevents overlap
and clipping — not luck.
"""

from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

# 16:9 canvas (13.333 x 7.5 inches). All layout math below is in inches.
SLIDE_W_IN = 13.333
SLIDE_H_IN = 7.5

# ---------------------------------------------------------------------------
# Themes. Colors are plain hex strings (no leading #). Business-neutral by
# default; swap the active theme via the deck config. A theme is just a lookup
# table so adding one is cheap.
# ---------------------------------------------------------------------------
THEMES = {
    "corporate": {
        "bg": "FFFFFF", "surface": "F2F5F9", "surface_alt": "E8EDF4",
        "primary": "1F3A5F", "primary_soft": "3D5A80", "accent": "2E8B8B",
        "text": "1A1F2B", "muted": "667085", "line": "D7DEE8",
        "on_primary": "FFFFFF", "good": "2E8B57", "warn": "C77D2E", "bad": "B3453B",
    },
    "dark": {
        "bg": "10151F", "surface": "1B2331", "surface_alt": "232E40",
        "primary": "4EA8DE", "primary_soft": "3B7FB0", "accent": "5BD1B0",
        "text": "EAF0F7", "muted": "9AA7B8", "line": "2E3A4D",
        "on_primary": "0B0F17", "good": "5BD1B0", "warn": "E0B15A", "bad": "E27A6E",
    },
    "minimal": {
        "bg": "FFFFFF", "surface": "F7F7F7", "surface_alt": "EDEDED",
        "primary": "111111", "primary_soft": "444444", "accent": "C8A24B",
        "text": "111111", "muted": "808080", "line": "E0E0E0",
        "on_primary": "FFFFFF", "good": "3B7A57", "warn": "B08A2E", "bad": "A8443B",
    },
}

# Categorical palette for charts (kept readable in both light and dark).
CHART_PALETTE = ["1F3A5F", "2E8B8B", "C77D2E", "6C8EAD", "8E7CC3", "5FA45F"]

_DEFAULT_FONT = "Malgun Gothic"  # renders both Latin and Korean on Windows/Mac


def set_default_font(name):
    global _DEFAULT_FONT
    if name:
        _DEFAULT_FONT = name


# ---------------------------------------------------------------------------
# Low-level primitives
# ---------------------------------------------------------------------------
def rgb(hex_str):
    return RGBColor.from_string(hex_str)


_ALIGN = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER,
          "right": PP_ALIGN.RIGHT, "justify": PP_ALIGN.JUSTIFY}
_ANCHOR = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE, "bottom": MSO_ANCHOR.BOTTOM}


def _set_run_font(run, name):
    """Set Latin + East Asian + complex-script typeface so Korean glyphs use
    the same family instead of falling back to a default."""
    run.font.name = name
    rPr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        existing = rPr.find(qn(tag))
        if existing is not None:
            rPr.remove(existing)
    for tag in ("a:ea", "a:cs"):
        el = rPr.makeelement(qn(tag), {"typeface": name})
        rPr.append(el)


def background(slide, hex_str):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = rgb(hex_str)


def rect(slide, box, fill=None, line=None, line_w=1.0, rounded=False,
         radius=0.08, shadow=False):
    """Draw a rectangle. `box` is (left, top, width, height) in inches."""
    l, t, w, h = box
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    sp = slide.shapes.add_shape(shape_type, Inches(l), Inches(t), Inches(w), Inches(h))
    if rounded:
        try:
            sp.adjustments[0] = radius
        except Exception:
            pass
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid()
        sp.fill.fore_color.rgb = rgb(fill)
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = rgb(line)
        sp.line.width = Pt(line_w)
    sp.shadow.inherit = False
    if not shadow:
        # explicit no-shadow; python-pptx has no clean setter so leave inherited off
        pass
    return sp


def text(slide, box, lines, align="left", anchor="top", wrap=True, shrink=False):
    """Place a text block. `lines` is a list of paragraph specs.

    A paragraph spec is a dict: {text, size, bold, italic, color, name,
    align, space_before, space_after, level, bullet}. Alternatively pass
    {"runs": [{text,...}, ...]} to mix styles within one line.
    """
    l, t, w, h = box
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = _ANCHOR.get(anchor, MSO_ANCHOR.TOP)
    if shrink:
        tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    for m in ("margin_left", "margin_right"):
        setattr(tf, m, Inches(0.04))
    for m in ("margin_top", "margin_bottom"):
        setattr(tf, m, Inches(0.02))

    for i, spec in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = _ALIGN.get(spec.get("align", align), _ALIGN[align if align in _ALIGN else "left"])
        if spec.get("space_before") is not None:
            p.space_before = Pt(spec["space_before"])
        if spec.get("space_after") is not None:
            p.space_after = Pt(spec["space_after"])
        if spec.get("level"):
            p.level = spec["level"]
        runs = spec.get("runs") or [spec]
        bullet = spec.get("bullet")
        for j, r in enumerate(runs):
            run = p.add_run()
            prefix = ("•  " if bullet is True else f"{bullet}  ") if (bullet and j == 0) else ""
            run.text = prefix + str(r.get("text", ""))
            run.font.size = Pt(r.get("size", 16))
            run.font.bold = bool(r.get("bold", False))
            run.font.italic = bool(r.get("italic", False))
            run.font.color.rgb = rgb(r.get("color", "1A1F2B"))
            _set_run_font(run, r.get("name", _DEFAULT_FONT))
    return tb


def table(slide, box, columns, rows, theme, col_widths=None,
          first_col_accent=False, font_size=13, header_size=13):
    """Render a data table with a themed header row and zebra body rows."""
    l, t, w, h = box
    n_rows = len(rows) + 1
    n_cols = len(columns)
    gf = slide.shapes.add_table(n_rows, n_cols, Inches(l), Inches(t), Inches(w), Inches(h))
    tbl = gf.table
    # column widths
    if col_widths and len(col_widths) == n_cols:
        total = float(sum(col_widths))
        for c, cw in enumerate(col_widths):
            tbl.columns[c].width = Inches(w * (cw / total))
    # header
    for c, label in enumerate(columns):
        cell = tbl.cell(0, c)
        _style_cell(cell, str(label), theme["primary"], theme["on_primary"],
                    bold=True, size=header_size,
                    align="left" if c == 0 else "center")
    # body
    for r, row in enumerate(rows, start=1):
        band = theme["bg"] if r % 2 else theme["surface"]
        for c in range(n_cols):
            val = row[c] if c < len(row) else ""
            is_accent = first_col_accent and c == 0
            _style_cell(
                tbl.cell(r, c), str(val), band,
                theme["primary"] if is_accent else theme["text"],
                bold=is_accent, size=font_size,
                align="left" if c == 0 else "center",
            )
    return gf


def _style_cell(cell, value, fill, color, bold=False, size=13, align="left"):
    cell.fill.solid()
    cell.fill.fore_color.rgb = rgb(fill)
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    cell.margin_left = Inches(0.12)
    cell.margin_right = Inches(0.08)
    cell.margin_top = Inches(0.03)
    cell.margin_bottom = Inches(0.03)
    tf = cell.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = _ALIGN.get(align, PP_ALIGN.LEFT)
    run = p.add_run()
    run.text = value
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = rgb(color)
    _set_run_font(run, _DEFAULT_FONT)


def chart(slide, box, chart_type, categories, series, theme,
          legend=True, data_labels=False):
    """Add a native (editable) chart. `series` is a list of
    {"name": str, "values": [..]}. Colors come from CHART_PALETTE."""
    from pptx.chart.data import CategoryChartData
    from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

    l, t, w, h = box
    cd = CategoryChartData()
    cd.categories = categories
    for s in series:
        cd.add_series(s.get("name", ""), tuple(s.get("values", [])))

    kind = {
        "bar": XL_CHART_TYPE.COLUMN_CLUSTERED,
        "bar_h": XL_CHART_TYPE.BAR_CLUSTERED,
        "line": XL_CHART_TYPE.LINE_MARKERS,
        "pie": XL_CHART_TYPE.PIE,
        "area": XL_CHART_TYPE.AREA,
        "stacked": XL_CHART_TYPE.COLUMN_STACKED,
    }.get(chart_type, XL_CHART_TYPE.COLUMN_CLUSTERED)

    gf = slide.shapes.add_chart(kind, Inches(l), Inches(t), Inches(w), Inches(h), cd)
    ch = gf.chart
    ch.has_title = False
    ch.has_legend = legend and chart_type != "pie" or (chart_type == "pie" and legend)
    if ch.has_legend:
        ch.legend.position = XL_LEGEND_POSITION.BOTTOM
        ch.legend.include_in_layout = False
        ch.legend.font.size = Pt(11)
        ch.legend.font.color.rgb = rgb(theme["muted"])

    plot = ch.plots[0]
    plot.has_data_labels = data_labels
    if data_labels:
        plot.data_labels.font.size = Pt(10)
        plot.data_labels.font.color.rgb = rgb(theme["text"])

    if chart_type == "pie":
        # color each slice from the palette
        pts = plot.series[0].points
        for i, pt in enumerate(pts):
            pt.format.fill.solid()
            pt.format.fill.fore_color.rgb = rgb(CHART_PALETTE[i % len(CHART_PALETTE)])
    else:
        for i, s in enumerate(ch.series):
            s.format.fill.solid()
            s.format.fill.fore_color.rgb = rgb(CHART_PALETTE[i % len(CHART_PALETTE)])
        # axis styling
        try:
            for ax in (ch.category_axis, ch.value_axis):
                ax.tick_labels.font.size = Pt(10)
                ax.tick_labels.font.color.rgb = rgb(theme["muted"])
                ax.format.line.color.rgb = rgb(theme["line"])
        except Exception:
            pass
    return ch


def picture(slide, box, path, mode="fit"):
    """Place an image inside `box`. mode='fit' preserves aspect ratio and
    centers; 'fill' stretches to the box."""
    import os
    l, t, w, h = box
    if not path or not os.path.exists(path):
        # graceful placeholder so a missing asset never crashes the deck
        return None
    if mode == "fill":
        return slide.shapes.add_picture(path, Inches(l), Inches(t), Inches(w), Inches(h))
    pic = slide.shapes.add_picture(path, Inches(l), Inches(t))
    scale = min((w * 914400) / pic.width, (h * 914400) / pic.height)
    pic.width = int(pic.width * scale)
    pic.height = int(pic.height * scale)
    pic.left = Inches(l) + int((Inches(w) - pic.width) / 2)
    pic.top = Inches(t) + int((Inches(h) - pic.height) / 2)
    return pic
