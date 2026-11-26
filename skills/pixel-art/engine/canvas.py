"""Core multi-layer, multi-frame pixel art canvas & document engine.

Features:
- Arbitrary canvas resolutions (8x8, 9x9, 12x12, 16x16, 24x24, 32x32, 48x48, 64x64, WxH)
- Multi-layer stack with visibility, opacity (0..255), blend modes, z-order, linked cels
- Pixel-perfect Bresenham lines, L-corner removal, midpoint circles, symmetric ellipses, capsules, ASCII grids
- Masking (`only="opaque" | "empty" | color`) for effortless shifted-shape shading
- Selective outlines (selout), rim light, Bayer 2/4/8 dithering, band-edge dithering
- Hybrid AI/photo cleanup pipeline (auto-scale detect, strip checker, harden alpha, despeckle, dedupe, dehalo, smooth edge)
- Inspection helpers: labeled contact sheet, onion-skin strip, silhouette test, ASCII ruler grid
"""

from __future__ import annotations

import base64
import colorsys
import io
import json
import math
import random as _random
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Sequence

from PIL import Image, ImageChops, ImageDraw, ImageFont

from .color import (
    RGBA,
    hex_to_rgba,
    load_palette,
    luminance,
    mix_color,
    nearest_color,
    rgba_to_hex,
)

_R = getattr(Image, "Resampling", Image)
NEAREST = _R.NEAREST
_T = getattr(Image, "Transpose", Image)
FLIP_LR = _T.FLIP_LEFT_RIGHT
FLIP_TB = _T.FLIP_TOP_BOTTOM


def _expand_bayer(m: list[list[int]]) -> list[list[int]]:
    n = len(m)
    out = [[0] * (2 * n) for _ in range(2 * n)]
    for y in range(n):
        for x in range(n):
            v = 4 * m[y][x]
            out[y][x] = v
            out[y][x + n] = v + 2
            out[y + n][x] = v + 3
            out[y + n][x + n] = v + 1
    return out


BAYER2 = [[0, 2], [3, 1]]
BAYER4 = _expand_bayer(BAYER2)
BAYER8 = _expand_bayer(BAYER4)
DITHER_PATTERNS = {
    "bayer2": BAYER2,
    "bayer4": BAYER4,
    "bayer8": BAYER8,
    "checker": BAYER2,
}

BLEND_MODES = ("normal", "multiply", "screen", "add", "overlay")


def _blend_pixel(dst: RGBA, src: RGBA, mode: str, layer_opacity: int) -> RGBA:
    """Blend a single source pixel onto destination using pixel-art-safe compositing."""
    sa_raw = src[3]
    if sa_raw == 0 or layer_opacity == 0:
        return dst
    sa = (sa_raw * layer_opacity) / (255.0 * 255.0)
    if mode == "normal" and sa >= 0.999:
        return (src[0], src[1], src[2], 255)

    dr, dg, db, da_raw = dst
    da = da_raw / 255.0
    sr, sg, sb = src[0] / 255.0, src[1] / 255.0, src[2] / 255.0
    drf, dgf, dbf = dr / 255.0, dg / 255.0, db / 255.0

    if mode == "multiply":
        br, bg, bb = drf * sr, dgf * sg, dbf * sb
    elif mode == "screen":
        br = 1.0 - (1.0 - drf) * (1.0 - sr)
        bg = 1.0 - (1.0 - dgf) * (1.0 - sg)
        bb = 1.0 - (1.0 - dbf) * (1.0 - sb)
    elif mode == "add":
        br, bg, bb = min(1.0, drf + sr), min(1.0, dgf + sg), min(1.0, dbf + sb)
    elif mode == "overlay":
        def _ov(d: float, s: float) -> float:
            return 2.0 * d * s if d < 0.5 else 1.0 - 2.0 * (1.0 - d) * (1.0 - s)
        br, bg, bb = _ov(drf, sr), _ov(dgf, sg), _ov(dbf, sb)
    else:
        br, bg, bb = sr, sg, sb

    if da_raw == 0:
        return (round(sr * 255), round(sg * 255), round(sb * 255), round(sa * 255))

    out_a = sa + da * (1.0 - sa)
    if out_a <= 0:
        return (0, 0, 0, 0)
    # Porter-Duff source-over with blended color
    cr = (sa * (1.0 - da) * sr + sa * da * br + (1.0 - sa) * da * drf) / out_a
    cg = (sa * (1.0 - da) * sg + sa * da * bg + (1.0 - sa) * da * dgf) / out_a
    cb = (sa * (1.0 - da) * sb + sa * da * bb + (1.0 - sa) * da * dbf) / out_a
    return (
        max(0, min(255, round(cr * 255))),
        max(0, min(255, round(cg * 255))),
        max(0, min(255, round(cb * 255))),
        max(0, min(255, round(out_a * 255))),
    )


def composite_layer_onto(base: Image.Image, layer_img: Image.Image, mode: str = "normal", opacity: int = 255) -> Image.Image:
    """Composite `layer_img` over `base` respecting blend mode and layer opacity."""
    if opacity <= 0:
        return base
    if mode == "normal" and opacity >= 255:
        return Image.alpha_composite(base, layer_img)

    out = base.copy()
    opx = out.load()
    lpx = layer_img.load()
    w, h = out.size
    for y in range(h):
        for x in range(w):
            sp = lpx[x, y]
            if sp[3] > 0:
                opx[x, y] = _blend_pixel(opx[x, y], sp, mode, opacity)
    return out


@dataclass
class Layer:
    """Layer metadata within a SpriteDocument."""

    name: str
    visible: bool = True
    opacity: int = 255
    blend_mode: str = "normal"
    locked: bool = False
    group: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "visible": self.visible,
            "opacity": self.opacity,
            "blend_mode": self.blend_mode,
            "locked": self.locked,
            "group": self.group,
        }


@dataclass
class Frame:
    """Single timeline frame holding per-layer RGBA cels and millisecond duration."""

    duration_ms: int = 100
    cels: dict[str, Image.Image] = field(default_factory=dict)


class SpriteDocument:
    """Layered, multi-frame pixel art document with pixel-perfect drawing & export.

    Frames are 1-indexed in public methods (`frame(1)` .. `frame(n)`).
    Coordinates are `(x, y)` with `(0, 0)` at top-left.
    """

    def __init__(
        self,
        width: int,
        height: int,
        palette: str | Sequence[str] | None = None,
        snap: bool = True,
        default_fps: int = 10,
    ):
        self.width = int(width)
        self.height = int(height)
        if self.width < 1 or self.height < 1:
            raise ValueError(f"Canvas dimensions must be >= 1, got {width}x{height}")
        self.snap = snap
        self.palette_name: str = "custom"
        self.palette: list[RGBA] | None = None
        self._pal_rgb: set[tuple[int, int, int]] = set()
        if palette is not None:
            self.set_palette(palette, snap=snap)

        self.layers: list[Layer] = [Layer("main")]
        dur = max(16, round(1000 / max(1, default_fps)))
        self.frames: list[Frame] = [Frame(duration_ms=dur, cels={"main": self._blank()})]
        self._f: int = 0
        self._l: str = "main"
        self.tags: dict[str, dict] = {}
        self.metadata: dict = {}

    # ---------------- properties & helpers ----------------

    @property
    def w(self) -> int:
        return self.width

    @property
    def h(self) -> int:
        return self.height

    @property
    def n_frames(self) -> int:
        return len(self.frames)

    @property
    def current_frame(self) -> int:
        return self._f + 1

    @property
    def current_layer(self) -> str:
        return self._l

    @property
    def layer_names(self) -> list[str]:
        return [l.name for l in self.layers]

    def _blank(self) -> Image.Image:
        return Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))

    def _get_layer_meta(self, name: str) -> Layer:
        for l in self.layers:
            if l.name == name:
                return l
        raise KeyError(f"Unknown layer: {name!r}")

    def _img(self) -> Image.Image:
        fr = self.frames[self._f]
        if self._l not in fr.cels:
            fr.cels[self._l] = self._blank()
        return fr.cels[self._l]

    def _resolve_color(self, color: str | Sequence[int] | int | None) -> RGBA:
        if isinstance(color, bool):
            raise ValueError("color cannot be bool")
        if isinstance(color, int):
            if not self.palette:
                raise ValueError("Palette index used without a locked palette")
            return self.palette[color % len(self.palette)]
        c = hex_to_rgba(color)
        if c[3] == 0:
            return (0, 0, 0, 0)
        if self.palette and self.snap and c[:3] not in self._pal_rgb:
            p = nearest_color(c, self.palette)
            return (p[0], p[1], p[2], c[3])
        return c

    def _only_ok(self, im: Image.Image, x: int, y: int, only) -> bool:
        if only is None:
            return True
        cur = im.getpixel((x, y))
        if only == "opaque":
            return cur[3] > 0
        if only == "empty":
            return cur[3] == 0
        oc = self._resolve_color(only)
        return cur[3] > 0 and cur[:3] == oc[:3]

    def _put(self, im: Image.Image, x: int, y: int, c: RGBA, only=None) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            if self._only_ok(im, x, y, only):
                im.putpixel((x, y), c)

    # ---------------- layer & frame management ----------------

    def layer(
        self,
        name: str,
        above: str | None = None,
        below: str | None = None,
        opacity: int | None = None,
        blend_mode: str | None = None,
        visible: bool | None = None,
        group: str = "",
    ) -> "SpriteDocument":
        """Create (if missing) and select a layer."""
        existing = next((l for l in self.layers if l.name == name), None)
        if existing is None:
            bm = blend_mode or "normal"
            if bm not in BLEND_MODES:
                raise ValueError(f"Unsupported blend mode {bm!r}. Choose from {BLEND_MODES}")
            meta = Layer(
                name=name,
                visible=True if visible is None else visible,
                opacity=255 if opacity is None else max(0, min(255, int(opacity))),
                blend_mode=bm,
                group=group,
            )
            names = self.layer_names
            if above is not None and above in names:
                self.layers.insert(names.index(above) + 1, meta)
            elif below is not None and below in names:
                self.layers.insert(names.index(below), meta)
            else:
                self.layers.append(meta)
            for fr in self.frames:
                fr.cels.setdefault(name, self._blank())
        else:
            if opacity is not None:
                existing.opacity = max(0, min(255, int(opacity)))
            if blend_mode is not None:
                if blend_mode not in BLEND_MODES:
                    raise ValueError(f"Unsupported blend mode {blend_mode!r}")
                existing.blend_mode = blend_mode
            if visible is not None:
                existing.visible = bool(visible)
            if group:
                existing.group = group
        self._l = name
        return self

    def ensure_rig_layers(self, names: Sequence[str], remove_default_main: bool = True) -> "SpriteDocument":
        """Initialize an ordered bottom-to-top layer rig in one call."""
        for name in names:
            self.layer(name)
        if remove_default_main and "main" in self.layer_names and "main" not in names and len(self.layers) > 1:
            self.delete_layer("main")
        self._l = names[-1]
        return self

    def delete_layer(self, name: str) -> "SpriteDocument":
        if len(self.layers) <= 1:
            raise ValueError("Cannot delete the last remaining layer")
        self.layers = [l for l in self.layers if l.name != name]
        for fr in self.frames:
            fr.cels.pop(name, None)
        if self._l == name:
            self._l = self.layers[-1].name
        return self

    def set_layer_visibility(self, name: str, visible: bool) -> "SpriteDocument":
        self._get_layer_meta(name).visible = bool(visible)
        return self

    def reorder_layers(self, new_order: Sequence[str]) -> "SpriteDocument":
        by_name = {l.name: l for l in self.layers}
        if set(new_order) != set(by_name.keys()):
            raise ValueError("new_order must contain exact set of existing layer names")
        self.layers = [by_name[n] for n in new_order]
        return self

    def frame(self, index: int) -> "SpriteDocument":
        if not 1 <= index <= len(self.frames):
            raise IndexError(f"Frame {index} out of range 1..{len(self.frames)}")
        self._f = index - 1
        return self

    def use(self, frame: int | None = None, layer: str | None = None) -> "SpriteDocument":
        if frame is not None:
            self.frame(frame)
        if layer is not None:
            self.layer(layer)
        return self

    def add_frame(self, copy: bool = True, duration_ms: int | None = None, after: int | None = None) -> int:
        src = self.frames[self._f]
        fr = Frame(duration_ms=duration_ms if duration_ms is not None else src.duration_ms)
        for l in self.layers:
            cel = src.cels.get(l.name)
            fr.cels[l.name] = cel.copy() if (copy and cel is not None) else self._blank()
        pos = len(self.frames) if after is None else int(after)
        self.frames.insert(pos, fr)
        self._f = pos
        return pos + 1

    def set_duration(self, ms: int, frames: str | Sequence[int] | None = None) -> "SpriteDocument":
        if frames is None:
            self.frames[self._f].duration_ms = max(1, int(ms))
        elif frames == "all":
            for fr in self.frames:
                fr.duration_ms = max(1, int(ms))
        else:
            for i in frames:
                self.frames[i - 1].duration_ms = max(1, int(ms))
        return self

    def set_fps(self, fps: float, frames: str | Sequence[int] | None = "all") -> "SpriteDocument":
        ms = max(16, round(1000.0 / max(0.5, float(fps))))
        return self.set_duration(ms, frames=frames)

    def link_cel(self, layer: str | None = None, from_frame: int | None = None, to_frames: str | Sequence[int] = "rest") -> "SpriteDocument":
        """Share a cel image object across frames (linked cel)."""
        ln = layer or self._l
        ff = from_frame or self.current_frame
        src = self.frames[ff - 1].cels.get(ln)
        if src is None:
            src = self._blank()
            self.frames[ff - 1].cels[ln] = src
        targets = [i for i in range(1, len(self.frames) + 1) if i != ff] if to_frames == "rest" else list(to_frames)
        for i in targets:
            self.frames[i - 1].cels[ln] = src
        return self

    def tag(self, name: str, from_frame: int, to_frame: int, direction: str = "forward") -> "SpriteDocument":
        if not (1 <= from_frame <= to_frame <= len(self.frames)):
            raise ValueError(f"Invalid tag range {from_frame}..{to_frame} (have {len(self.frames)} frames)")
        if direction not in ("forward", "reverse", "pingpong", "ping-pong"):
            raise ValueError(f"Invalid tag direction: {direction!r}")
        norm_dir = "pingpong" if direction == "ping-pong" else direction
        self.tags[name] = {"from": int(from_frame), "to": int(to_frame), "direction": norm_dir}
        return self

    def tag_frame_indices(self, tag: str | None = None) -> list[int]:
        """Return 0-based frame indices for playback of `tag` (or all frames)."""
        if tag is None:
            return list(range(len(self.frames)))
        t = self.tags[tag]
        idx = list(range(t["from"] - 1, t["to"]))
        if t["direction"] == "reverse":
            return idx[::-1]
        if t["direction"] == "pingpong" and len(idx) > 2:
            return idx + idx[-2:0:-1]
        return idx

    # ---------------- palette management ----------------

    def set_palette(self, palette: str | Sequence[str], snap: bool = True, remap: bool = False) -> "SpriteDocument":
        name, rgbas = load_palette(palette)
        self.palette_name = name
        self.palette = rgbas
        self._pal_rgb = {p[:3] for p in rgbas}
        self.snap = snap
        if remap:
            self.remap_to_palette(rgbas)
        return self

    def remap_to_palette(self, palette: str | Sequence[str] | Sequence[RGBA], dither: bool = False) -> "SpriteDocument":
        if isinstance(palette, (str, Path)) or (palette and isinstance(palette[0], str)):
            name, rgbas = load_palette(palette)  # type: ignore[arg-type]
        else:
            name, rgbas = "custom", [tuple(c) for c in palette]  # type: ignore[misc]

        for fr in self.frames:
            for ln, cel in fr.cels.items():
                px = cel.load()
                if not dither:
                    for y in range(self.height):
                        for x in range(self.width):
                            r, g, b, a = px[x, y]
                            if a > 0:
                                nr, ng, nb, _ = nearest_color((r, g, b), rgbas)
                                px[x, y] = (nr, ng, nb, a)
                else:
                    # Ordered Bayer 4x4 dithering toward palette
                    for y in range(self.height):
                        for x in range(self.width):
                            r, g, b, a = px[x, y]
                            if a > 0:
                                bias = ((BAYER4[y % 4][x % 4] / 16.0) - 0.5) * 32.0
                                cr = max(0, min(255, int(r + bias)))
                                cg = max(0, min(255, int(g + bias)))
                                cb = max(0, min(255, int(b + bias)))
                                nr, ng, nb, _ = nearest_color((cr, cg, cb), rgbas)
                                px[x, y] = (nr, ng, nb, a)
        self.palette_name = name
        self.palette = list(rgbas)
        self._pal_rgb = {p[:3] for p in rgbas}
        return self

    # ---------------- pixel-perfect drawing primitives ----------------

    def px(self, x: int, y: int, color, only=None) -> "SpriteDocument":
        self._put(self._img(), int(x), int(y), self._resolve_color(color), only)
        return self

    def get(self, x: int, y: int, composite: bool = False) -> RGBA | None:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None
        im = self.composite(self.current_frame) if composite else self._img()
        c = im.getpixel((int(x), int(y)))
        return None if c[3] == 0 else c

    def line(self, x0: int, y0: int, x1: int, y1: int, color, pixel_perfect: bool = False, only=None) -> "SpriteDocument":
        """Bresenham line; `pixel_perfect=True` strips L-shaped double corners."""
        im, c = self._img(), self._resolve_color(color)
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        pts: list[tuple[int, int]] = []
        while True:
            pts.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy
        if pixel_perfect and len(pts) > 2:
            cleaned = [pts[0]]
            i = 1
            while i < len(pts) - 1:
                prev_pt = cleaned[-1]
                cur_pt = pts[i]
                next_pt = pts[i + 1]
                # Remove L-corner pixel when prev -> next is a pure 1-step diagonal
                if abs(prev_pt[0] - next_pt[0]) == 1 and abs(prev_pt[1] - next_pt[1]) == 1:
                    i += 1
                    continue
                cleaned.append(cur_pt)
                i += 1
            cleaned.append(pts[-1])
            pts = cleaned
        for x, y in pts:
            self._put(im, x, y, c, only)
        return self

    def rect(self, x0: int, y0: int, x1: int, y1: int, color, fill: bool = True, only=None) -> "SpriteDocument":
        im, c = self._img(), self._resolve_color(color)
        x0, x1 = sorted((int(x0), int(x1)))
        y0, y1 = sorted((int(y0), int(y1)))
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if fill or x in (x0, x1) or y in (y0, y1):
                    self._put(im, x, y, c, only)
        return self

    def rounded_rect(self, x0: int, y0: int, x1: int, y1: int, color, radius: int = 1, fill: bool = True, only=None) -> "SpriteDocument":
        """Crisp pixel-art rounded rectangle (clipped corners)."""
        im, c = self._img(), self._resolve_color(color)
        x0, x1 = sorted((int(x0), int(x1)))
        y0, y1 = sorted((int(y0), int(y1)))
        r = max(0, min(radius, (x1 - x0) // 2, (y1 - y0) // 2))
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                dx = max(0, (x0 + r) - x, x - (x1 - r))
                dy = max(0, (y0 + r) - y, y - (y1 - r))
                if dx + dy > r and (dx > 0 and dy > 0):
                    continue
                if fill:
                    self._put(im, x, y, c, only)
                else:
                    on_edge = x in (x0, x1) or y in (y0, y1) or (dx + dy == r and dx > 0 and dy > 0)
                    if on_edge:
                        self._put(im, x, y, c, only)
        return self

    def circle(self, cx: int, cy: int, r: int, color, fill: bool = True, only=None) -> "SpriteDocument":
        """Symmetric pixel-perfect midpoint circle."""
        im, c = self._img(), self._resolve_color(color)
        cx, cy, r = int(cx), int(cy), int(r)
        if r <= 0:
            self._put(im, cx, cy, c, only)
            return self
        pts: set[tuple[int, int]] = set()
        x, y, d = r, 0, 3 - 2 * r
        while y <= x:
            for px_, py_ in ((x, y), (y, x), (-x, y), (-y, x), (x, -y), (y, -x), (-x, -y), (-y, -x)):
                pts.add((cx + px_, cy + py_))
            if d <= 0:
                d += 4 * y + 6
            else:
                d += 4 * (y - x) + 10
                x -= 1
            y += 1
        if fill:
            spans: dict[int, tuple[int, int]] = {}
            for px_, py_ in pts:
                lo, hi = spans.get(py_, (px_, px_))
                spans[py_] = (min(lo, px_), max(hi, px_))
            for py_, (lo, hi) in spans.items():
                for px_ in range(lo, hi + 1):
                    self._put(im, px_, py_, c, only)
        else:
            for px_, py_ in pts:
                self._put(im, px_, py_, c, only)
        return self

    def ellipse(self, x0: int, y0: int, x1: int, y1: int, color, fill: bool = True, only=None) -> "SpriteDocument":
        """Exact symmetric pixel-art ellipse (avoids lopsided PIL ellipses at small sizes)."""
        im, c = self._img(), self._resolve_color(color)
        x0, x1 = sorted((int(x0), int(x1)))
        y0, y1 = sorted((int(y0), int(y1)))
        cx = (x0 + x1) * 0.5
        cy = (y0 + y1) * 0.5
        rx = max(0.5, (x1 - x0 + 1) * 0.5)
        ry = max(0.5, (y1 - y0 + 1) * 0.5)
        inside: set[tuple[int, int]] = set()
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                nx = (x - cx) / rx
                ny = (y - cy) / ry
                if nx * nx + ny * ny <= 1.0:
                    inside.add((x, y))
        for x, y in inside:
            if fill or any((x + dx, y + dy) not in inside for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                self._put(im, x, y, c, only)
        return self

    def capsule(self, x0: float, y0: float, x1: float, y1: float, r0: float, r1: float | None = None, color=None, only=None) -> "SpriteDocument":
        """Tapered articulated limb/segment capsule (Codixel-inspired)."""
        im, c = self._img(), self._resolve_color(color)
        r1 = r0 if r1 is None else r1
        max_r = max(r0, r1) + 1.0
        min_x = max(0, int(math.floor(min(x0, x1) - max_r)))
        max_x = min(self.width - 1, int(math.ceil(max(x0, x1) + max_r)))
        min_y = max(0, int(math.floor(min(y0, y1) - max_r)))
        max_y = min(self.height - 1, int(math.ceil(max(y0, y1) + max_r)))
        vx, vy = x1 - x0, y1 - y0
        len2 = vx * vx + vy * vy
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                if len2 < 1e-6:
                    t = 0.0
                else:
                    t = max(0.0, min(1.0, ((x - x0) * vx + (y - y0) * vy) / len2))
                px_ = x0 + t * vx
                py_ = y0 + t * vy
                rad = r0 + (r1 - r0) * t
                if (x - px_) ** 2 + (y - py_) ** 2 <= rad * rad:
                    self._put(im, x, y, c, only)
        return self

    def polygon(self, points: Sequence[tuple[int, int]], color, fill: bool = True, only=None) -> "SpriteDocument":
        c = self._resolve_color(color)
        tmp = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        d = ImageDraw.Draw(tmp)
        pts = [(int(x), int(y)) for x, y in points]
        if fill:
            d.polygon(pts, fill=c)
        else:
            d.line(pts + [pts[0]], fill=c, width=1)
        im = self._img()
        tp = tmp.load()
        for y in range(self.height):
            for x in range(self.width):
                if tp[x, y][3] > 0:
                    self._put(im, x, y, tp[x, y], only)
        return self

    def flood_fill(self, x: int, y: int, color) -> "SpriteDocument":
        if 0 <= x < self.width and 0 <= y < self.height:
            ImageDraw.floodfill(self._img(), (int(x), int(y)), self._resolve_color(color))
        return self

    def grid(self, text: str, key_map: dict[str, str | Sequence[int] | None], x0: int = 0, y0: int = 0, only=None) -> "SpriteDocument":
        """Stamp an ASCII pixel art grid onto the current cel (claude-pxl style).

        '.' and space are skipped; '_' erases to transparent unless overridden in key_map.
        """
        im = self._img()
        lines = [ln.strip() for ln in text.strip("\n").splitlines() if ln.strip()]
        for dy, row in enumerate(lines):
            for dx, ch in enumerate(row):
                if ch in (".", " ") and ch not in key_map:
                    continue
                if ch == "_" and ch not in key_map:
                    self._put(im, x0 + dx, y0 + dy, (0, 0, 0, 0), only)
                    continue
                if ch in key_map:
                    self._put(im, x0 + dx, y0 + dy, self._resolve_color(key_map[ch]), only)
        return self

    def paste_image(self, img: Image.Image, x: int = 0, y: int = 0) -> "SpriteDocument":
        src = img.convert("RGBA")
        im = self._img()
        im.alpha_composite(src, (int(x), int(y)))
        return self

    def clear(self, color=None) -> "SpriteDocument":
        self.frames[self._f].cels[self._l] = Image.new("RGBA", (self.width, self.height), self._resolve_color(color))
        return self

    # ---------------- pixel-art shading, outlines & transforms ----------------

    def outline(
        self,
        color,
        where: str = "outside",
        diagonals: bool = False,
        target_layer: str | None = None,
    ) -> "SpriteDocument":
        """Add a crisp 1px outline around opaque pixels on current (or target) cel."""
        prev_l = self._l
        if target_layer:
            self.layer(target_layer)
        im = self._img()
        c = self._resolve_color(color)
        src = im.load()
        alpha = [[src[x, y][3] > 0 for x in range(self.width)] for y in range(self.height)]
        nb = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if diagonals:
            nb += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        todo: list[tuple[int, int]] = []
        for y in range(self.height):
            for x in range(self.width):
                if where == "outside" and not alpha[y][x]:
                    if any(0 <= x + dx < self.width and 0 <= y + dy < self.height and alpha[y + dy][x + dx] for dx, dy in nb):
                        todo.append((x, y))
                elif where == "inside" and alpha[y][x]:
                    if any(not (0 <= x + dx < self.width and 0 <= y + dy < self.height) or not alpha[y + dy][x + dx] for dx, dy in nb):
                        todo.append((x, y))
        for x, y in todo:
            src[x, y] = c
        self._l = prev_l
        return self

    def selout(
        self,
        dark_color: str | Sequence[int] = "#1B1630",
        light_dir: tuple[int, int] = (-1, -1),
        tint_strength: float = 0.42,
        diagonals: bool = False,
        composite_mode: bool = False,
    ) -> "SpriteDocument":
        """Selective hue-shifted outline (Codixel / MortMort style).

        Edge pixels facing the light take a slightly brighter tinted shade of their adjacent
        fill color; shadow-side edges approach `dark_color`.
        """
        dark_rgba = self._resolve_color(dark_color)
        im = self.composite(self.current_frame) if composite_mode else self._img()
        src = im.load()
        out_im = self._img()
        opx = out_im.load()
        nb = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if diagonals:
            nb += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        lx, ly = light_dir
        todo: list[tuple[int, int, RGBA]] = []
        for y in range(self.height):
            for x in range(self.width):
                if src[x, y][3] > 0:
                    continue
                neighbors = []
                lit_dot = 0.0
                for dx, dy in nb:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height and src[nx, ny][3] > 0:
                        neighbors.append(src[nx, ny])
                        # Normal pointing outward from shape is (-dx, -dy)
                        lit_dot += (-dx * lx) + (-dy * ly)
                if not neighbors:
                    continue
                # Average neighbor color
                ar = sum(p[0] for p in neighbors) // len(neighbors)
                ag = sum(p[1] for p in neighbors) // len(neighbors)
                ab = sum(p[2] for p in neighbors) // len(neighbors)
                # Facing light -> keep more neighbor tint; shadow side -> darker ink
                t = tint_strength if lit_dot > 0 else tint_strength * 0.35
                oc = mix_color(dark_rgba, (ar, ag, ab, 255), t)
                oc = (oc[0], oc[1], oc[2], 255)
                if self.palette and self.snap:
                    p = nearest_color(oc, self.palette)
                    oc = (p[0], p[1], p[2], 255)
                todo.append((x, y, oc))
        for x, y, oc in todo:
            opx[x, y] = oc
        return self

    def rim_light(self, light_dir: tuple[int, int] = (-1, -1), brighten: float = 0.25) -> "SpriteDocument":
        """Brighten outer opaque edge pixels facing `light_dir` (call BEFORE selout!)."""
        im = self._img()
        px = im.load()
        lx, ly = light_dir
        todo: list[tuple[int, int, RGBA]] = []
        for y in range(self.height):
            for x in range(self.width):
                r, g, b, a = px[x, y]
                if a == 0:
                    continue
                nx, ny = x + lx, y + ly
                exposed_to_light = not (0 <= nx < self.width and 0 <= ny < self.height) or px[nx, ny][3] == 0
                if exposed_to_light:
                    # Warm highlight shift toward pale cream
                    lit = mix_color((r, g, b, 255), (255, 248, 224, 255), brighten)
                    if self.palette and self.snap:
                        p = nearest_color(lit, self.palette)
                        lit = (p[0], p[1], p[2], 255)
                    todo.append((x, y, lit))
        for x, y, c in todo:
            px[x, y] = c
        return self

    def dither(self, x0: int, y0: int, x1: int, y1: int, c1, c2, mix: float = 0.5, pattern: str = "bayer4", only=None) -> "SpriteDocument":
        im = self._img()
        m = DITHER_PATTERNS[pattern]
        n = len(m)
        n2 = n * n
        cc1 = None if c1 == "keep" else self._resolve_color(c1)
        cc2 = None if c2 == "keep" else self._resolve_color(c2)
        x0, x1 = sorted((int(x0), int(x1)))
        y0, y1 = sorted((int(y0), int(y1)))
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                thr = (m[y % n][x % n] + 0.5) / n2
                c = cc2 if mix > thr else cc1
                if c is not None:
                    self._put(im, x, y, c, only)
        return self

    def band_dither(
        self,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        colors: Sequence,
        axis: str = "v",
        strip: float = 0.25,
        pattern: str = "bayer4",
        only=None,
    ) -> "SpriteDocument":
        """Codixel-style flat color bands with ordered dither ONLY at band borders."""
        im = self._img()
        m = DITHER_PATTERNS[pattern]
        n = len(m)
        n2 = n * n
        cols = [self._resolve_color(c) for c in colors]
        k = len(cols)
        if k == 0:
            return self
        x0, x1 = sorted((int(x0), int(x1)))
        y0, y1 = sorted((int(y0), int(y1)))
        span = max(1, (y1 - y0) if axis == "v" else (x1 - x0))
        half_strip = max(0.0, min(0.5, strip * 0.5))
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                t = ((y - y0) if axis == "v" else (x - x0)) / span
                pos = t * (k - 1)
                idx = min(int(pos), max(0, k - 2))
                frac = pos - idx
                if k == 1:
                    c = cols[0]
                elif frac < 0.5 - half_strip:
                    c = cols[idx]
                elif frac > 0.5 + half_strip:
                    c = cols[idx + 1]
                else:
                    local_t = (frac - (0.5 - half_strip)) / max(1e-6, 2.0 * half_strip)
                    thr = (m[y % n][x % n] + 0.5) / n2
                    c = cols[idx + 1] if local_t > thr else cols[idx]
                self._put(im, x, y, c, only)
        return self

    def mirror_x(self, source: str = "left") -> "SpriteDocument":
        im = self._img()
        half = self.width // 2
        if source == "left":
            part = im.crop((0, 0, half, self.height)).transpose(FLIP_LR)
            im.paste(part, (self.width - half, 0))
        else:
            part = im.crop((self.width - half, 0, self.width, self.height)).transpose(FLIP_LR)
            im.paste(part, (0, 0))
        return self

    def flip_all_horizontal(self) -> "SpriteDocument":
        for fr in self.frames:
            for ln in list(fr.cels.keys()):
                fr.cels[ln] = fr.cels[ln].transpose(FLIP_LR)
        return self

    def shift(self, dx: int, dy: int, wrap: bool = False) -> "SpriteDocument":
        im = self._img()
        if wrap:
            self.frames[self._f].cels[self._l] = ImageChops.offset(im, int(dx), int(dy))
        else:
            out = self._blank()
            out.paste(im, (int(dx), int(dy)))
            self.frames[self._f].cels[self._l] = out
        return self

    def swap_colors(self, mapping: dict, frames="all", layers="all") -> "SpriteDocument":
        resolved = {self._resolve_color(k)[:3]: self._resolve_color(v) for k, v in mapping.items()}
        fidx = range(len(self.frames)) if frames == "all" else [f - 1 for f in frames]
        lnames = self.layer_names if layers == "all" else list(layers)
        for fi in fidx:
            for ln in lnames:
                cel = self.frames[fi].cels.get(ln)
                if cel is None:
                    continue
                px = cel.load()
                for y in range(self.height):
                    for x in range(self.width):
                        r, g, b, a = px[x, y]
                        if a > 0 and (r, g, b) in resolved:
                            nc = resolved[(r, g, b)]
                            px[x, y] = (nc[0], nc[1], nc[2], a if nc[3] == 255 else nc[3])
        return self

    # ---------------- cleanup pipeline (messy / AI-gen PNGs) ----------------

    def _iter_cels(self, frames=None, layers=None):
        fidx = [self._f] if frames is None else (range(len(self.frames)) if frames == "all" else [i - 1 for i in frames])
        lnames = [self._l] if layers is None else (self.layer_names if layers == "all" else list(layers))
        for fi in fidx:
            for ln in lnames:
                cel = self.frames[fi].cels.get(ln)
                if cel is not None:
                    yield fi, ln, cel

    def harden_alpha(self, threshold: int = 128, frames="all", layers="all") -> "SpriteDocument":
        for _, _, cel in self._iter_cels(frames, layers):
            px = cel.load()
            for y in range(self.height):
                for x in range(self.width):
                    r, g, b, a = px[x, y]
                    if 0 < a < 255:
                        px[x, y] = (r, g, b, 255 if a >= threshold else 0)
        return self

    def despeckle(self, min_cluster: int = 2, frames="all", layers="all") -> "SpriteDocument":
        for _, _, cel in self._iter_cels(frames, layers):
            px = cel.load()
            seen = [[False] * self.width for _ in range(self.height)]
            kill = []
            for sy in range(self.height):
                for sx in range(self.width):
                    if seen[sy][sx] or px[sx, sy][3] == 0:
                        continue
                    stack, comp = [(sx, sy)], []
                    while stack:
                        cx, cy = stack.pop()
                        if cx < 0 or cy < 0 or cx >= self.width or cy >= self.height:
                            continue
                        if seen[cy][cx] or px[cx, cy][3] == 0:
                            continue
                        seen[cy][cx] = True
                        comp.append((cx, cy))
                        stack.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])
                    if len(comp) < min_cluster:
                        kill.extend(comp)
            for cx, cy in kill:
                px[cx, cy] = (0, 0, 0, 0)
        return self

    def dedupe_colors(self, tol: int = 12, frames="all", layers="all") -> "SpriteDocument":
        reps: dict[tuple[int, int, int], tuple[int, int, int]] = {}
        for _, _, cel in self._iter_cels(frames, layers):
            px = cel.load()
            counts = Counter()
            for y in range(self.height):
                for x in range(self.width):
                    r, g, b, a = px[x, y]
                    if a > 0:
                        counts[(r, g, b)] += 1
            for key, _ in counts.most_common():
                if key in reps:
                    continue
                rep = next((c for c in reps.values() if max(abs(c[k] - key[k]) for k in range(3)) <= tol), key)
                reps[key] = rep
            for y in range(self.height):
                for x in range(self.width):
                    r, g, b, a = px[x, y]
                    if a > 0:
                        rep = reps[(r, g, b)]
                        px[x, y] = (rep[0], rep[1], rep[2], a)
        return self

    def dehalo(self, sat_floor: float = 0.12, val_floor: float = 0.15, frames="all", layers="all") -> "SpriteDocument":
        for _, _, cel in self._iter_cels(frames, layers):
            px = cel.load()
            todo = []
            for y in range(self.height):
                for x in range(self.width):
                    r, g, b, a = px[x, y]
                    if a < 255:
                        continue
                    is_edge = False
                    nab = []
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            nr, ng, nb, na = px[nx, ny]
                            if na == 0:
                                is_edge = True
                            else:
                                nab.append((nr, ng, nb))
                        else:
                            is_edge = True
                    if not is_edge or not nab:
                        continue
                    _, ss, vv = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
                    if ss > sat_floor or vv < val_floor or vv > (1.0 - val_floor):
                        continue
                    avg = tuple(sum(c[i] for c in nab) // len(nab) for i in range(3))
                    todo.append((x, y, avg))
            for x, y, avg in todo:
                px[x, y] = (avg[0], avg[1], avg[2], 255)
        return self

    def clean(
        self,
        palette: str | Sequence[str] | None = None,
        max_colors: int | None = None,
        dither: bool = False,
        harden: bool = True,
        despeckle_min: int = 2,
        dedupe_tol: int = 10,
        dehalo: bool = True,
    ) -> "SpriteDocument":
        """Full deterministic pixel-art cleanup pipeline for AI-generated or messy PNGs."""
        if harden:
            self.harden_alpha()
        if despeckle_min > 1:
            self.despeckle(min_cluster=despeckle_min)
        if dedupe_tol > 0:
            self.dedupe_colors(tol=dedupe_tol)
        if dehalo:
            self.dehalo()
        if palette is not None:
            self.remap_to_palette(palette, dither=dither)
        elif max_colors is not None and max_colors > 0:
            # Adaptive median-cut quantization across all frames while preserving alpha
            strip = Image.new("RGBA", (self.width, self.height * len(self.frames)), (0, 0, 0, 0))
            for i in range(len(self.frames)):
                strip.paste(self.composite(i + 1), (0, i * self.height))
            opaque_pixels = [p[:3] for p in strip.getdata() if p[3] > 0]
            if opaque_pixels:
                sample = Image.new("RGB", (len(opaque_pixels), 1))
                sample.putdata(opaque_pixels)
                q = sample.quantize(colors=min(max_colors, 256), method=Image.Quantize.MEDIANCUT)
                raw_pal = q.getpalette()[: min(max_colors, 256) * 3]
                cols = [
                    (raw_pal[i], raw_pal[i + 1], raw_pal[i + 2], 255)
                    for i in range(0, len(raw_pal), 3)
                ]
                # Deduplicate palette entries
                unique_cols = list(dict.fromkeys(cols))
                self.remap_to_palette(unique_cols, dither=dither)
        return self

    # ---------------- compositing & inspection ----------------

    def composite(self, frame: int | None = None, layers: Sequence[str] | None = None) -> Image.Image:
        """Flatten visible layers (or subset `layers`) for a 1-based frame."""
        fr = self.frames[(frame or self.current_frame) - 1]
        out = self._blank()
        allowed = set(layers) if layers is not None else None
        for meta in self.layers:
            if allowed is not None:
                if meta.name not in allowed:
                    continue
            elif not meta.visible:
                continue
            cel = fr.cels.get(meta.name)
            if cel is not None:
                out = composite_layer_onto(out, cel, mode=meta.blend_mode, opacity=meta.opacity)
        return out

    def flatten(self) -> "SpriteDocument":
        for i, fr in enumerate(self.frames):
            merged = self.composite(i + 1)
            fr.cels = {"main": merged}
        self.layers = [Layer("main")]
        self._l = "main"
        return self

    def used_colors(self, frame: int | None = None, all_frames: bool = True) -> Counter:
        cnt: Counter = Counter()
        targets = range(1, len(self.frames) + 1) if all_frames else [frame or self.current_frame]
        for fi in targets:
            im = self.composite(fi)
            px = im.load()
            for y in range(self.height):
                for x in range(self.width):
                    r, g, b, a = px[x, y]
                    if a > 0:
                        cnt[(r, g, b)] += 1
        return cnt

    @staticmethod
    def _checker_bg(wpx: int, hpx: int, sq: int = 8) -> Image.Image:
        bg = Image.new("RGB", (wpx, hpx), (235, 235, 240))
        d = ImageDraw.Draw(bg)
        for y in range(0, hpx, sq):
            for x in range(0, wpx, sq):
                if ((x // sq) + (y // sq)) % 2:
                    d.rectangle([x, y, x + sq - 1, y + sq - 1], fill=(210, 212, 222))
        return bg

    def preview_image(
        self,
        scale: int = 6,
        cols: int = 8,
        bg: str = "checker",
        grid: bool = False,
        labels: bool = True,
        frames: Sequence[int] | None = None,
    ) -> Image.Image:
        """Build a labeled, upscaled contact sheet for visual inspection."""
        idx = [f - 1 for f in frames] if frames else list(range(len(self.frames)))
        n = len(idx)
        cols = max(1, min(cols, n))
        rows = math.ceil(n / cols)
        cw, chh = self.width * scale, self.height * scale
        lh = 16 if labels else 0
        sep = 4
        W = cols * cw + (cols + 1) * sep
        H = rows * (chh + lh) + (rows + 1) * sep
        sheet = Image.new("RGB", (W, H), (44, 46, 58))
        font = ImageFont.load_default()
        for k, fi in enumerate(idx):
            r, c = divmod(k, cols)
            ox = sep + c * (cw + sep)
            oy = sep + r * (chh + lh + sep)
            if labels:
                ImageDraw.Draw(sheet).rectangle([ox, oy, ox + cw - 1, oy + lh - 1], fill=(242, 244, 248))
                ImageDraw.Draw(sheet).text((ox + 3, oy + 2), f"F{fi + 1} {self.frames[fi].duration_ms}ms", fill=(35, 38, 52), font=font)
            cbg = self._checker_bg(cw, chh) if bg == "checker" else Image.new("RGB", (cw, chh), hex_to_rgba(bg)[:3])
            cell = cbg.convert("RGBA")
            art = self.composite(fi + 1).resize((cw, chh), NEAREST)
            cell.alpha_composite(art)
            if grid and scale >= 4:
                ov = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
                od = ImageDraw.Draw(ov)
                for gx in range(1, self.width):
                    od.line([(gx * scale, 0), (gx * scale, chh)], fill=(0, 0, 0, 75 if gx % 8 == 0 else 28))
                for gy in range(1, self.height):
                    od.line([(0, gy * scale), (cw, gy * scale)], fill=(0, 0, 0, 75 if gy % 8 == 0 else 28))
                cell.alpha_composite(ov)
            sheet.paste(cell.convert("RGB"), (ox, oy + lh))
        return sheet

    def onion_preview(self, frame: int, scale: int = 6) -> Image.Image:
        """Render frame `frame` with previous frame ghosted red & next frame ghosted cyan."""
        cw, chh = self.width * scale, self.height * scale
        cell = self._checker_bg(cw, chh).convert("RGBA")

        def _tint(im: Image.Image, rgb: tuple[int, int, int], alpha: int) -> Image.Image:
            out = Image.new("RGBA", im.size, (0, 0, 0, 0))
            spx, opx = im.load(), out.load()
            for y in range(im.height):
                for x in range(im.width):
                    if spx[x, y][3] > 0:
                        opx[x, y] = (rgb[0], rgb[1], rgb[2], alpha)
            return out

        if frame > 1:
            prev_im = _tint(self.composite(frame - 1), (230, 70, 90), 90).resize((cw, chh), NEAREST)
            cell.alpha_composite(prev_im)
        if frame < len(self.frames):
            next_im = _tint(self.composite(frame + 1), (60, 180, 240), 90).resize((cw, chh), NEAREST)
            cell.alpha_composite(next_im)
        cur_im = self.composite(frame).resize((cw, chh), NEAREST)
        cell.alpha_composite(cur_im)
        return cell.convert("RGB")

    def silhouette_image(self, frame: int | None = None, scale: int = 6, fg: str = "#1A1C2C", bg: str = "#EDEAE2") -> Image.Image:
        im = self.composite(frame)
        f = hex_to_rgba(fg)[:3]
        b = hex_to_rgba(bg)[:3]
        out = Image.new("RGB", (self.width, self.height), b)
        spx, opx = im.load(), out.load()
        for y in range(self.height):
            for x in range(self.width):
                if spx[x, y][3] > 0:
                    opx[x, y] = f
        return out.resize((self.width * scale, self.height * scale), NEAREST)

    def ascii_view(self, frame: int | None = None, layer: str | None = None) -> str:
        """Render the pixel grid as ASCII symbols with X/Y coordinate rulers (claude-pxl style)."""
        im = (
            self.frames[(frame or self.current_frame) - 1].cels.get(layer, self._blank())
            if layer
            else self.composite(frame)
        )
        px = im.load()
        symbols = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%&*+=-"
        color_to_sym: dict[tuple[int, int, int], str] = {}
        rows = []
        header = "    " + "".join(str(x % 10) for x in range(self.width))
        rows.append(header)
        for y in range(self.height):
            line_chars = []
            for x in range(self.width):
                r, g, b, a = px[x, y]
                if a == 0:
                    line_chars.append(".")
                else:
                    key = (r, g, b)
                    if key not in color_to_sym:
                        idx = len(color_to_sym)
                        color_to_sym[key] = symbols[idx] if idx < len(symbols) else "?"
                    line_chars.append(color_to_sym[key])
            rows.append(f"{y:2d}: " + "".join(line_chars))
        legend = [f"  {sym} = {rgba_to_hex(rgb)}" for rgb, sym in color_to_sym.items()]
        return "\n".join(rows + ["Legend:"] + legend)

    # ---------------- project serialization (.pxproj.json) ----------------

    def save_project(self, path: str | Path) -> Path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "engine": "pixelforge",
            "version": "1.0.0",
            "width": self.width,
            "height": self.height,
            "snap": self.snap,
            "palette_name": self.palette_name,
            "palette": [rgba_to_hex(c) for c in self.palette] if self.palette else None,
            "layers": [l.to_dict() for l in self.layers],
            "tags": self.tags,
            "metadata": self.metadata,
            "frames": [],
        }
        for fr in self.frames:
            cels_b64 = {}
            for ln, cel in fr.cels.items():
                buf = io.BytesIO()
                cel.save(buf, "PNG")
                cels_b64[ln] = base64.b64encode(buf.getvalue()).decode("ascii")
            data["frames"].append({"duration_ms": fr.duration_ms, "cels": cels_b64})
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return p

    @classmethod
    def load_project(cls, path: str | Path) -> "SpriteDocument":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        doc = cls(
            data["width"],
            data["height"],
            palette=data.get("palette"),
            snap=data.get("snap", True),
        )
        doc.palette_name = data.get("palette_name", "custom")
        doc.layers = [Layer(**ld) for ld in data["layers"]]
        doc.tags = {k: dict(v) for k, v in data.get("tags", {}).items()}
        doc.metadata = dict(data.get("metadata", {}))
        doc.frames = []
        for fd in data["frames"]:
            fr = Frame(duration_ms=fd.get("duration_ms", 100))
            for ln, b64 in fd["cels"].items():
                fr.cels[ln] = Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGBA")
            doc.frames.append(fr)
        doc._f = 0
        doc._l = doc.layers[0].name
        return doc

    @classmethod
    def from_png(
        cls,
        path: str | Path,
        scale: str | int | float = "auto",
        strip_bg: bool = False,
    ) -> "SpriteDocument":
        im = Image.open(path).convert("RGBA")
        if strip_bg:
            im = strip_checker(im)
        if scale == "auto":
            s = detect_scale(im)
            method = "nearest"
            if s == 1:
                est = estimate_scale(im)
                if est > 1:
                    s = est
                    method = "block"
        else:
            sf = float(scale)
            method = "nearest" if sf.is_integer() else "block"
            s = max(1, int(sf)) if sf.is_integer() else sf
        if s > 1:
            im = (
                im.resize((int(im.width // s), int(im.height // s)), NEAREST)
                if method == "nearest"
                else block_downscale(im, s)
            )
        doc = cls(im.width, im.height, snap=False)
        doc.frames[0].cels["main"] = im
        doc.metadata["detected_scale"] = s
        doc.metadata["import_method"] = method
        return doc


# ---------------- image recovery helpers ----------------


def detect_scale(im: Image.Image) -> int:
    """Detect exact integer upscale factor s where image is pure s×s blocks."""
    w, h = im.size
    g = math.gcd(w, h)
    divs = sorted({d for d in range(2, g + 1) if g % d == 0}, reverse=True)
    raw = im.tobytes()
    for s in divs:
        if w // s < 4 or h // s < 4:
            continue
        small = im.resize((w // s, h // s), NEAREST)
        if small.resize((w, h), NEAREST).tobytes() == raw:
            return s
    return 1


def estimate_scale(im: Image.Image) -> int:
    """Median run-length scale estimate for resampled / AI-upscaled pixel art."""
    p = im.load()
    runs = []
    step = max(1, im.height // 32)
    for y in range(0, im.height, step):
        run = 1
        for x in range(1, im.width):
            a, b = p[x - 1, y], p[x, y]
            if max(abs(a[i] - b[i]) for i in range(3)) < 24 and abs(a[3] - b[3]) < 64:
                run += 1
            else:
                if 1 < run < 40:
                    runs.append(run)
                run = 1
    if not runs:
        return 1
    runs.sort()
    return runs[len(runs) // 2]


def block_downscale(im: Image.Image, scale: float) -> Image.Image:
    """Dominant-color modal block downscaling (avoids blurry averaging)."""
    w, h = im.size
    tw, th = max(1, round(w / scale)), max(1, round(h / scale))
    small = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    sp, px = small.load(), im.load()
    for ty in range(th):
        y0 = int(ty * scale)
        y1 = max(y0 + 1, min(h, int((ty + 1) * scale)))
        for tx in range(tw):
            x0 = int(tx * scale)
            x1 = max(x0 + 1, min(w, int((tx + 1) * scale)))
            buckets: dict = {}
            for y in range(y0, y1):
                for x in range(x0, x1):
                    r, g, b, a = px[x, y]
                    key = None if a < 128 else (r >> 3, g >> 3, b >> 3)
                    n, sr, sg, sb = buckets.get(key, (0, 0, 0, 0))
                    buckets[key] = (n + 1, sr + r, sg + g, sb + b)
            win_key, (n, sr, sg, sb) = max(buckets.items(), key=lambda kv: kv[1][0])
            sp[tx, ty] = (0, 0, 0, 0) if win_key is None else (sr // n, sg // n, sb // n, 255)
    return small


def strip_checker(im: Image.Image) -> Image.Image:
    """Strip baked-in light-gray checkerboard backgrounds common in AI exports."""
    out = im.convert("RGBA").copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a > 0 and abs(r - g) < 14 and abs(g - b) < 22 and r > 180 and b > 170:
                px[x, y] = (0, 0, 0, 0)
    return out
