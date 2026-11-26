"""Seamless Toroidal Terrain, Wang 16-Tile & 47-Tile Blob Autotiles, Animated Tiles, and 2:1 Isometric Engine."""

from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Sequence

from PIL import Image

from .canvas import SpriteDocument
from .color import ColorRamp, RGBA, hex_to_rgba, load_palette, mix_color, nearest_color

# 47 canonical 8-bit neighbor bitmasks for standard Godot/RPG blob autotiling
# Bit layout: NW=1, N=2, NE=4, W=8, E=16, SW=32, S=64, SE=128
BLOB_47_MASKS: list[int] = [
    0, 2, 8, 10, 11, 16, 18, 22, 24, 26, 27, 30, 31,
    64, 66, 72, 74, 75, 80, 82, 86, 88, 90, 91, 94, 95,
    104, 106, 107, 120, 122, 123, 126, 127,
    208, 210, 214, 216, 218, 219, 222, 223,
    248, 250, 251, 254, 255,
]


def _fade(t: float) -> float:
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def toroidal_value_noise(w: int, h: int, period_x: int = 4, period_y: int = 4, octaves: int = 2, seed: int = 42) -> list[list[float]]:
    """Guaranteed 4-edge seamless periodic FBM value noise in [0.0, 1.0]."""
    rng = random.Random(seed)
    field = [[0.0] * w for _ in range(h)]
    amp = 1.0
    total_amp = 0.0
    px_cur = max(2, int(period_x))
    py_cur = max(2, int(period_y))

    for _ in range(max(1, octaves)):
        grid = [[rng.random() for _ in range(px_cur)] for _ in range(py_cur)]
        for y in range(h):
            fy = (y / h) * py_cur
            y0 = int(math.floor(fy)) % py_cur
            y1 = (y0 + 1) % py_cur
            ty = _fade(fy - math.floor(fy))
            for x in range(w):
                fx = (x / w) * px_cur
                x0 = int(math.floor(fx)) % px_cur
                x1 = (x0 + 1) % px_cur
                tx = _fade(fx - math.floor(fx))
                a = _lerp(grid[y0][x0], grid[y0][x1], tx)
                b = _lerp(grid[y1][x0], grid[y1][x1], tx)
                field[y][x] += _lerp(a, b, ty) * amp
        total_amp += amp
        amp *= 0.5
        px_cur = min(w, px_cur * 2)
        py_cur = min(h, py_cur * 2)

    for y in range(h):
        for x in range(w):
            field[y][x] = max(0.0, min(1.0, field[y][x] / max(1e-6, total_amp)))
    return field


def toroidal_voronoi(w: int, h: int, cells: int = 9, seed: int = 42) -> tuple[list[list[float]], list[list[int]]]:
    """Guaranteed 4-edge seamless toroidal Voronoi cell distances (border distance, cell_id)."""
    rng = random.Random(seed)
    pts = [(rng.random() * w, rng.random() * h) for _ in range(max(3, cells))]
    edge_dist = [[0.0] * w for _ in range(h)]
    cell_ids = [[0] * w for _ in range(h)]

    for y in range(h):
        for x in range(w):
            d1 = 1e9
            d2 = 1e9
            cid = 0
            for idx, (px_, py_) in enumerate(pts):
                dx = abs(x - px_)
                dx = min(dx, w - dx)
                dy = abs(y - py_)
                dy = min(dy, h - dy)
                d = math.hypot(dx, dy)
                if d < d1:
                    d2 = d1
                    d1 = d
                    cid = idx
                elif d < d2:
                    d2 = d
            edge_dist[y][x] = d2 - d1
            cell_ids[y][x] = cid
    return edge_dist, cell_ids


TERRAIN_PRESETS: dict[str, dict] = {
    "grass":       {"base": "#4E9A47", "accent": "#8CCF55", "edge": "#326B3E", "mode": "organic"},
    "dirt":        {"base": "#8F5E3B", "accent": "#B88156", "edge": "#5E3B28", "mode": "organic"},
    "stone":       {"base": "#6F7887", "accent": "#9AA6B5", "edge": "#454D5E", "mode": "voronoi"},
    "cobblestone": {"base": "#737A8C", "accent": "#A3AEBF", "edge": "#3D4252", "mode": "voronoi"},
    "brick":       {"base": "#A84A3E", "accent": "#CC6D56", "edge": "#4A292E", "mode": "brick"},
    "wood":        {"base": "#99643D", "accent": "#C28B5B", "edge": "#573623", "mode": "planks"},
    "water":       {"base": "#2E7EB8", "accent": "#73D2F2", "edge": "#1E4D82", "mode": "water"},
    "sand":        {"base": "#D9B26C", "accent": "#F2D999", "edge": "#A67C46", "mode": "organic"},
    "lava":        {"base": "#D94426", "accent": "#FFE055", "edge": "#6E1C26", "mode": "lava"},
    "snow":        {"base": "#C8DDF0", "accent": "#F2F8FF", "edge": "#7E9AB8", "mode": "organic"},
    "dungeon":     {"base": "#48455C", "accent": "#6E6A85", "edge": "#262336", "mode": "flagstone"},
}


def generate_seamless_tile(
    size: int = 16,
    terrain: str = "grass",
    palette: str | Sequence[str] | None = None,
    seed: int = 42,
    phase: float = 0.0,
) -> Image.Image:
    """Generate a guaranteed 4-edge seamless terrain tile (follows all 9 SKILL.md tile rules)."""
    preset = TERRAIN_PRESETS.get(terrain.lower(), TERRAIN_PRESETS["grass"])
    pal_rgbas = load_palette(palette)[1] if palette is not None else None

    def _mk_ramp(hex_c: str) -> ColorRamp:
        r = ColorRamp.from_base(terrain, hex_c, steps=4, hue_shift=16.0)
        return r.snap_to(pal_rgbas) if pal_rgbas else r

    ramp = _mk_ramp(preset["base"])
    accent_c = hex_to_rgba(preset["accent"])
    edge_c = hex_to_rgba(preset["edge"])
    if pal_rgbas:
        accent_c = nearest_color(accent_c, pal_rgbas)
        edge_c = nearest_color(edge_c, pal_rgbas)

    img = Image.new("RGBA", (size, size), ramp.mid)
    px = img.load()
    mode = preset["mode"]
    rng = random.Random(seed)

    if mode == "organic":
        noise = toroidal_value_noise(size, size, period_x=max(3, size // 4), period_y=max(3, size // 4), octaves=2, seed=seed)
        # 70% base, 15% dark accent, 10% light accent, 5% subtle highlight (Tile Rule #3!)
        for y in range(size):
            for x in range(size):
                v = noise[y][x]
                if v < 0.26:
                    px[x, y] = ramp.shadow
                elif v < 0.76:
                    px[x, y] = ramp.mid
                elif v < 0.90:
                    px[x, y] = ramp.light
                else:
                    px[x, y] = accent_c
        # Sparse asymmetric grass blades / pebbles (<= 2% feature budget, wrapped!)
        n_feats = max(2, (size * size) // 56)
        for _ in range(n_feats):
            fx = rng.randrange(size)
            fy = rng.randrange(size)
            px[fx, fy] = accent_c if terrain in ("grass", "snow") else ramp.shadow
            if terrain == "grass" and size >= 12:
                px[fx, (fy - 1) % size] = ramp.light
                px[(fx + 1) % size, fy] = ramp.shadow

    elif mode == "voronoi":
        cells = max(5, (size * size) // 48)
        ed, cids = toroidal_voronoi(size, size, cells=cells, seed=seed)
        noise = toroidal_value_noise(size, size, period_x=4, period_y=4, octaves=1, seed=seed + 7)
        cell_tones = [rng.choice((ramp.mid, ramp.mid, ramp.light, ramp.shadow)) for _ in range(cells)]
        for y in range(size):
            for x in range(size):
                if ed[y][x] < max(0.85, size * 0.055):
                    px[x, y] = edge_c
                else:
                    c = cell_tones[cids[y][x] % len(cell_tones)]
                    # Top-left facet highlight inside stone
                    up_border = ed[(y - 1) % size][x] < max(0.85, size * 0.055)
                    left_border = ed[y][(x - 1) % size] < max(0.85, size * 0.055)
                    if (up_border or left_border) and noise[y][x] > 0.35:
                        px[x, y] = ramp.light
                    else:
                        px[x, y] = c

    elif mode == "brick":
        rows = max(2, size // 6)
        cols = max(2, size // 8)
        bh = max(3, size // rows)
        bw = max(4, size // cols)
        noise = toroidal_value_noise(size, size, period_x=4, period_y=4, octaves=1, seed=seed)
        for y in range(size):
            row_idx = y // bh
            off = (bw // 2) if (row_idx % 2 == 1) else 0
            is_h_mortar = (y % bh == 0)
            for x in range(size):
                bx = (x + off) % size
                is_v_mortar = (bx % bw == 0)
                if is_h_mortar or is_v_mortar:
                    px[x, y] = edge_c
                elif y % bh == 1:
                    px[x, y] = ramp.light
                elif y % bh == bh - 1:
                    px[x, y] = ramp.shadow
                else:
                    px[x, y] = accent_c if noise[y][x] > 0.72 else ramp.mid

    elif mode == "planks":
        plank_h = max(4, size // 4)
        noise = toroidal_value_noise(size, size, period_x=2, period_y=max(2, size // 4), octaves=2, seed=seed)
        for y in range(size):
            p_idx = y // plank_h
            joint_x = ((p_idx * 7 + seed * 3) % size)
            for x in range(size):
                if y % plank_h == 0 or x == joint_x:
                    px[x, y] = edge_c
                elif y % plank_h == 1:
                    px[x, y] = ramp.light
                elif noise[y][x] > 0.65:
                    px[x, y] = ramp.shadow
                else:
                    px[x, y] = ramp.mid

    elif mode == "flagstone":
        half = max(4, size // 2)
        noise = toroidal_value_noise(size, size, period_x=4, period_y=4, octaves=2, seed=seed)
        for y in range(size):
            for x in range(size):
                bx = (x + (half // 2 if y >= half else 0)) % size
                if y in (0, half) or bx in (0, half):
                    px[x, y] = edge_c
                elif y in (1, half + 1):
                    px[x, y] = ramp.light
                elif noise[y][x] < 0.25:
                    px[x, y] = ramp.shadow
                else:
                    px[x, y] = ramp.mid

    elif mode in ("water", "lava"):
        # Smooth animated scrolling wave highlights (seamless for any phase in [0, 1))
        noise = toroidal_value_noise(size, size, period_x=max(2, size // 5), period_y=max(2, size // 5), octaves=2, seed=seed)
        shift_x = int(round(phase * size)) % size
        shift_y = int(round(phase * size * 0.5)) % size
        for y in range(size):
            for x in range(size):
                sx = (x + shift_x) % size
                sy = (y + shift_y) % size
                wave = 0.5 + 0.5 * math.sin(2.0 * math.pi * ((x / size) * 2.0 + phase) + noise[sy][sx] * 3.0)
                v = 0.55 * noise[sy][sx] + 0.45 * wave
                if v < 0.30:
                    px[x, y] = ramp.shadow
                elif v < 0.72:
                    px[x, y] = ramp.mid
                elif v < 0.88:
                    px[x, y] = ramp.light
                else:
                    px[x, y] = accent_c

    return img


def generate_animated_tile(
    size: int = 16,
    terrain: str = "water",
    frames: int = 6,
    fps: int = 6,
    palette: str | Sequence[str] | None = None,
    seed: int = 42,
) -> SpriteDocument:
    """Generate a seamlessly looping animated tile (water, lava, etc.)."""
    doc = SpriteDocument(size, size, palette=palette, snap=(palette is not None), default_fps=fps)
    for fi in range(max(1, frames)):
        if fi > 0:
            doc.add_frame(copy=False)
        tile = generate_seamless_tile(size=size, terrain=terrain, palette=palette, seed=seed, phase=fi / max(1, frames))
        doc.frames[fi].cels["main"] = tile
    doc.tag(f"{terrain}_loop", 1, max(1, frames), direction="forward")
    return doc


def _apply_autotile_borders(
    base: Image.Image,
    has_n: bool,
    has_e: bool,
    has_s: bool,
    has_w: bool,
    has_nw: bool = True,
    has_ne: bool = True,
    has_sw: bool = True,
    has_se: bool = True,
    edge_color: RGBA = (32, 26, 42, 255),
    top_highlight: RGBA | None = None,
) -> Image.Image:
    """Apply crisp exposed edges, darkened border trim, rounded outer corners, and inner corner cuts."""
    w, h = base.size
    out = base.copy()
    px = out.load()
    border_w = max(1, w // 12)

    def _darken(c: RGBA, factor: float = 0.65) -> RGBA:
        return (int(c[0] * factor), int(c[1] * factor), int(c[2] * factor), 255)

    # Exposed cardinal sides get crisp outline + shaded bevel
    if not has_n:
        for x in range(w):
            px[x, 0] = edge_color
            if top_highlight and h > 2:
                px[x, 1] = top_highlight
    if not has_s:
        for x in range(w):
            px[x, h - 1] = edge_color
            for dy in range(1, min(border_w + 1, h - 1)):
                px[x, h - 1 - dy] = _darken(px[x, h - 1 - dy], 0.72)
    if not has_w:
        for y in range(h):
            px[0, y] = edge_color
            if w > 2:
                px[1, y] = _darken(px[1, y], 0.85)
    if not has_e:
        for y in range(h):
            px[w - 1, y] = edge_color
            if w > 2:
                px[w - 2, y] = _darken(px[w - 2, y], 0.74)

    # Round outer corners where two exposed edges meet
    if not has_n and not has_w:
        px[0, 0] = (0, 0, 0, 0)
        if w > 2 and h > 2:
            px[1, 1] = edge_color
    if not has_n and not has_e:
        px[w - 1, 0] = (0, 0, 0, 0)
        if w > 2 and h > 2:
            px[w - 2, 1] = edge_color
    if not has_s and not has_w:
        px[0, h - 1] = (0, 0, 0, 0)
        if w > 2 and h > 2:
            px[1, h - 2] = edge_color
    if not has_s and not has_e:
        px[w - 1, h - 1] = (0, 0, 0, 0)
        if w > 2 and h > 2:
            px[w - 2, h - 2] = edge_color

    # Inner corner accents (47-tile blob mode!)
    if has_n and has_w and not has_nw:
        px[0, 0] = edge_color
    if has_n and has_e and not has_ne:
        px[w - 1, 0] = edge_color
    if has_s and has_w and not has_sw:
        px[0, h - 1] = edge_color
    if has_s and has_e and not has_se:
        px[w - 1, h - 1] = edge_color

    return out


def generate_autotile_sheet(
    tile_size: int = 16,
    terrain: str = "grass",
    mode: str = "wang16",
    palette: str | Sequence[str] | None = None,
    seed: int = 42,
) -> tuple[Image.Image, dict]:
    """Generate a complete 16-tile Wang or 47-tile Blob autotile sheet + bitmask JSON metadata."""
    base = generate_seamless_tile(size=tile_size, terrain=terrain, palette=palette, seed=seed)
    preset = TERRAIN_PRESETS.get(terrain.lower(), TERRAIN_PRESETS["grass"])
    pal_rgbas = load_palette(palette)[1] if palette is not None else None
    edge_c = hex_to_rgba(preset["edge"])
    hi_c = hex_to_rgba(preset["accent"])
    if pal_rgbas:
        edge_c = nearest_color(edge_c, pal_rgbas)
        hi_c = nearest_color(hi_c, pal_rgbas)

    tiles: list[tuple[int, Image.Image]] = []
    if mode == "blob47":
        for mask in BLOB_47_MASKS:
            t = _apply_autotile_borders(
                base,
                has_n=bool(mask & 2),
                has_e=bool(mask & 16),
                has_s=bool(mask & 64),
                has_w=bool(mask & 8),
                has_nw=bool(mask & 1),
                has_ne=bool(mask & 4),
                has_sw=bool(mask & 32),
                has_se=bool(mask & 128),
                edge_color=edge_c,
                top_highlight=hi_c,
            )
            tiles.append((mask, t))
        cols = 8
    else:
        # Wang 16: N=1, E=2, S=4, W=8
        for mask in range(16):
            t = _apply_autotile_borders(
                base,
                has_n=bool(mask & 1),
                has_e=bool(mask & 2),
                has_s=bool(mask & 4),
                has_w=bool(mask & 8),
                edge_color=edge_c,
                top_highlight=hi_c,
            )
            tiles.append((mask, t))
        cols = 4

    rows = math.ceil(len(tiles) / cols)
    sheet = Image.new("RGBA", (cols * tile_size, rows * tile_size), (0, 0, 0, 0))
    tile_meta = []
    for idx, (mask, im) in enumerate(tiles):
        r, c = divmod(idx, cols)
        x, y = c * tile_size, r * tile_size
        sheet.alpha_composite(im, (x, y))
        tile_meta.append({"index": idx, "bitmask": mask, "col": c, "row": r, "x": x, "y": y})

    meta = {
        "terrain": terrain,
        "mode": mode,
        "tile_size": tile_size,
        "tile_count": len(tiles),
        "columns": cols,
        "rows": rows,
        "tiles": tile_meta,
    }
    return sheet, meta


def generate_isometric_block(
    width: int = 64,
    terrain: str = "grass",
    wall_height: int | None = None,
    palette: str | Sequence[str] | None = None,
    seed: int = 42,
) -> Image.Image:
    """Generate a crisp 2:1 pixel-art isometric tile block (diamond top + left/right shaded walls)."""
    diamond_h = max(8, width // 2)
    wh = wall_height if wall_height is not None else max(4, diamond_h // 2)
    total_h = diamond_h + wh
    preset = TERRAIN_PRESETS.get(terrain.lower(), TERRAIN_PRESETS["grass"])
    pal_rgbas = load_palette(palette)[1] if palette is not None else None

    top_ramp = ColorRamp.from_base("top", preset["base"], steps=4)
    side_base = "#8F5E3B" if terrain == "grass" else preset["base"]
    side_ramp = ColorRamp.from_base("side", side_base, steps=4)
    outline_c = hex_to_rgba("#1E182B")
    if pal_rgbas:
        top_ramp = top_ramp.snap_to(pal_rgbas)
        side_ramp = side_ramp.snap_to(pal_rgbas)
        outline_c = nearest_color(outline_c, pal_rgbas)

    img = Image.new("RGBA", (width, total_h), (0, 0, 0, 0))
    px = img.load()
    half_w = width // 2
    half_dh = diamond_h // 2
    noise = toroidal_value_noise(width, total_h, period_x=6, period_y=6, octaves=2, seed=seed)

    # Top 2:1 diamond face (keep highlight within organic green/terrain ramp!)
    top_hi = hex_to_rgba(preset["accent"])
    if pal_rgbas:
        top_hi = nearest_color(top_hi, pal_rgbas)

    bottom_edge_y = [None] * width
    for y in range(diamond_h):
        span = (y + 1) * 2 if y < half_dh else (diamond_h - y) * 2
        x0 = max(0, half_w - span)
        x1 = min(width - 1, half_w + span - 1)
        for x in range(x0, x1 + 1):
            if x in (x0, x1):
                px[x, y] = outline_c
            else:
                v = noise[y][x]
                px[x, y] = top_hi if v > 0.76 else (top_ramp.light if v > 0.34 else top_ramp.mid)
            bottom_edge_y[x] = y

    # Left & Right vertical walls column-by-column dropping exact `wh` pixels from bottom diamond edge!
    for x in range(width):
        ey = bottom_edge_y[x]
        if ey is None:
            continue
        is_left_face = x < half_w
        for dy in range(1, wh + 1):
            ny = ey + dy
            if ny >= total_h:
                continue
            is_border = (x == 0 or x == width - 1 or x == half_w - 1 or x == half_w or dy == wh)
            if is_border:
                px[x, ny] = outline_c
            elif dy <= max(2, wh // 6) and terrain == "grass":
                px[x, ny] = top_ramp.mid if is_left_face else top_ramp.shadow
            elif is_left_face:
                px[x, ny] = side_ramp.light if noise[ny][x] > 0.65 else (side_ramp.mid if noise[ny][x] > 0.25 else side_ramp.shadow)
            else:
                px[x, ny] = side_ramp.shadow if noise[ny][x] > 0.30 else side_ramp.outline

    return img
