"""Color theory, hue-shifted ramps, perceptual matching, and palette management."""

from __future__ import annotations

import colorsys
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageDraw, ImageFont

RGBA = tuple[int, int, int, int]
RGB = tuple[int, int, int]

PALETTES_DIR = Path(__file__).resolve().parent.parent / "palettes"

# Built-in fallback palettes (kept in sync with palettes/*.json)
PALETTES: dict[str, list[str]] = {
    "onebit": ["#11111B", "#F5F5F0"],
    "gameboy": ["#0F380F", "#306230", "#8BAC0F", "#9BBC0F"],
    "pico-8": [
        "#000000", "#1D2B53", "#7E2553", "#008751",
        "#AB5236", "#5F574F", "#C2C3C7", "#FFF1E8",
        "#FF004D", "#FFA300", "#FFEC27", "#00E436",
        "#29ADFF", "#83769C", "#FF77A8", "#FFCCAA",
    ],
    "sweetie-16": [
        "#1A1C2C", "#5D275D", "#B13E53", "#EF7D57",
        "#FFCD75", "#A7F070", "#38B764", "#257179",
        "#29366F", "#3B5DC9", "#41A6F6", "#73EFF7",
        "#F4F4F4", "#94B0C2", "#566C86", "#333C57",
    ],
    "db32": [
        "#000000", "#222034", "#45283C", "#663931",
        "#8F563B", "#DF7126", "#D9A066", "#EEC39A",
        "#FBF236", "#99E550", "#6ABE30", "#37946E",
        "#4B692F", "#524B24", "#323C39", "#3F3F74",
        "#306082", "#5B6EE1", "#639BFF", "#5FCDE4",
        "#CBDBFC", "#FFFFFF", "#9BADB7", "#847E87",
        "#696A6A", "#595652", "#76428A", "#AC3232",
        "#D95763", "#D77BBA", "#8F974A", "#8A6F30",
    ],
    "endesga-32": [
        "#BE4A2F", "#D77643", "#EAD4AA", "#E4A672",
        "#B86F50", "#733E39", "#3E2731", "#A22633",
        "#E43B44", "#F77622", "#FEAE34", "#FEE761",
        "#63C74D", "#3E8948", "#265C42", "#193C3E",
        "#124E89", "#0099DB", "#2CE8F5", "#FFFFFF",
        "#C0CBDC", "#8B9BB4", "#5A6988", "#3A4466",
        "#262B44", "#181425", "#FF0044", "#68386C",
        "#B55088", "#F6757A", "#E8B796", "#C28569",
    ],
    "fantasy-24": [
        "#1F1827", "#34263B", "#523B52", "#7C5A68",
        "#B28582", "#E2BFA6", "#F7E5CA", "#D94E4E",
        "#E8854D", "#F2C75C", "#7BC253", "#3B8C52",
        "#21524B", "#2D6B8C", "#4FA6C9", "#9AE2F2",
        "#4A437A", "#7B69B5", "#C49AE6", "#A6633C",
        "#6E3B28", "#47251E", "#7C8C99", "#BCCAD6",
    ],
    "cyberpunk-16": [
        "#0D0917", "#1B1536", "#31235E", "#5A338F",
        "#9B44C9", "#FF3CA6", "#FF85C8", "#00F5D4",
        "#00B4D8", "#0077B6", "#FFE66D", "#FF9F1C",
        "#FF4D4D", "#3D4C6E", "#8B9BB4", "#F0F6FF",
    ],
    "pastel-16": [
        "#2E2538", "#574866", "#8B779E", "#C8B8D9",
        "#FFF8F0", "#FFE1CC", "#F5B5B5", "#E88491",
        "#F7D694", "#B8E3A3", "#7AC29A", "#4B8F7C",
        "#94D4E8", "#6CA6D9", "#8E8CE0", "#D49CE0",
    ],
}

# Aliases for convenience
_PALETTE_ALIASES = {
    "pico8": "pico-8",
    "sweetie16": "sweetie-16",
    "endesga32": "endesga-32",
    "resurrect64": "resurrect-64",
    "c64": "commodore-64",
    "gb": "gameboy",
    "aap64": "aap-64",
    "lospec500": "lospec-500",
    "fantasy24": "fantasy-24",
    "cyberpunk16": "cyberpunk-16",
    "pastel16": "pastel-16",
    "1bit": "onebit",
}


def hex_to_rgba(color: str | Sequence[int] | None) -> RGBA:
    """Convert '#RGB', '#RRGGBB', '#RRGGBBAA', (r,g,b[,a]), or None to RGBA tuple."""
    if color is None:
        return (0, 0, 0, 0)
    if isinstance(color, (tuple, list)):
        vals = tuple(max(0, min(255, int(v))) for v in color)
        if len(vals) == 3:
            return (vals[0], vals[1], vals[2], 255)
        if len(vals) == 4:
            return (vals[0], vals[1], vals[2], vals[3])
        raise ValueError(f"Expected 3 or 4 color channels, got {len(vals)}")
    s = str(color).strip().lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    if len(s) == 6:
        s += "FF"
    if len(s) != 8:
        raise ValueError(f"Invalid hex color: {color!r}")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), int(s[6:8], 16))


def rgba_to_hex(color: Sequence[int], include_alpha: bool = False) -> str:
    """Convert RGBA/RGB tuple to uppercase hex string."""
    r, g, b = int(color[0]), int(color[1]), int(color[2])
    if include_alpha and len(color) > 3:
        return f"#{r:02X}{g:02X}{b:02X}{int(color[3]):02X}"
    return f"#{r:02X}{g:02X}{b:02X}"


def perceptual_dist2(a: Sequence[int], b: Sequence[int]) -> float:
    """Weighted redmean perceptual RGB distance squared (better than flat Euclidean)."""
    rmean = (a[0] + b[0]) * 0.5
    dr = a[0] - b[0]
    dg = a[1] - b[1]
    db = a[2] - b[2]
    return (2.0 + rmean / 256.0) * dr * dr + 4.0 * dg * dg + (2.0 + (255.0 - rmean) / 256.0) * db * db


def nearest_color(color: Sequence[int], palette_rgba: Sequence[RGBA]) -> RGBA:
    """Find the perceptually nearest color in a palette."""
    return min(palette_rgba, key=lambda p: perceptual_dist2(color, p))


def luminance(color: Sequence[int]) -> float:
    """Relative luminance (0.0 to 1.0)."""
    return (0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]) / 255.0


def contrast_ratio(c1: Sequence[int], c2: Sequence[int]) -> float:
    """WCAG-style contrast ratio between two RGB colors."""
    def _lin(ch: int) -> float:
        s = ch / 255.0
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

    l1 = 0.2126 * _lin(c1[0]) + 0.7152 * _lin(c1[1]) + 0.0722 * _lin(c1[2])
    l2 = 0.2126 * _lin(c2[0]) + 0.7152 * _lin(c2[1]) + 0.0722 * _lin(c2[2])
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def mix_color(c1: str | Sequence[int], c2: str | Sequence[int], t: float = 0.5) -> RGBA:
    """Linearly blend two colors."""
    a, b = hex_to_rgba(c1), hex_to_rgba(c2)
    t = max(0.0, min(1.0, float(t)))
    return (
        round(a[0] + (b[0] - a[0]) * t),
        round(a[1] + (b[1] - a[1]) * t),
        round(a[2] + (b[2] - a[2]) * t),
        round(a[3] + (b[3] - a[3]) * t),
    )


def _rotate_hue_toward(hue_deg: float, target_deg: float, amount_deg: float) -> float:
    diff = ((target_deg - hue_deg + 180.0) % 360.0) - 180.0
    step = max(-amount_deg, min(amount_deg, diff))
    return (hue_deg + step) % 360.0


def hue_ramp(
    base: str | Sequence[int],
    steps: int = 5,
    hue_shift: float = 18.0,
    dark: float = 0.48,
    light: float = 0.55,
    cool_target: float = 245.0,
    warm_target: float = 55.0,
) -> list[str]:
    """Generate a hue-shifted pixel art shading ramp (dark -> light).

    Shadows rotate cool (toward indigo/purple/blue) with rich saturation;
    highlights rotate warm (toward yellow/cream) with slightly softer saturation.
    Middle index equals `base` when `steps` is odd.
    """
    r, g, b, _ = hex_to_rgba(base)
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    hdeg = h * 360.0
    v_dark = max(0.08, v * (1.0 - dark))
    v_light = min(0.98, v + (1.0 - v) * light)

    out: list[str] = []
    for i in range(steps):
        t = i / (steps - 1) if steps > 1 else 0.5
        vv = v_dark + (v_light - v_dark) * t
        if t < 0.5:
            f = (0.5 - t) * 2.0
            hh = _rotate_hue_toward(hdeg, cool_target, f * hue_shift)
            ss = min(1.0, s * (1.0 + 0.18 * f)) if s > 0.05 else s + 0.08 * f
        else:
            f = (t - 0.5) * 2.0
            hh = _rotate_hue_toward(hdeg, warm_target, f * hue_shift)
            ss = max(0.0, s * (1.0 - 0.35 * f))
        rr, gg, bb = colorsys.hsv_to_rgb(hh / 360.0, max(0.0, min(1.0, ss)), max(0.0, min(1.0, vv)))
        out.append(rgba_to_hex((round(rr * 255), round(gg * 255), round(bb * 255))))
    if steps % 2 == 1:
        out[steps // 2] = rgba_to_hex((r, g, b))
    return out


@dataclass(frozen=True)
class ColorRamp:
    """Named shading ramp from darkest (0) to brightest (-1)."""

    name: str
    colors: tuple[RGBA, ...]

    @classmethod
    def from_base(cls, name: str, base: str | Sequence[int], steps: int = 4, hue_shift: float = 18.0) -> "ColorRamp":
        hexes = hue_ramp(base, steps=steps, hue_shift=hue_shift)
        return cls(name=name, colors=tuple(hex_to_rgba(c) for c in hexes))

    @property
    def outline(self) -> RGBA:
        return self.colors[0]

    @property
    def shadow(self) -> RGBA:
        return self.colors[min(1, len(self.colors) - 1)]

    @property
    def mid(self) -> RGBA:
        return self.colors[len(self.colors) // 2]

    @property
    def light(self) -> RGBA:
        return self.colors[max(0, len(self.colors) - 2)]

    @property
    def highlight(self) -> RGBA:
        return self.colors[-1]

    def snap_to(self, palette_rgba: Sequence[RGBA]) -> "ColorRamp":
        return ColorRamp(
            name=self.name,
            colors=tuple(nearest_color(c, palette_rgba) for c in self.colors),
        )


def list_palettes() -> list[str]:
    """Return sorted list of all available palette names (JSON files + built-ins)."""
    names = set(PALETTES.keys())
    if PALETTES_DIR.is_dir():
        for p in PALETTES_DIR.glob("*.json"):
            names.add(p.stem)
    return sorted(names)


def load_palette(name_or_path: str | Path | Sequence[str]) -> tuple[str, list[RGBA]]:
    """Load a palette from a built-in name, a JSON path, or an explicit list of colors."""
    if isinstance(name_or_path, (list, tuple)):
        return ("custom", [hex_to_rgba(c) for c in name_or_path])

    raw = str(name_or_path).strip()
    path = Path(raw)
    if path.exists() and path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
        return (data.get("name", path.stem), [hex_to_rgba(c) for c in data["colors"]])

    key = _PALETTE_ALIASES.get(raw.lower(), raw.lower())
    json_candidate = PALETTES_DIR / f"{key}.json"
    if json_candidate.exists():
        data = json.loads(json_candidate.read_text(encoding="utf-8"))
        return (data.get("name", key), [hex_to_rgba(c) for c in data["colors"]])

    if key in PALETTES:
        return (key, [hex_to_rgba(c) for c in PALETTES[key]])

    available = ", ".join(list_palettes())
    raise FileNotFoundError(f"Palette {name_or_path!r} not found. Available: {available}")


def load_palette_hex(name_or_path: str | Path | Sequence[str]) -> tuple[str, list[str]]:
    name, rgbas = load_palette(name_or_path)
    return name, [rgba_to_hex(c) for c in rgbas]


def render_swatch(colors: Iterable[str | Sequence[int]], cell: int = 32, cols: int = 16) -> Image.Image:
    """Render a clean labeled palette swatch image."""
    rgba_list = [hex_to_rgba(c) for c in colors]
    n = max(1, len(rgba_list))
    cols = min(cols, n)
    rows = math.ceil(n / cols)
    label_h = 16
    img = Image.new("RGB", (cols * cell, rows * (cell + label_h)), (24, 24, 34))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    for i, c in enumerate(rgba_list):
        r, col = divmod(i, cols)
        x0 = col * cell
        y0 = r * (cell + label_h)
        draw.rectangle([x0, y0, x0 + cell - 1, y0 + cell - 1], fill=c[:3])
        draw.text((x0 + 2, y0 + cell + 2), str(i), fill=(210, 210, 225), font=font)
    return img
