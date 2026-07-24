"""engine.py — turn a content JSON file into a .pptx deck.

Usage:
    python engine.py <content.json> <output.pptx>

The JSON is either a bare list of slide objects, or an object:
    {
      "config": {"theme": "corporate", "font": "Malgun Gothic",
                  "footer": "ACME Inc. · Confidential"},
      "slides": [ {"type": "cover", ...}, {"type": "kpi", ...}, ... ]
    }

Design split: this file only orchestrates (load JSON → make blank slides →
dispatch to a builder → add shared footer). All drawing lives in deck_kit.py
and builders.py, so adding a slide type never touches the engine.
"""

import json
import os
import sys
import types

from pptx import Presentation
from pptx.util import Inches

import deck_kit as dk
import builders


def _ctx_from_config(cfg):
    theme_name = cfg.get("theme", "corporate")
    theme = dk.THEMES.get(theme_name, dk.THEMES["corporate"])
    font = cfg.get("font", "Malgun Gothic")
    dk.set_default_font(font)
    return types.SimpleNamespace(T=theme, font=font, footer=cfg.get("footer", ""))


def build_deck(content, out_path):
    if isinstance(content, list):
        cfg, slides = {}, content
    else:
        cfg = content.get("config", {})
        slides = content.get("slides", [])

    ctx = _ctx_from_config(cfg)

    prs = Presentation()
    prs.slide_width = Inches(dk.SLIDE_W_IN)
    prs.slide_height = Inches(dk.SLIDE_H_IN)
    blank = prs.slide_layouts[6]

    page = 0
    warnings = []
    for i, d in enumerate(slides):
        stype = d.get("type", "bullets")
        builder = builders.REGISTRY.get(stype)
        slide = prs.slides.add_slide(blank)
        if builder is None:
            warnings.append(f"slide {i}: unknown type '{stype}' — rendered as blank note")
            dk.background(slide, ctx.T["bg"])
            dk.text(slide, (1, 3, 11, 1),
                    [{"text": f"[unknown slide type: {stype}]", "size": 18,
                      "color": ctx.T["bad"]}])
            continue
        try:
            builder(slide, d, ctx)
        except Exception as e:  # one bad slide must not kill the whole deck
            warnings.append(f"slide {i} ({stype}): {e}")
            dk.background(slide, ctx.T["bg"])
            dk.text(slide, (1, 3, 11, 1.5),
                    [{"text": f"[error building '{stype}' slide]", "size": 16, "color": ctx.T["bad"]},
                     {"text": str(e), "size": 11, "color": ctx.T["muted"]}])
        if stype not in builders.NO_FOOTER:
            page += 1
            builders.add_footer(slide, ctx, page)

    out_dir = os.path.dirname(os.path.abspath(out_path))
    os.makedirs(out_dir, exist_ok=True)
    prs.save(out_path)
    return warnings


def main():
    if len(sys.argv) < 3:
        print("usage: python engine.py <content.json> <output.pptx>")
        sys.exit(1)
    in_path, out_path = sys.argv[1], sys.argv[2]
    with open(in_path, encoding="utf-8") as f:
        content = json.load(f)
    warnings = build_deck(content, out_path)
    print(f"OK  -> {out_path}")
    if warnings:
        print(f"{len(warnings)} warning(s):")
        for w in warnings:
            print("  -", w)


if __name__ == "__main__":
    main()
