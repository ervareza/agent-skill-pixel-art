"""Game Items, Weapons, ZzSprite Procedural Creatures, 9-Slice UI, and Fake-3D Sprite Stacking Engine.

Synthesized from:
- KilledByAPixel/ZzSprite (171★) — Seeded symmetrical procedural sprite generator
- danielwh2/sprite-stacking (940★) — 4-view visual-hull carving & symmetric-pivot turntable renderer
- MozeeB/pixel-asset-gen & Gamezxz/pixel-art-studio — Crisp pixel items, weapons, & 9-slice UI
"""

from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Sequence

from PIL import Image

from .canvas import NEAREST, SpriteDocument
from .color import ColorRamp, RGBA, hex_to_rgba, load_palette, mix_color, nearest_color

ITEM_TYPES = ("sword", "axe", "staff", "potion", "gem", "chest", "shield", "key", "heart", "coin")
UI_TYPES = ("panel_9slice", "health_bar", "button_3state", "inventory_slot", "cursor")
STACK_PRESETS = ("car", "crate", "tree", "tower", "chest")


# ===========================================================================
# 1. GAME ITEMS & WEAPONS (16x16 .. 64x64, crisp silhouette + selout!)
# ===========================================================================


def generate_item(
    item_type: str = "sword",
    size: int = 16,
    palette: str | Sequence[str] | None = "endesga-32",
    seed: int = 42,
) -> SpriteDocument:
    itype = item_type.lower().strip()
    if itype not in ITEM_TYPES:
        raise ValueError(f"Unknown item {item_type!r}. Valid: {ITEM_TYPES}")
    doc = SpriteDocument(size, size, palette=palette, snap=(palette is not None))
    pal = doc.palette

    def _r(name: str, base: str) -> ColorRamp:
        r = ColorRamp.from_base(name, base, steps=4)
        return r.snap_to(pal) if pal else r

    steel = _r("steel", "#B8C7D9")
    gold = _r("gold", "#E8B63E")
    wood = _r("wood", "#8C5430")
    ruby = _r("ruby", "#E03B4A")
    emerald = _r("emerald", "#42C268")
    magic = _r("magic", "#4CC9FF")
    ink = nearest_color(hex_to_rgba("#1C1629"), pal) if pal else hex_to_rgba("#1C1629")

    s = size
    cx, cy = (s - 1) // 2, (s - 1) // 2

    if itype == "sword":
        # Crisp 45-degree diagonal RPG sword!
        m = max(2, s // 8)
        for i in range(s - m * 2 - 2):
            bx = m + 3 + i
            by = s - 1 - m - 3 - i
            if 1 <= bx < s - 1 and 1 <= by < s - 1:
                doc.px(bx, by, steel.highlight)
                doc.px(bx, by + 1, steel.mid)
                if s >= 24 and bx + 1 < s - 1:
                    doc.px(bx + 1, by + 1, steel.shadow)
        # Crossguard & grip
        gx, gy = m + 3, s - 1 - m - 3
        doc.line(gx - max(2, s // 7), gy - max(2, s // 7), gx + max(2, s // 7), gy + max(2, s // 7), gold.light, pixel_perfect=True)
        doc.line(m + 1, s - 2 - m, gx - 1, gy + 1, wood.mid, pixel_perfect=True)
        doc.px(m + 1, s - 2 - m, gold.highlight)

    elif itype == "axe":
        m = max(2, s // 8)
        # Wooden haft
        doc.line(m + 1, s - 2 - m, s - 3 - m, m + 2, wood.mid, pixel_perfect=True)
        doc.line(m + 2, s - 2 - m, s - 2 - m, m + 2, wood.shadow, pixel_perfect=True)
        # Crisp curved battle-axe blade!
        hx, hy = s - 4 - m, m + 3
        ar = max(3, s // 3)
        blade_pts = [
            (hx - 1, hy - 1),
            (hx + 2, hy - 2),
            (min(s - 2, hx + ar), hy + 1),
            (hx + ar - 1, min(s - 2, hy + ar)),
            (hx, hy + ar - 1),
            (hx - 1, hy + 2),
        ]
        doc.polygon(blade_pts, steel.mid, fill=True)
        # Bright sharp cutting edge!
        doc.line(min(s - 2, hx + ar), hy + 1, hx + ar - 1, min(s - 2, hy + ar), steel.highlight, pixel_perfect=True)
        doc.px(hx, hy, gold.mid)

    elif itype == "staff":
        m = max(2, s // 8)
        doc.line(m + 1, s - 2 - m, s - 4 - m, m + 3, wood.mid, pixel_perfect=True)
        doc.line(m + 2, s - 2 - m, s - 3 - m, m + 3, wood.shadow, pixel_perfect=True)
        ox, oy = s - 3 - m, m + 2
        orad = max(2, s // 6)
        # Gold cradle prongs + vibrant cyan/blue magic crystal!
        c_dark = nearest_color(hex_to_rgba("#0077CC"), pal) if pal else hex_to_rgba("#0077CC")
        c_mid = nearest_color(hex_to_rgba("#00C8FF"), pal) if pal else hex_to_rgba("#00C8FF")
        c_hi = nearest_color(hex_to_rgba("#FFFFFF"), pal) if pal else hex_to_rgba("#FFFFFF")
        doc.circle(ox, oy, orad, c_dark, fill=True)
        doc.circle(ox, oy, max(1, orad - 1), c_mid, fill=True)
        doc.px(ox - 1, oy - 1, c_hi)
        doc.px(ox - 1, oy + orad, gold.highlight)
        doc.px(ox - orad, oy + 1, gold.mid)

    elif itype == "potion":
        # Rounded flask + cork + glowing liquid + glass specular!
        rx = max(3, int(s * 0.30))
        ry = max(3, int(s * 0.28))
        by = int(s * 0.62)
        doc.ellipse(cx - rx, by - ry, cx + rx, by + ry, ruby.shadow, fill=True)
        doc.ellipse(cx - rx, by - ry, cx + rx - 1, by + ry - 1, ruby.mid, fill=True, only="opaque")
        doc.ellipse(cx - rx + 1, by - ry + 1, cx, by, ruby.highlight, fill=True, only="opaque")
        # Bottle neck & cork
        nw = max(1, s // 10)
        doc.rect(cx - nw, max(2, by - ry - max(2, s // 6)), cx + nw, by - ry, steel.light)
        doc.rect(cx - nw, max(1, by - ry - max(3, s // 5)), cx + nw, max(1, by - ry - max(2, s // 6)), wood.light)

    elif itype == "gem":
        # Faceted emerald/ruby diamond cut!
        r = max(4, int(s * 0.36))
        pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
        doc.polygon(pts, emerald.mid, fill=True)
        doc.polygon([(cx, cy - r), (cx, cy), (cx - r, cy)], emerald.highlight, fill=True)
        doc.polygon([(cx, cy), (cx + r, cy), (cx, cy + r)], emerald.shadow, fill=True)
        doc.px(cx - max(1, r // 3), cy - max(1, r // 3), hex_to_rgba("#FFFFFF"))

    elif itype == "chest":
        x0, x1 = max(2, s // 6), s - 1 - max(2, s // 6)
        y0, y1 = max(3, s // 4), s - 1 - max(2, s // 6)
        mid_y = (y0 + y1) // 2
        doc.rounded_rect(x0, y0, x1, y1, wood.mid, radius=1, fill=True)
        doc.rect(x0, y0, x1, mid_y - 1, wood.light, only="opaque")
        doc.rect(x0, mid_y, x1, mid_y, gold.mid)
        doc.rect(x0, y0, x0, y1, gold.shadow, only="opaque")
        doc.rect(x1, y0, x1, y1, gold.shadow, only="opaque")
        # Golden clasp
        doc.rect(cx - 1, mid_y - 1, cx + 1, mid_y + 1, gold.highlight)

    elif itype == "shield":
        x0, x1 = max(2, s // 5), s - 1 - max(2, s // 5)
        y0, y1 = max(2, s // 6), s - 1 - max(2, s // 6)
        pts = [(x0, y0), (x1, y0), (x1, (y0 + y1) // 2 + 1), (cx, y1), (x0, (y0 + y1) // 2 + 1)]
        doc.polygon(pts, steel.mid, fill=True)
        doc.polygon([(x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x1 - 1, (y0 + y1) // 2), (cx, y1 - 2), (x0 + 1, (y0 + y1) // 2)], ruby.mid, fill=True)
        doc.line(cx, y0 + 1, cx, y1 - 2, gold.highlight)
        doc.line(x0 + 1, (y0 + y1) // 2 - 1, x1 - 1, (y0 + y1) // 2 - 1, gold.highlight)

    elif itype == "key":
        r = max(2, s // 5)
        doc.circle(max(r + 2, s // 3), cy, r, gold.light, fill=False)
        doc.line(max(r + 2, s // 3) + r, cy, s - 3, cy, gold.mid)
        doc.line(s - 4, cy, s - 4, cy + max(2, s // 6), gold.shadow)
        doc.line(s - 6, cy, s - 6, cy + max(1, s // 8), gold.shadow)

    elif itype == "heart":
        r = max(2, s // 5)
        doc.circle(cx - r + 1, cy - r // 2, r, ruby.mid, fill=True)
        doc.circle(cx + r - 1, cy - r // 2, r, ruby.mid, fill=True)
        doc.polygon([(cx - r * 2 + 1, cy - r // 3), (cx + r * 2 - 1, cy - r // 3), (cx, cy + r * 2)], ruby.mid, fill=True)
        doc.circle(cx - r, cy - r // 2 - 1, max(1, r // 2), ruby.highlight, fill=True, only="opaque")

    elif itype == "coin":
        r = max(4, int(s * 0.36))
        doc.circle(cx, cy, r, gold.shadow, fill=True)
        doc.circle(cx, cy, max(2, r - 1), gold.mid, fill=True)
        doc.circle(cx - 1, cy - 1, max(1, r - 2), gold.light, fill=True, only="opaque")
        doc.rect(cx, cy - max(1, r // 2), cx, cy + max(1, r // 2), gold.highlight)

    doc.selout(dark_color=ink)
    doc.tag(itype, 1, 1)
    return doc


# ===========================================================================
# 2. ZZSPRITE PROCEDURAL SYMMETRICAL SPRITE GENERATOR
# ===========================================================================


def generate_zzsprite(
    size: int = 16,
    seed: int = 1,
    palette: str | Sequence[str] | None = "pico-8",
) -> SpriteDocument:
    """Port & pixel-art enhancement of Frank Force's ZzSprite algorithm.

    Procedurally generates unique symmetrical creatures, spaceships, aliens, or relics
    with hue-shifted 3-tone shading and selective outlines.
    """
    doc = SpriteDocument(size, size, palette=palette, snap=(palette is not None))
    rng = random.Random(seed)
    pal = doc.palette or [hex_to_rgba(c) for c in ("#1A1C2C", "#B13E53", "#EF7D57", "#FFCD75", "#38B764", "#41A6F6", "#F4F4F4")]

    # Pick 2-3 cohesive mid/bright colors from palette (excluding darkest outline)
    sorted_pal = sorted(pal, key=lambda c: c[0] * 0.299 + c[1] * 0.587 + c[2] * 0.114)
    outline_c = sorted_pal[0]
    body_choices = sorted_pal[1:] if len(sorted_pal) > 2 else sorted_pal
    main_c = rng.choice(body_choices)
    accent_c = rng.choice(body_choices)
    ramp = ColorRamp.from_base("zz", main_c, steps=4)
    if doc.palette:
        ramp = ramp.snap_to(doc.palette)

    half_w = max(2, (size - 4) // 2)
    h_span = max(4, size - 4)
    cx = size // 2
    y_bias = rng.uniform(-0.15, 0.15)
    density = rng.uniform(0.72, 0.94)
    rad = size * rng.uniform(0.32, 0.44)

    for j in range(h_span):
        for i in range(half_w):
            dist2 = i * i + (j - (0.5 + y_bias) * h_span) ** 2
            if rng.uniform(0, rad) ** 2 > dist2 and rng.random() < density:
                # Shade by vertical & horizontal position
                if j < h_span * 0.35:
                    col = ramp.light
                elif j > h_span * 0.72:
                    col = ramp.shadow
                else:
                    col = accent_c if rng.random() < 0.14 else ramp.mid
                y = 2 + j
                doc.px(cx - 1 - i, y, col)
                doc.px(cx + i, y, col)

    # Add symmetric eyes if creature-sized
    if size >= 12:
        eye_y = 2 + int(h_span * 0.32)
        eye_off = max(1, half_w // 3)
        if doc.get(cx - 1 - eye_off, eye_y):
            doc.px(cx - 1 - eye_off, eye_y, outline_c)
            doc.px(cx + eye_off, eye_y, outline_c)

    doc.outline(outline_c, where="outside")
    doc.metadata = {"generator": "zzsprite", "seed": seed}
    return doc


# ===========================================================================
# 3. GAME UI ELEMENTS (9-Slice Panels, Health Bars, 3-State Buttons)
# ===========================================================================


def generate_ui_asset(
    ui_type: str = "panel_9slice",
    width: int = 48,
    height: int = 48,
    style: str = "fantasy",
    palette: str | Sequence[str] | None = "endesga-32",
) -> tuple[SpriteDocument, dict]:
    utype = ui_type.lower().strip()
    if utype not in UI_TYPES:
        raise ValueError(f"Unknown UI type {ui_type!r}. Valid: {UI_TYPES}")

    doc = SpriteDocument(width, height, palette=palette, snap=(palette is not None))
    pal = doc.palette

    def _c(hx: str) -> RGBA:
        c = hex_to_rgba(hx)
        return nearest_color(c, pal) if pal else c

    if style == "scifi":
        bg, border, hi, sh, accent = _c("#141C33"), _c("#3B5DC9"), _c("#73EFF7"), _c("#0D1020"), _c("#00F5D4")
    elif style == "minimal":
        bg, border, hi, sh, accent = _c("#262B44"), _c("#8B9BB4"), _c("#FFFFFF"), _c("#181425"), _c("#FEAE34")
    else:  # fantasy RPG
        bg, border, hi, sh, accent = _c("#2A2136"), _c("#8F5E3B"), _c("#F2C75C"), _c("#181221"), _c("#E8B63E")

    meta: dict = {"ui_type": utype, "style": style, "size": [width, height]}

    if utype == "panel_9slice":
        corner = max(3, min(width, height) // 6)
        doc.rounded_rect(0, 0, width - 1, height - 1, sh, radius=1, fill=True)
        doc.rounded_rect(1, 1, width - 2, height - 2, border, radius=1, fill=True)
        doc.rect(2, 2, width - 3, height - 3, bg, fill=True)
        # Bevel highlight top/left, inner shadow bottom/right
        doc.line(2, 1, width - 3, 1, hi)
        doc.line(1, 2, 1, height - 3, hi)
        doc.line(2, 2, width - 3, 2, sh)
        # Ornate corner rivets for fantasy style
        if style == "fantasy" and width >= 16 and height >= 16:
            for cx_, cy_ in ((2, 2), (width - 3, 2), (2, height - 3), (width - 3, height - 3)):
                doc.px(cx_, cy_, accent)
        meta["nine_slice_margins"] = {"left": corner, "right": corner, "top": corner, "bottom": corner}

    elif utype == "health_bar":
        # 5 frames showing 100%, 75%, 50%, 25%, 0% fill with dynamic green->yellow->red!
        pcts = [1.0, 0.75, 0.50, 0.25, 0.0]
        doc.set_duration(350)
        for fi, pct in enumerate(pcts):
            if fi > 0:
                doc.add_frame(copy=False, duration_ms=350)
            doc.rect(0, 0, width - 1, height - 1, sh, fill=True)
            doc.rect(1, 1, width - 2, height - 2, border, fill=False)
            doc.rect(2, 2, width - 3, height - 3, bg, fill=True)
            inner_w = max(0, width - 4)
            fill_w = round(inner_w * pct)
            if fill_w > 0:
                fill_hex = "#38B764" if pct > 0.6 else ("#FEAE34" if pct > 0.3 else "#E43B44")
                hi_hex = "#A7F070" if pct > 0.6 else ("#FEE761" if pct > 0.3 else "#F6757A")
                sh_hex = "#265C42" if pct > 0.6 else ("#BE4A2F" if pct > 0.3 else "#A22633")
                doc.rect(2, 2, 1 + fill_w, height - 3, _c(fill_hex), fill=True)
                if height >= 6:
                    doc.rect(2, 2, 1 + fill_w, 2, _c(hi_hex), fill=True)
                    doc.rect(2, height - 3, 1 + fill_w, height - 3, _c(sh_hex), fill=True)
        doc.tag("health_levels", 1, len(pcts))
        meta["levels"] = pcts

    elif utype == "button_3state":
        # Frame 1 = normal, Frame 2 = hover, Frame 3 = pressed (shifted 1px down/right!)
        states = ("normal", "hover", "pressed")
        for fi, st in enumerate(states):
            if fi > 0:
                doc.add_frame(copy=False, duration_ms=400)
            y_off = 1 if st == "pressed" else 0
            doc.rounded_rect(0, y_off, width - 1, height - 1, sh, radius=1, fill=True)
            body_c = hi if st == "hover" else border
            doc.rounded_rect(1, 1 + y_off, width - 2, height - 2, body_c, radius=1, fill=True)
            doc.rect(2, 2 + y_off, width - 3, height - 3, bg if st != "hover" else _c("#3A3252"), fill=True)
            if st != "pressed":
                doc.line(2, 1, width - 3, 1, accent if st == "hover" else hi)
            # Center decorative emblem bar
            bx0 = width // 4
            bx1 = width - 1 - width // 4
            by = height // 2 + y_off
            doc.rect(bx0, by, bx1, by, accent if st == "hover" else hi)
        doc.tag("normal", 1, 1)
        doc.tag("hover", 2, 2)
        doc.tag("pressed", 3, 3)
        meta["states"] = list(states)

    elif utype == "inventory_slot":
        # Frame 1 = empty, Frame 2 = selected (bright highlight border!)
        for fi in range(2):
            if fi > 0:
                doc.add_frame(copy=False, duration_ms=400)
            doc.rect(0, 0, width - 1, height - 1, accent if fi == 1 else sh, fill=True)
            doc.rect(1, 1, width - 2, height - 2, hi if fi == 1 else border, fill=False)
            doc.rect(2, 2, width - 3, height - 3, bg, fill=True)
            doc.line(2, 2, width - 3, 2, sh)
        doc.tag("empty", 1, 1)
        doc.tag("selected", 2, 2)

    elif utype == "cursor":
        # Classic pixel arrow cursor
        pts = [(1, 1), (1, min(height - 2, 11)), (4, min(height - 2, 8)), (6, min(height - 2, 12)), (8, min(height - 2, 11)), (6, min(height - 2, 7)), (9, min(height - 2, 7))]
        doc.polygon(pts, _c("#FFFFFF"), fill=True)
        doc.outline(sh, where="outside")

    return doc, meta


# ===========================================================================
# 4. FAKE-3D SPRITE STACKING ENGINE (inspired by danielwh2/sprite-stacking)
# ===========================================================================


def build_stack_preset(
    preset: str = "car",
    slice_w: int = 16,
    slice_h: int = 24,
    num_slices: int = 12,
    palette: str | Sequence[str] | None = "endesga-32",
) -> tuple[Image.Image, dict]:
    """Generate a horizontal fake-3D slice strip (z=0 ground on left -> roof on right)."""
    pname = preset.lower().strip()
    if pname not in STACK_PRESETS:
        raise ValueError(f"Unknown sprite stack preset {preset!r}. Valid: {STACK_PRESETS}")

    pal = load_palette(palette)[1] if palette is not None else None

    def _c(hx: str) -> RGBA:
        c = hex_to_rgba(hx)
        return nearest_color(c, pal) if pal else c

    strip = Image.new("RGBA", (slice_w * num_slices, slice_h), (0, 0, 0, 0))

    for z in range(num_slices):
        zt = z / max(1, num_slices - 1)
        sdoc = SpriteDocument(slice_w, slice_h, palette=palette, snap=(palette is not None))
        cx, cy = (slice_w - 1) // 2, (slice_h - 1) // 2

        if pname == "car":
            # Retro rally car (front points DOWN +y!)
            if z < 3:
                # 4 tires + dark chassis
                sdoc.rect(3, 3, slice_w - 4, slice_h - 4, _c("#262B44"))
                for wx in (1, slice_w - 3):
                    sdoc.rect(wx, 4, wx + 1, 7, _c("#181425"))
                    sdoc.rect(wx, slice_h - 8, wx + 1, slice_h - 5, _c("#181425"))
            elif z < 7:
                # Car body + headlights at front (+y) & taillights at rear (-y)
                body_c = _c("#E43B44") if z >= 5 else _c("#A22633")
                sdoc.rounded_rect(2, 2, slice_w - 3, slice_h - 3, body_c, radius=1, fill=True)
                sdoc.rect(cx - 1, 2, cx + 1, slice_h - 3, _c("#FFFFFF"))  # Racing stripe!
                if z == 4:
                    sdoc.rect(3, slice_h - 3, 4, slice_h - 3, _c("#FEE761"))
                    sdoc.rect(slice_w - 5, slice_h - 3, slice_w - 4, slice_h - 3, _c("#FEE761"))
            elif z < 10:
                # Cabin & windshield glass
                sdoc.rounded_rect(3, 5, slice_w - 4, slice_h - 7, _c("#0099DB"), radius=1, fill=True)
                sdoc.rect(4, 7, slice_w - 5, slice_h - 9, _c("#2CE8F5"))
            else:
                # Roof
                sdoc.rounded_rect(4, 7, slice_w - 5, slice_h - 9, _c("#F77622"), radius=1, fill=True)
                sdoc.rect(cx - 1, 7, cx + 1, slice_h - 9, _c("#FFFFFF"))

        elif pname == "crate":
            w_ = min(slice_w, slice_h)
            x0, x1 = (slice_w - w_) // 2 + 2, (slice_w + w_) // 2 - 3
            y0, y1 = (slice_h - w_) // 2 + 2, (slice_h + w_) // 2 - 3
            frame_c = _c("#733E39") if z < 2 else _c("#B86F50")
            fill_c = _c("#E4A672") if z == num_slices - 1 else _c("#D77643")
            sdoc.rect(x0, y0, x1, y1, fill_c)
            if z in (0, 1, num_slices - 2, num_slices - 1):
                sdoc.rect(x0, y0, x1, y1, frame_c, fill=False)
            else:
                for px_, py_ in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
                    sdoc.rect(px_, py_, px_, py_, frame_c)

        elif pname == "tree":
            if z < num_slices // 3:
                tr = max(2, min(slice_w, slice_h) // 6)
                sdoc.circle(cx, cy, tr, _c("#733E39") if z < 2 else _c("#B86F50"), fill=True)
            else:
                kt = (z - num_slices // 3) / max(1, num_slices - num_slices // 3 - 1)
                r = max(2, round(min(slice_w, slice_h) * 0.42 * math.sin((0.2 + kt * 0.78) * math.pi)))
                col = _c("#265C42") if kt < 0.35 else (_c("#3E8948") if kt < 0.75 else _c("#63C74D"))
                sdoc.circle(cx, cy, r, col, fill=True)

        elif pname == "tower":
            r = max(3, round(min(slice_w, slice_h) * 0.36))
            if z < num_slices - 2:
                col = _c("#5A6988") if z % 2 == 0 else _c("#8B9BB4")
                sdoc.circle(cx, cy, r, col, fill=True)
            else:
                # Battlement crenels on top
                sdoc.circle(cx, cy, r + 1, _c("#C0CBDC"), fill=False)
                sdoc.circle(cx, cy, r - 1, _c("#3A4466"), fill=True)

        elif pname == "chest":
            x0, x1 = 2, slice_w - 3
            y0, y1 = 4, slice_h - 5
            if z < num_slices // 2:
                sdoc.rect(x0, y0, x1, y1, _c("#733E39"))
                sdoc.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, _c("#B86F50"))
            else:
                inset = max(0, int((z - num_slices // 2) * 0.6))
                sdoc.rect(x0, y0 + inset, x1, y1 - inset, _c("#D77643"))
                sdoc.rect(cx - 1, y1 - inset, cx + 1, y1 - inset, _c("#FEAE34"))

        strip.alpha_composite(sdoc.composite(1), (z * slice_w, 0))

    meta = {
        "preset": pname,
        "slice_width": slice_w,
        "slice_height": slice_h,
        "slice_count": num_slices,
        "strip_size": [slice_w * num_slices, slice_h],
        "recommended_squash": 0.75,
        "recommended_spacing": 1.0,
    }
    return strip, meta


def render_stack_angle(
    strip: Image.Image,
    slice_count: int,
    angle_deg: float,
    squash: float = 0.75,
    spacing: float = 1.0,
    outline_color: str | None = "#181425",
    add_shadow: bool = True,
) -> Image.Image:
    """Render a slice strip at `angle_deg` using symmetric pivot `(w-1)*0.5` & unified post-stack outline."""
    sw = strip.width // slice_count
    sh = strip.height
    diag = int(math.ceil(math.hypot(sw, sh))) + 6
    out_w = diag + 4
    out_h = int(math.ceil(diag * squash + slice_count * spacing)) + 8
    buf = Image.new("RGBA", (out_w, out_h), (0, 0, 0, 0))
    bpx = buf.load()

    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    scx, scy = (sw - 1) * 0.5, (sh - 1) * 0.5
    dcx = (out_w - 1) * 0.5
    base_y = out_h - 4 - diag * squash * 0.5

    # Extract slices once
    slices = [strip.crop((z * sw, 0, (z + 1) * sw, sh)).convert("RGBA").load() for z in range(slice_count)]

    # Ground shadow (union footprint of z=0 offset by +2,+2)
    if add_shadow:
        s0 = slices[0]
        for oy in range(out_h):
            dy = (oy - (base_y + 2)) / max(0.2, squash)
            for ox in range(out_w):
                dx = ox - (dcx + 2)
                sx = round(dx * cos_a + dy * sin_a + scx)
                sy = round(-dx * sin_a + dy * cos_a + scy)
                if 0 <= sx < sw and 0 <= sy < sh and s0[sx, sy][3] > 0:
                    bpx[ox, oy] = (24, 20, 37, 255)

    # Bottom-to-top slice stack (exact nearest-neighbor inverse rotation around symmetric center!)
    for z in range(slice_count):
        spx = slices[z]
        lift_y = base_y - round(z * spacing)
        for oy in range(out_h):
            dy = (oy - lift_y) / max(0.2, squash)
            if abs(dy) > diag * 0.55:
                continue
            for ox in range(out_w):
                dx = ox - dcx
                if abs(dx) > diag * 0.55:
                    continue
                sx = round(dx * cos_a + dy * sin_a + scx)
                sy = round(-dx * sin_a + dy * cos_a + scy)
                if 0 <= sx < sw and 0 <= sy < sh:
                    c = spx[sx, sy]
                    if c[3] > 0:
                        bpx[ox, oy] = c

    # Outline the finished stack ONCE (never per slice! Rule from danielwh2/sprite-stacking)
    if outline_color:
        doc = SpriteDocument(out_w, out_h, snap=False)
        doc.frames[0].cels["main"] = buf
        doc.outline(outline_color, where="outside")
        return doc.composite(1)
    return buf


def render_stack_turntable(
    strip: Image.Image,
    slice_count: int,
    frames: int = 16,
    fps: int = 12,
    squash: float = 0.75,
    spacing: float = 1.0,
    outline_color: str | None = "#181425",
) -> SpriteDocument:
    """Render a full 360-degree rotatable fake-3D turntable animation as a SpriteDocument."""
    first = render_stack_angle(strip, slice_count, 0.0, squash=squash, spacing=spacing, outline_color=outline_color)
    doc = SpriteDocument(first.width, first.height, snap=False, default_fps=fps)
    doc.frames[0].cels["main"] = first
    for fi in range(1, max(1, frames)):
        angle = (fi / frames) * 360.0
        doc.add_frame(copy=False)
        doc.frames[fi].cels["main"] = render_stack_angle(
            strip, slice_count, angle, squash=squash, spacing=spacing, outline_color=outline_color
        )
    doc.tag("turntable", 1, max(1, frames), direction="forward")
    return doc
