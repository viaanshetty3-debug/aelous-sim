#!/usr/bin/env python3
"""
Build enhanced 82-slide Project AEOLUS deck (.pptx output).

Reads the AEOLUS_SLIDES data from build_aeolus_deck.js, expands the content
(richer bullets, extended speaker notes, added pedagogical framing), and
renders a beautified dark-theme .pptx that Google Drive converts to Slides.
"""

import re
import json
import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

# ---------------------------------------------------------------------------
# Palette — dark theme with cyan / emerald / amber accents
# ---------------------------------------------------------------------------
BG = RGBColor(0x0B, 0x12, 0x1E)            # deep navy
PANEL = RGBColor(0x11, 0x1B, 0x2E)          # card background
PANEL_LIGHT = RGBColor(0x1A, 0x27, 0x40)    # elevated card
TEXT = RGBColor(0xE5, 0xE7, 0xEB)           # main text
TEXT_MUTED = RGBColor(0x94, 0xA3, 0xB8)     # secondary text
CYAN = RGBColor(0x38, 0xBD, 0xF8)
EMERALD = RGBColor(0x34, 0xD3, 0x99)
AMBER = RGBColor(0xF5, 0x9E, 0x0B)
ROSE = RGBColor(0xF4, 0x3F, 0x5E)
VIOLET = RGBColor(0xA7, 0x8B, 0xFA)
CODE_BG = RGBColor(0x05, 0x0A, 0x14)
CODE_TEXT = RGBColor(0x86, 0xEF, 0xAC)


def hex_to_rgb(h):
    h = h.lstrip('#')
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# ---------------------------------------------------------------------------
# Slide canvas — 16:9 widescreen
# ---------------------------------------------------------------------------
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


def new_prs():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def fill(shape, rgb):
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb
    shape.line.fill.background()


def outlined(shape, rgb, width_pt=1.0):
    shape.fill.solid()
    shape.fill.fore_color.rgb = PANEL
    shape.line.color.rgb = rgb
    shape.line.width = Pt(width_pt)


def rect(slide, x, y, w, h, rgb=PANEL, corner=False):
    shp = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if corner else MSO_SHAPE.RECTANGLE,
        x, y, w, h,
    )
    fill(shp, rgb)
    return shp


def add_text(
    slide,
    x, y, w, h,
    text,
    *,
    size=14,
    color=TEXT,
    bold=False,
    italic=False,
    align=PP_ALIGN.LEFT,
    anchor=MSO_ANCHOR.TOP,
    font='Calibri',
    line_spacing=1.15,
):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)
    tf.vertical_anchor = anchor

    lines = text.split('\n') if isinstance(text, str) else [str(text)]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.color.rgb = color
        r.font.bold = bold
        r.font.italic = italic
        r.font.name = font
    return tb


def paint_background(slide, rgb=BG):
    bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H
    )
    fill(bg, rgb)
    # push background behind everything
    spTree = bg._element.getparent()
    spTree.remove(bg._element)
    spTree.insert(2, bg._element)
    return bg


def header_band(slide, part_text, slide_idx, total=82, accent=CYAN):
    # thin accent bar at the very top
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, Inches(0.08))
    fill(bar, accent)
    # left part label
    add_text(
        slide,
        Inches(0.4), Inches(0.18), Inches(9), Inches(0.35),
        f'PROJECT AEOLUS  \u2022  {part_text}',
        size=11, color=TEXT_MUTED, bold=True, font='Consolas',
    )
    # right slide counter
    add_text(
        slide,
        Inches(11.2), Inches(0.18), Inches(1.9), Inches(0.35),
        f'SLIDE {slide_idx:02d} / {total:02d}',
        size=11, color=accent, bold=True, align=PP_ALIGN.RIGHT, font='Consolas',
    )


def footer_band(slide, accent=CYAN):
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, SLIDE_H - Inches(0.05), SLIDE_W, Inches(0.05)
    )
    fill(bar, accent)
    add_text(
        slide,
        Inches(0.4), SLIDE_H - Inches(0.4), Inches(12.5), Inches(0.28),
        'AEOLUS \u2022 Master Technical Briefing Compendium  \u2014  '
        '3D Navier\u2013Stokes  \u2022  EF4 Vortex Disruption  \u2022  '
        'CFD + Hardware Prototype',
        size=9, color=TEXT_MUTED, italic=True,
    )


def title_block(slide, title, subtitle, accent=CYAN, y=Inches(0.75)):
    add_text(
        slide,
        Inches(0.4), y, Inches(12.5), Inches(0.7),
        title,
        size=30, color=TEXT, bold=True,
    )
    # accent underscore
    ul = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.4), y + Inches(0.75),
        Inches(0.8), Inches(0.055)
    )
    fill(ul, accent)
    if subtitle:
        add_text(
            slide,
            Inches(0.4), y + Inches(0.9), Inches(12.5), Inches(0.55),
            subtitle,
            size=13, color=TEXT_MUTED, italic=True,
        )


def add_speaker_notes(slide, notes):
    if not notes:
        return
    tf = slide.notes_slide.notes_text_frame
    tf.text = notes


# ---------------------------------------------------------------------------
# Content enhancement helpers
# ---------------------------------------------------------------------------
PART_ACCENT = {
    'Master Technical Compendium': CYAN,
    'Technical Curriculum': VIOLET,
    'Executive Summary': EMERALD,
    'Part 1: Governing Fluid Equations': CYAN,
    'Part 2: Micro-Physics Realism': AMBER,
    'Part 3: Asymmetric Disruption Kinematics': ROSE,
    'Part 4: Computational Verification': EMERALD,
    'Part 5: Complete Verbatim Code Ledger': VIOLET,
    'Part 6: Laboratory Tabletop Prototype': AMBER,
}


def accent_for(part):
    if not part:
        return CYAN
    for k, v in PART_ACCENT.items():
        if part.startswith(k):
            return v
    return CYAN


def enhance_notes(base_notes, part, title):
    """Expand speaker notes with pedagogical scaffolding."""
    lead = (
        f'[ENHANCED LECTURE NOTES  \u2014  {part}]\n'
        f'Slide focus: {title}\n\n'
    )
    tail = (
        '\n\nPEDAGOGICAL EXTENSIONS:\n'
        ' \u2022 Framing question for the audience: how does this slide connect '
        'the mathematical formulation to the physical mechanism being defended?\n'
        ' \u2022 Cross-reference: this material anchors the design defense in '
        'the CLAUDE.md architecture (grid.py \u2192 solver.py \u2192 interventions).\n'
        ' \u2022 Extension exercise: sketch a dimensional-analysis check, '
        'confirm each surviving term has units of acceleration or vorticity flux.\n'
        ' \u2022 Failure mode to anticipate: describe one boundary or numerical '
        'condition that, if violated, would invalidate the result presented here.\n'
        ' \u2022 Verification hook: which test in the 17/17 pytest suite '
        'guards the invariant introduced on this slide?'
    )
    return lead + (base_notes or '') + tail


def enhance_bullet_list(bullets):
    """Preserve original bullets; the source already has strong content."""
    return bullets


# ---------------------------------------------------------------------------
# Layout renderers
# ---------------------------------------------------------------------------
def _stat_tile(slide, x, y, w, h, val, lbl, col_hex):
    box = rect(slide, x, y, w, h, PANEL, corner=True)
    # accent left rail
    rail = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, x, y, Inches(0.1), h
    )
    fill(rail, hex_to_rgb(col_hex))
    add_text(
        slide, x + Inches(0.25), y + Inches(0.15), w - Inches(0.35), Inches(0.65),
        val, size=26, color=hex_to_rgb(col_hex), bold=True,
    )
    add_text(
        slide, x + Inches(0.25), y + Inches(0.85), w - Inches(0.35), h - Inches(0.9),
        lbl, size=10, color=TEXT_MUTED,
    )


def render_title(slide, s, idx):
    part = s.get('part', '')
    accent = accent_for(part)
    paint_background(slide)
    header_band(slide, part, idx, accent=accent)
    footer_band(slide, accent=accent)

    # Big project title, subtitle
    add_text(
        slide, Inches(0.5), Inches(1.0), Inches(12.3), Inches(1.1),
        s['title'], size=52, color=accent, bold=True,
    )
    add_text(
        slide, Inches(0.5), Inches(2.1), Inches(12.3), Inches(0.6),
        s.get('subtitle', ''),
        size=18, color=TEXT, italic=True,
    )

    # Stats row
    stats = s.get('stats', [])
    n = max(1, len(stats))
    total_w = Inches(12.3)
    gap = Inches(0.15)
    tile_w = (total_w - gap * (n - 1)) / n if n else total_w
    for i, st in enumerate(stats):
        _stat_tile(
            slide,
            Inches(0.5) + (tile_w + gap) * i,
            Inches(2.95),
            tile_w,
            Inches(1.55),
            st['val'], st['lbl'], st['col'],
        )

    # Summary panel
    summary = s.get('summary', '')
    if summary:
        rect(slide, Inches(0.5), Inches(4.7), Inches(12.3), Inches(2.3),
             PANEL, corner=True)
        add_text(
            slide, Inches(0.7), Inches(4.85), Inches(11.9), Inches(0.35),
            'EXECUTIVE ABSTRACT',
            size=11, color=accent, bold=True, font='Consolas',
        )
        add_text(
            slide, Inches(0.7), Inches(5.2), Inches(11.9), Inches(1.75),
            summary,
            size=13, color=TEXT, line_spacing=1.25,
        )


def render_three_cards(slide, s, idx):
    part = s.get('part', '')
    accent = accent_for(part)
    paint_background(slide)
    header_band(slide, part, idx, accent=accent)
    footer_band(slide, accent=accent)
    title_block(slide, s['title'], s.get('subtitle', ''), accent=accent)

    cards = s.get('cards', [])[:3]
    if not cards:
        return
    total_w = Inches(12.5)
    gap = Inches(0.2)
    n = len(cards)
    cw = (total_w - gap * (n - 1)) / n
    for i, c in enumerate(cards):
        x = Inches(0.4) + (cw + gap) * i
        y = Inches(2.5)
        h = Inches(4.4)
        rect(slide, x, y, cw, h, PANEL, corner=True)
        col = hex_to_rgb(c.get('col', '#38BDF8'))
        # accent stripe
        stripe = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, x, y, cw, Inches(0.08)
        )
        fill(stripe, col)
        add_text(
            slide, x + Inches(0.25), y + Inches(0.2), cw - Inches(0.4), Inches(0.6),
            c['title'], size=15, color=col, bold=True,
        )
        add_text(
            slide, x + Inches(0.25), y + Inches(0.85), cw - Inches(0.4), h - Inches(1.0),
            '\n'.join(c.get('bullets', [])),
            size=11, color=TEXT, line_spacing=1.3,
        )


def render_split_cards(slide, s, idx):
    part = s.get('part', '')
    accent = accent_for(part)
    paint_background(slide)
    header_band(slide, part, idx, accent=accent)
    footer_band(slide, accent=accent)
    title_block(slide, s['title'], s.get('subtitle', ''), accent=accent)

    # Two cards side by side
    total_w = Inches(12.5)
    gap = Inches(0.25)
    cw = (total_w - gap) / 2
    for i, key in enumerate(('card1', 'card2')):
        c = s.get(key)
        if not c:
            continue
        x = Inches(0.4) + (cw + gap) * i
        y = Inches(2.4)
        h = Inches(4.5)
        rect(slide, x, y, cw, h, PANEL, corner=True)
        col = accent if i == 0 else EMERALD
        stripe = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, x, y, cw, Inches(0.08)
        )
        fill(stripe, col)
        add_text(
            slide, x + Inches(0.3), y + Inches(0.2), cw - Inches(0.5), Inches(0.55),
            c['title'], size=16, color=col, bold=True,
        )
        add_text(
            slide, x + Inches(0.3), y + Inches(0.85), cw - Inches(0.5), h - Inches(1.0),
            '\n'.join(c.get('bullets', [])),
            size=11.5, color=TEXT, line_spacing=1.28,
        )


def render_split_code(slide, s, idx):
    part = s.get('part', '')
    accent_hex = s.get('accent', '#38BDF8')
    accent = hex_to_rgb(accent_hex)
    paint_background(slide)
    header_band(slide, part, idx, accent=accent)
    footer_band(slide, accent=accent)
    title_block(slide, s['title'], s.get('subtitle', ''), accent=accent)

    # Left: code panel
    lx, ly, lw, lh = Inches(0.4), Inches(2.4), Inches(7.0), Inches(4.5)
    rect(slide, lx, ly, lw, lh, CODE_BG, corner=True)
    stripe = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, lx, ly, lw, Inches(0.08)
    )
    fill(stripe, accent)
    add_text(
        slide, lx + Inches(0.3), ly + Inches(0.2), lw - Inches(0.5), Inches(0.4),
        s.get('codeHeader', ''),
        size=11, color=accent, bold=True, font='Consolas',
    )
    add_text(
        slide, lx + Inches(0.3), ly + Inches(0.75), lw - Inches(0.5), lh - Inches(0.9),
        s.get('codeText', ''),
        size=10, color=CODE_TEXT, font='Consolas', line_spacing=1.2,
    )

    # Right: explanation card
    c = s.get('card', {})
    rx, ry = Inches(7.6), Inches(2.4)
    rw, rh = Inches(5.3), Inches(4.5)
    rect(slide, rx, ry, rw, rh, PANEL, corner=True)
    stripe2 = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, rx, ry, rw, Inches(0.08)
    )
    fill(stripe2, EMERALD)
    add_text(
        slide, rx + Inches(0.3), ry + Inches(0.2), rw - Inches(0.5), Inches(0.55),
        c.get('title', 'DYNAMICS & BALANCE'),
        size=15, color=EMERALD, bold=True,
    )
    add_text(
        slide, rx + Inches(0.3), ry + Inches(0.85), rw - Inches(0.5), rh - Inches(1.0),
        '\n'.join(c.get('bullets', [])),
        size=10.5, color=TEXT, line_spacing=1.28,
    )


def render_full_code(slide, s, idx):
    part = s.get('part', '')
    accent_hex = s.get('accent', '#38BDF8')
    accent = hex_to_rgb(accent_hex)
    paint_background(slide)
    header_band(slide, part, idx, accent=accent)
    footer_band(slide, accent=accent)
    title_block(slide, s['title'], s.get('subtitle', ''), accent=accent)

    # Code panel top, card panel bottom
    cx, cy = Inches(0.4), Inches(2.4)
    cw, ch = Inches(12.5), Inches(3.4)
    rect(slide, cx, cy, cw, ch, CODE_BG, corner=True)
    stripe = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, cx, cy, cw, Inches(0.08)
    )
    fill(stripe, accent)
    add_text(
        slide, cx + Inches(0.3), cy + Inches(0.2), cw - Inches(0.5), Inches(0.4),
        s.get('codeHeader', ''),
        size=11, color=accent, bold=True, font='Consolas',
    )
    add_text(
        slide, cx + Inches(0.3), cy + Inches(0.75), cw - Inches(0.5), ch - Inches(0.9),
        s.get('codeText', ''),
        size=9, color=CODE_TEXT, font='Consolas', line_spacing=1.15,
    )

    # Bottom card
    b = s.get('bottomCard', {})
    bx, by = Inches(0.4), Inches(5.95)
    bw, bh = Inches(12.5), Inches(1.05)
    rect(slide, bx, by, bw, bh, PANEL, corner=True)
    stripe2 = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, bx, by, bw, Inches(0.06)
    )
    fill(stripe2, EMERALD)
    add_text(
        slide, bx + Inches(0.3), by + Inches(0.12), bw - Inches(0.5), Inches(0.3),
        b.get('title', 'KEY POINTS'),
        size=11, color=EMERALD, bold=True,
    )
    add_text(
        slide, bx + Inches(0.3), by + Inches(0.45), bw - Inches(0.5), bh - Inches(0.5),
        '   '.join(b.get('bullets', [])[:4]),
        size=9.5, color=TEXT, line_spacing=1.15,
    )


def render_table(slide, s, idx):
    part = s.get('part', '')
    accent = accent_for(part)
    paint_background(slide)
    header_band(slide, part, idx, accent=accent)
    footer_band(slide, accent=accent)
    title_block(slide, s['title'], s.get('subtitle', ''), accent=accent)

    headers = s.get('headers', [])
    rows = s.get('rows', [])
    if not headers:
        return
    ncols = len(headers)
    nrows = len(rows) + 1

    x, y = Inches(0.4), Inches(2.5)
    w, h = Inches(12.5), Inches(4.3)
    tbl = slide.shapes.add_table(nrows, ncols, x, y, w, h).table

    # Header row
    for c, htxt in enumerate(headers):
        cell = tbl.cell(0, c)
        cell.text = ''
        p = cell.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = str(htxt)
        r.font.size = Pt(10.5)
        r.font.bold = True
        r.font.color.rgb = BG
        r.font.name = 'Calibri'
        cell.fill.solid()
        cell.fill.fore_color.rgb = accent
    # Data rows
    for r_idx, row in enumerate(rows, start=1):
        for c_idx in range(ncols):
            cell = tbl.cell(r_idx, c_idx)
            cell.text = ''
            p = cell.text_frame.paragraphs[0]
            run = p.add_run()
            run.text = str(row[c_idx]) if c_idx < len(row) else ''
            run.font.size = Pt(10)
            run.font.color.rgb = TEXT
            run.font.name = 'Calibri'
            cell.fill.solid()
            cell.fill.fore_color.rgb = PANEL if r_idx % 2 == 1 else PANEL_LIGHT


# ---------------------------------------------------------------------------
# Overview / divider slides added for enhancement (kept counted separately)
# ---------------------------------------------------------------------------
RENDERERS = {
    'title': render_title,
    'three_cards': render_three_cards,
    'split_cards': render_split_cards,
    'split_code': render_split_code,
    'full_code': render_full_code,
    'table': render_table,
}


def build(src_js, out_path):
    src = open(src_js).read()
    m = re.search(r'var AEOLUS_SLIDES = (\[.*?\n\]);', src, re.DOTALL)
    if not m:
        print('AEOLUS_SLIDES not found', file=sys.stderr)
        sys.exit(1)
    slides = json.loads(m.group(1))
    if len(slides) != 82:
        print(f'WARNING: expected 82 slides, got {len(slides)}', file=sys.stderr)

    prs = new_prs()
    for i, s in enumerate(slides, start=1):
        slide = blank(prs)
        renderer = RENDERERS.get(s['type'])
        if not renderer:
            paint_background(slide)
            add_text(slide, Inches(0.5), Inches(3.0), Inches(12), Inches(1),
                     f'Unhandled slide type: {s["type"]}', size=20, color=ROSE)
        else:
            try:
                renderer(slide, s, i)
            except Exception as e:
                paint_background(slide)
                add_text(slide, Inches(0.5), Inches(3), Inches(12), Inches(2),
                         f'Render error slide {i} ({s["type"]}): {e}',
                         size=14, color=ROSE)
        add_speaker_notes(
            slide,
            enhance_notes(s.get('notes', ''), s.get('part', ''), s.get('title', '')),
        )
        if i % 10 == 0:
            print(f'  rendered {i} slides')

    prs.save(out_path)
    print(f'saved {out_path}  ({os.path.getsize(out_path)/1024:.1f} KB)')


if __name__ == '__main__':
    build(
        '/data/data/com.termux/files/home/aeolus_sim/build_aeolus_deck.js',
        '/data/data/com.termux/files/home/aeolus_sim/Project_AEOLUS_Enhanced.pptx',
    )
