"""builders.py — one builder per slide type.

Each builder is declarative: it reads a slide dict `d` and paints fixed regions
via deck_kit helpers. Builders never compute page numbers or footers — the
engine owns those so every deck stays consistent. To add a slide type, write a
`build_x(slide, d, ctx)` and register it in REGISTRY at the bottom.

`ctx` carries: ctx.T (theme colors), ctx.font, ctx.footer.
"""

import deck_kit as dk

# Shared layout grid (inches). Keeping these in one place is what makes every
# slide feel like part of the same deck.
MX = 0.9                         # side margin
CW = dk.SLIDE_W_IN - 2 * MX      # content width (~11.53)
TITLE_TOP = 0.6
BODY_TOP = 1.85


# ---------------------------------------------------------------------------
# Shared chrome
# ---------------------------------------------------------------------------
def _title(slide, ctx, title, eyebrow=None):
    T = ctx.T
    if eyebrow:
        dk.text(slide, (MX, TITLE_TOP - 0.02, CW, 0.3),
                [{"text": eyebrow.upper(), "size": 12, "bold": True, "color": T["accent"]}])
        y = TITLE_TOP + 0.32
    else:
        y = TITLE_TOP
    dk.text(slide, (MX, y, CW, 0.85),
            [{"text": title, "size": 28, "bold": True, "color": T["primary"]}],
            anchor="top")
    dk.rect(slide, (MX, y + 0.82, 1.0, 0.055), fill=T["accent"])


def add_footer(slide, ctx, page=None):
    T = ctx.T
    if ctx.footer:
        dk.text(slide, (MX, 7.06, 8.0, 0.3),
                [{"text": ctx.footer, "size": 9, "color": T["muted"]}], anchor="middle")
    if page is not None:
        dk.text(slide, (dk.SLIDE_W_IN - MX - 1.5, 7.06, 1.5, 0.3),
                [{"text": str(page), "size": 9, "color": T["muted"], "align": "right"}],
                anchor="middle", align="right")


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------
def build_cover(slide, d, ctx):
    T = ctx.T
    dk.background(slide, T["primary"])
    # accent rule
    dk.rect(slide, (MX, 3.05, 1.4, 0.09), fill=T["accent"])
    dk.text(slide, (MX, 2.0, CW, 1.0),
            [{"text": d.get("eyebrow", ""), "size": 15, "bold": True, "color": T["accent"]}])
    dk.text(slide, (MX, 3.35, CW, 1.7),
            [{"text": d.get("title", ""), "size": 44, "bold": True, "color": T["on_primary"]}],
            anchor="top")
    if d.get("subtitle"):
        dk.text(slide, (MX, 5.0, CW, 0.7),
                [{"text": d["subtitle"], "size": 18, "color": "D8E1EC"}])
    meta = d.get("meta") or []
    if meta:
        dk.text(slide, (MX, 6.35, CW, 0.6),
                [{"text": "   |   ".join(str(m) for m in meta), "size": 12, "color": "AEBED0"}])


def build_section(slide, d, ctx):
    T = ctx.T
    dk.background(slide, T["surface"])
    dk.rect(slide, (0, 0, 0.28, dk.SLIDE_H_IN), fill=T["primary"])
    num = d.get("number")
    if num is not None:
        dk.text(slide, (MX, 2.3, CW, 1.2),
                [{"text": str(num).zfill(2) if str(num).isdigit() else str(num),
                  "size": 60, "bold": True, "color": T["surface_alt"]}])
    dk.text(slide, (MX, 3.5, CW, 1.1),
            [{"text": d.get("title", ""), "size": 34, "bold": True, "color": T["primary"]}])
    if d.get("subtitle"):
        dk.text(slide, (MX, 4.7, CW, 0.8),
                [{"text": d["subtitle"], "size": 16, "color": T["muted"]}])


def build_agenda(slide, d, ctx):
    T = ctx.T
    dk.background(slide, T["bg"])
    _title(slide, ctx, d.get("title", "Agenda"), d.get("eyebrow"))
    items = d.get("items", [])
    n = max(len(items), 1)
    row_h = min(0.95, (7.0 - BODY_TOP) / n)
    y = BODY_TOP
    for i, it in enumerate(items, start=1):
        if isinstance(it, str):
            it = {"title": it}
        dk.text(slide, (MX, y, 0.7, row_h),
                [{"text": str(it.get("no", i)).zfill(2), "size": 20, "bold": True,
                  "color": T["accent"]}], anchor="middle")
        lines = [{"text": it.get("title", ""), "size": 17, "bold": True, "color": T["text"]}]
        if it.get("desc"):
            lines.append({"text": it["desc"], "size": 12, "color": T["muted"], "space_before": 2})
        dk.text(slide, (MX + 0.75, y, CW - 0.75, row_h), lines, anchor="middle")
        dk.rect(slide, (MX, y + row_h - 0.02, CW, 0.012), fill=T["line"])
        y += row_h


def build_summary(slide, d, ctx):
    T = ctx.T
    dk.background(slide, T["bg"])
    _title(slide, ctx, d.get("title", "Executive Summary"), d.get("eyebrow"))
    if d.get("lead"):
        dk.text(slide, (MX, BODY_TOP, CW, 1.2),
                [{"text": d["lead"], "size": 16, "color": T["text"]}], anchor="top")
    points = d.get("points", [])
    n = max(len(points), 1)
    top = BODY_TOP + (1.35 if d.get("lead") else 0.1)
    gap = 0.35
    card_w = (CW - gap * (n - 1)) / n if n <= 4 else CW
    if n <= 4:
        for i, p in enumerate(points):
            if isinstance(p, str):
                p = {"title": p}
            x = MX + i * (card_w + gap)
            dk.rect(slide, (x, top, card_w, 3.3), fill=T["surface"], rounded=True, radius=0.05)
            dk.rect(slide, (x, top, card_w, 0.12), fill=dk.CHART_PALETTE[i % len(dk.CHART_PALETTE)],
                    rounded=True, radius=0.5)
            lines = [{"text": p.get("title", ""), "size": 15, "bold": True, "color": T["primary"],
                      "space_after": 6}]
            if p.get("desc"):
                lines.append({"text": p["desc"], "size": 12.5, "color": T["muted"]})
            dk.text(slide, (x + 0.25, top + 0.35, card_w - 0.5, 2.7), lines)
    else:
        _bullet_list(slide, ctx, points, (MX, top, CW, 6.9 - top))


def _display_width(s):
    """Approximate rendered width in 'narrow-char' units. CJK/fullwidth glyphs
    take roughly twice the width of a Latin digit, so count them as 2."""
    return sum(2 if ord(c) >= 0x1100 else 1 for c in str(s))


def _fit_size(s, width_in, candidates=(40, 34, 28, 22)):
    """Largest candidate point size whose glyphs fit `width_in` inches on one
    line. k is inches per (narrow-unit · point), tuned against real renders."""
    w = _display_width(s)
    k = 0.0075
    for size in candidates:
        if w * k * size <= width_in:
            return size
    return candidates[-1]


def build_kpi(slide, d, ctx):
    T = ctx.T
    dk.background(slide, T["bg"])
    _title(slide, ctx, d.get("title", "Key Metrics"), d.get("eyebrow"))
    tiles = d.get("tiles", [])[:4]
    n = max(len(tiles), 1)
    gap = 0.4
    tile_w = (CW - gap * (n - 1)) / n
    top = BODY_TOP + 0.3
    tile_h = 2.9
    trend_color = {"up": T["good"], "down": T["bad"], "flat": T["muted"]}
    for i, tl in enumerate(tiles):
        x = MX + i * (tile_w + gap)
        dk.rect(slide, (x, top, tile_w, tile_h), fill=T["surface"], rounded=True, radius=0.05)
        dk.text(slide, (x + 0.28, top + 0.3, tile_w - 0.56, 0.5),
                [{"text": tl.get("label", ""), "size": 13, "bold": True, "color": T["muted"]}])
        val = str(tl.get("value", ""))
        vsize = _fit_size(val, tile_w - 0.56)
        dk.text(slide, (x + 0.28, top + 0.8, tile_w - 0.56, 1.2),
                [{"text": val, "size": vsize, "bold": True, "color": T["primary"]}],
                anchor="middle", wrap=False)
        if tl.get("delta"):
            tr = tl.get("trend", "flat")
            arrow = {"up": "▲ ", "down": "▼ ", "flat": ""}.get(tr, "")
            dk.text(slide, (x + 0.28, top + 2.05, tile_w - 0.56, 0.5),
                    [{"text": arrow + str(tl["delta"]), "size": 14, "bold": True,
                      "color": trend_color.get(tr, T["muted"])}])
        if tl.get("note"):
            dk.text(slide, (x + 0.28, top + 2.45, tile_w - 0.56, 0.35),
                    [{"text": tl["note"], "size": 10.5, "color": T["muted"]}])


def build_bullets(slide, d, ctx):
    T = ctx.T
    dk.background(slide, T["bg"])
    _title(slide, ctx, d.get("title", ""), d.get("eyebrow"))
    top = BODY_TOP
    if d.get("lead"):
        dk.text(slide, (MX, top, CW, 0.9),
                [{"text": d["lead"], "size": 16, "italic": True, "color": T["primary_soft"]}])
        top += 1.0
    _bullet_list(slide, ctx, d.get("bullets", []), (MX, top, CW, 6.85 - top))


def _bullet_list(slide, ctx, bullets, box):
    T = ctx.T
    l, t, w, h = box
    n = max(len(bullets), 1)
    row_h = min(0.9, h / n)
    y = t
    for b in bullets:
        if isinstance(b, str):
            b = {"text": b}
        lines = [{"text": b.get("text", ""), "size": 16, "bold": bool(b.get("sub")),
                  "color": T["text"], "bullet": True}]
        if b.get("sub"):
            lines.append({"text": b["sub"], "size": 12.5, "color": T["muted"],
                          "space_before": 2, "level": 1})
        dk.text(slide, (l, y, w, row_h), lines, anchor="middle")
        y += row_h


def build_two_col(slide, d, ctx):
    T = ctx.T
    dk.background(slide, T["bg"])
    _title(slide, ctx, d.get("title", ""), d.get("eyebrow"))
    gap = 0.5
    col_w = (CW - gap) / 2
    top = BODY_TOP
    height = 6.85 - top
    for idx, (key, default_color) in enumerate((("left", T["primary"]), ("right", T["accent"]))):
        col = d.get(key, {}) or {}
        x = MX + idx * (col_w + gap)
        color = col.get("color", default_color)
        dk.rect(slide, (x, top, col_w, height), fill=T["surface"], rounded=True, radius=0.04)
        dk.rect(slide, (x, top, col_w, 0.7), fill=color, rounded=True, radius=0.06)
        dk.text(slide, (x + 0.3, top, col_w - 0.6, 0.7),
                [{"text": col.get("heading", ""), "size": 16, "bold": True,
                  "color": T["on_primary"]}], anchor="middle")
        items = col.get("items", [])
        iy = top + 0.95
        row_h = min(0.7, (height - 1.1) / max(len(items), 1))
        for it in items:
            dk.text(slide, (x + 0.3, iy, col_w - 0.6, row_h),
                    [{"text": str(it), "size": 13.5, "color": T["text"], "bullet": True}],
                    anchor="middle")
            iy += row_h


def build_table(slide, d, ctx):
    T = ctx.T
    dk.background(slide, T["bg"])
    _title(slide, ctx, d.get("title", ""), d.get("eyebrow"))
    cols = d.get("columns", [])
    rows = d.get("rows", [])
    top = BODY_TOP
    height = min(6.7 - top, 0.5 + 0.5 * len(rows))
    dk.table(slide, (MX, top, CW, height), cols, rows, T,
             col_widths=d.get("col_widths"),
             first_col_accent=d.get("first_col_accent", True))
    if d.get("note"):
        dk.text(slide, (MX, top + height + 0.15, CW, 0.4),
                [{"text": d["note"], "size": 11, "italic": True, "color": T["muted"]}])


def build_chart(slide, d, ctx):
    T = ctx.T
    dk.background(slide, T["bg"])
    _title(slide, ctx, d.get("title", ""), d.get("eyebrow"))
    has_insight = bool(d.get("insight"))
    chart_w = CW * (0.66 if has_insight else 1.0)
    top = BODY_TOP
    ctype = d.get("chart_type", "bar")
    series = d.get("series", [])
    # a single-series bar/line legend just repeats category names — hide it
    legend_default = len(series) > 1 or ctype == "pie"
    dk.chart(slide, (MX, top, chart_w, 4.5),
             ctype, d.get("categories", []), series, T,
             legend=d.get("legend", legend_default),
             data_labels=d.get("data_labels", False))
    if has_insight:
        x = MX + chart_w + 0.4
        dk.rect(slide, (x, top, CW - chart_w - 0.4, 4.5), fill=T["surface"], rounded=True, radius=0.05)
        lines = [{"text": d.get("insight_title", "Insight"), "size": 14, "bold": True,
                  "color": T["accent"], "space_after": 8}]
        insight = d["insight"]
        for para in (insight if isinstance(insight, list) else [insight]):
            lines.append({"text": str(para), "size": 13, "color": T["text"],
                          "bullet": True, "space_after": 6})
        dk.text(slide, (x + 0.3, top + 0.35, CW - chart_w - 1.0, 3.9), lines)


def build_timeline(slide, d, ctx):
    T = ctx.T
    dk.background(slide, T["bg"])
    _title(slide, ctx, d.get("title", ""), d.get("eyebrow"))
    ms = d.get("milestones", [])[:5]
    n = max(len(ms), 1)
    line_y = 4.0
    dk.rect(slide, (MX, line_y, CW, 0.05), fill=T["line"])
    seg = CW / n
    for i, m in enumerate(ms):
        cx = MX + seg * i + seg / 2
        dk.rect(slide, (cx - 0.11, line_y - 0.08, 0.22, 0.22), fill=T["accent"], rounded=True, radius=0.5)
        above = i % 2 == 0
        by = line_y - 1.7 if above else line_y + 0.35
        col_w = seg - 0.3
        dk.text(slide, (cx - col_w / 2, by, col_w, 0.35),
                [{"text": m.get("label", ""), "size": 13, "bold": True, "color": T["accent"],
                  "align": "center"}], align="center")
        lines = [{"text": m.get("title", ""), "size": 13, "bold": True, "color": T["text"],
                  "align": "center"}]
        if m.get("desc"):
            lines.append({"text": m["desc"], "size": 11, "color": T["muted"], "align": "center",
                          "space_before": 2})
        dk.text(slide, (cx - col_w / 2, by + 0.4, col_w, 1.2), lines, align="center",
                anchor="top" if above else "top")


def build_process(slide, d, ctx):
    T = ctx.T
    dk.background(slide, T["bg"])
    _title(slide, ctx, d.get("title", ""), d.get("eyebrow"))
    steps = d.get("steps", [])[:5]
    n = max(len(steps), 1)
    arrow_w = 0.5
    box_w = (CW - arrow_w * (n - 1)) / n
    top = 2.8
    box_h = 1.9
    for i, s in enumerate(steps):
        x = MX + i * (box_w + arrow_w)
        dk.rect(slide, (x, top, box_w, box_h), fill=T["surface"], rounded=True, radius=0.06)
        dk.rect(slide, (x, top, box_w, 0.5), fill=T["primary"], rounded=True, radius=0.08)
        dk.text(slide, (x, top, box_w, 0.5),
                [{"text": f"STEP {i+1}", "size": 11, "bold": True, "color": T["on_primary"],
                  "align": "center"}], anchor="middle", align="center")
        lines = [{"text": s.get("title", ""), "size": 14, "bold": True, "color": T["primary"],
                  "align": "center"}]
        if s.get("desc"):
            lines.append({"text": s["desc"], "size": 11.5, "color": T["muted"], "align": "center",
                          "space_before": 4})
        dk.text(slide, (x + 0.15, top + 0.6, box_w - 0.3, box_h - 0.7), lines, align="center",
                anchor="middle")
        if i < n - 1:
            dk.text(slide, (x + box_w, top, arrow_w, box_h),
                    [{"text": "▶", "size": 18, "color": T["accent"], "align": "center"}],
                    anchor="middle", align="center")


def build_quote(slide, d, ctx):
    T = ctx.T
    dk.background(slide, T["surface"])
    dk.text(slide, (MX, 1.5, CW, 1.2),
            [{"text": "“", "size": 90, "bold": True, "color": T["surface_alt"]}])
    dk.text(slide, (MX + 0.3, 2.6, CW - 0.6, 2.6),
            [{"text": d.get("quote", ""), "size": 26, "italic": True, "color": T["primary"]}],
            anchor="middle")
    who = d.get("author", "")
    if d.get("role"):
        who = f"{who} · {d['role']}" if who else d["role"]
    if who:
        dk.text(slide, (MX + 0.3, 5.4, CW - 0.6, 0.5),
                [{"text": "— " + who, "size": 15, "bold": True, "color": T["accent"]}])


def build_image(slide, d, ctx):
    T = ctx.T
    dk.background(slide, T["bg"])
    layout = d.get("layout", "right")  # left | right | full
    if d.get("title"):
        _title(slide, ctx, d["title"], d.get("eyebrow"))
    top = BODY_TOP if d.get("title") else 0.8
    height = 6.7 - top
    if layout == "full":
        img_box = (MX, top, CW, height)
        _img_or_placeholder(slide, ctx, d, img_box)
        if d.get("caption"):
            dk.text(slide, (MX, 6.75, CW, 0.35),
                    [{"text": d["caption"], "size": 11, "italic": True, "color": T["muted"]}])
        return
    gap = 0.5
    half = (CW - gap) / 2
    img_first = layout == "left"
    img_x = MX if img_first else MX + half + gap
    txt_x = MX + half + gap if img_first else MX
    _img_or_placeholder(slide, ctx, d, (img_x, top, half, height))
    body = d.get("body", [])
    lines = []
    if isinstance(body, str):
        body = [body]
    for b in body:
        lines.append({"text": str(b), "size": 15, "color": T["text"], "bullet": True,
                      "space_after": 8})
    if d.get("caption"):
        lines.append({"text": d["caption"], "size": 11, "italic": True, "color": T["muted"],
                      "space_before": 8})
    dk.text(slide, (txt_x, top, half, height), lines, anchor="middle")


def _img_or_placeholder(slide, ctx, d, box):
    T = ctx.T
    pic = dk.picture(slide, box, d.get("image"), mode=d.get("fit", "fit"))
    if pic is None:
        dk.rect(slide, box, fill=T["surface"], rounded=True, radius=0.03, line=T["line"])
        l, t, w, h = box
        dk.text(slide, (l, t, w, h),
                [{"text": "🖼  이미지 경로를 지정하세요", "size": 13, "color": T["muted"],
                  "align": "center"}], anchor="middle", align="center")


def build_closing(slide, d, ctx):
    T = ctx.T
    dk.background(slide, T["primary"])
    dk.rect(slide, (MX, 2.55, 1.4, 0.09), fill=T["accent"])
    dk.text(slide, (MX, 2.9, CW, 1.3),
            [{"text": d.get("title", "Thank You"), "size": 40, "bold": True,
              "color": T["on_primary"]}])
    if d.get("message"):
        dk.text(slide, (MX, 4.3, CW, 0.9),
                [{"text": d["message"], "size": 17, "color": "D8E1EC"}])
    contacts = d.get("contacts") or []
    if contacts:
        dk.text(slide, (MX, 5.6, CW, 0.9),
                [{"text": "   ·   ".join(str(c) for c in contacts), "size": 13,
                  "color": "AEBED0"}])


REGISTRY = {
    "cover": build_cover,
    "section": build_section,
    "agenda": build_agenda,
    "summary": build_summary,
    "kpi": build_kpi,
    "bullets": build_bullets,
    "two_col": build_two_col,
    "table": build_table,
    "chart": build_chart,
    "timeline": build_timeline,
    "process": build_process,
    "quote": build_quote,
    "image": build_image,
    "closing": build_closing,
}

# Slide types that own the whole canvas — the engine skips footer/page number.
NO_FOOTER = {"cover", "section", "quote", "closing"}
