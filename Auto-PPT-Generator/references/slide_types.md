# Slide type reference

Every slide is a JSON object with a `type` key. Below are all keys each type
reads and the **character budgets** that keep text inside its fixed region.
Budgets are guidance, not hard limits — the engine won't crash if you exceed
them, but text may clip or wrap awkwardly. When in doubt, split into two slides
rather than cramming one.

Wide characters (한글, 漢字, full-width) take ~2× the width of a Latin letter, so
a "40 chars" budget means ~20 Korean characters.

## Table of contents
- [Deck config](#deck-config)
- [cover](#cover) · [section](#section) · [agenda](#agenda) · [summary](#summary)
- [kpi](#kpi) · [bullets](#bullets) · [two_col](#two_col) · [table](#table)
- [chart](#chart) · [timeline](#timeline) · [process](#process)
- [quote](#quote) · [image](#image) · [closing](#closing)

---

## Deck config

Top-level `config` object (optional; all keys optional):

| key | values | default | notes |
|-----|--------|---------|-------|
| theme | `corporate` / `dark` / `minimal` | corporate | color system |
| font | any installed font name | `Malgun Gothic` | applied to all text (Latin + 한글) |
| footer | string | "" | bottom-left on content slides; empty = no footer |

`slides` is the ordered list of slide objects. Page numbers are auto-assigned to
content slides (cover/section/quote/closing are excluded from numbering).

---

## cover
Full-bleed title slide (primary background).

| key | type | budget | notes |
|-----|------|--------|-------|
| eyebrow | string | ~30 | small kicker above title |
| title | string | ~40 | main deck title |
| subtitle | string | ~50 | one line under title |
| meta | list[string] | 3–4 items | joined with " \| " (team, date, author) |

## section
Chapter divider.

| key | type | budget | notes |
|-----|------|--------|-------|
| number | int/string | — | shows as big ghost number (zero-padded if digit) |
| title | string | ~24 | chapter title |
| subtitle | string | ~40 | optional |

## agenda
Numbered outline. Best with 3–6 items (auto-sizes down to fit).

| key | type | budget | notes |
|-----|------|--------|-------|
| title | string | ~24 | default "Agenda" |
| eyebrow | string | ~30 | optional kicker |
| items | list | ≤6 | each `{title, desc?, no?}` or a bare string; `no` overrides auto-number |

## summary
Executive summary. 2–4 `points` render as accent cards; 5+ fall back to bullets.

| key | type | budget | notes |
|-----|------|--------|-------|
| title | string | ~24 | default "Executive Summary" |
| lead | string | ~120 | intro paragraph above the cards |
| points | list | 2–4 ideal | each `{title, desc?}` or a bare string |

## kpi
Metric tiles. 2–4 tiles. Value font auto-shrinks to fit the tile.

| key | type | budget | notes |
|-----|------|--------|-------|
| title | string | ~24 | |
| tiles | list | ≤4 | see below |

Tile object: `{label, value, delta?, trend?, note?}`
- `value`: the big number (auto-sized) — keep ≤ ~7 wide-units for the largest font
- `trend`: `up` (green ▲) / `down` (red ▼) / `flat` (gray) — colors the delta
- `delta`: e.g. "+8.4% YoY"; `note`: small caption under the delta

## bullets
Standard content slide. Best with ≤6 bullets.

| key | type | budget | notes |
|-----|------|--------|-------|
| title | string | ~24 | |
| lead | string | ~90 | optional emphasized intro line |
| bullets | list | ≤6 | each `{text, sub?}` or a bare string; `sub` = indented subtext |

## two_col
Side-by-side comparison (great for pros/cons, before/after, A vs B).

| key | type | notes |
|-----|------|-------|
| title | string | |
| left / right | object | `{heading, items[], color?}` — `color` overrides the header band hex (no `#`) |

Keep `items` to ≤5 per column, each ≤ ~40 chars.

## table
Data table with themed header + zebra rows.

| key | type | notes |
|-----|------|-------|
| title | string | |
| columns | list[string] | header labels |
| rows | list[list] | each inner list aligns to columns |
| col_widths | list[number] | optional relative weights, e.g. `[3,2,2,2]` |
| first_col_accent | bool | default true — bolds/colors the first column |
| note | string | optional footnote below the table |

Keep to ≤7 rows and ≤6 columns for readability.

## chart
Native, editable chart (users can double-click to edit data in PowerPoint).

| key | type | notes |
|-----|------|-------|
| title | string | |
| chart_type | string | `bar` / `bar_h` / `line` / `pie` / `area` / `stacked` |
| categories | list | x-axis labels (or pie slice labels) |
| series | list | each `{name, values[]}`; pie uses the first series only |
| data_labels | bool | show values on the chart (default false) |
| legend | bool | default true |
| insight | string or list | optional sidebar takeaways (shrinks chart to 66% width) |
| insight_title | string | sidebar heading, default "Insight" |

## timeline
Horizontal roadmap. Up to 5 milestones, labels alternate above/below the line.

| key | type | notes |
|-----|------|-------|
| title | string | |
| milestones | list | ≤5, each `{label, title, desc?}` — `label` is the date/phase |

## process
Left-to-right step flow with arrows. Up to 5 steps.

| key | type | notes |
|-----|------|-------|
| title | string | |
| steps | list | ≤5, each `{title, desc?}` — auto-numbered STEP 1..N |

## quote
Full-bleed pull quote.

| key | type | budget | notes |
|-----|------|--------|-------|
| quote | string | ~140 | the quotation |
| author | string | — | attribution |
| role | string | — | appended after author with · |

## image
Image with optional text. `layout`: `left` / `right` / `full`.

| key | type | notes |
|-----|------|-------|
| image | string (path) | absolute or relative to run dir; missing path → labeled placeholder |
| layout | string | `right` (default), `left`, or `full` |
| title | string | optional slide title |
| body | string or list | text beside the image (rendered as bullets) |
| caption | string | small italic caption |
| fit | string | `fit` (default, letterboxed) or `fill` (stretch) |

## closing
Thank-you / contact slide (primary background).

| key | type | notes |
|-----|------|-------|
| title | string | default "Thank You" |
| message | string | one line under the title |
| contacts | list[string] | joined with · (name, email, phone) |
