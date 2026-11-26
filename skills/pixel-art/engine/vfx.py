"""Seeded Two-Buffer Procedural Pixel Art VFX Engine (inspired by patch-gg/pixelfx & codixel).

Every effect renders into deterministic quantized palette ramps with zero semi-transparent AA:
- explosion, fire, smoke, slash, sparkle, magic_orb, lightning, water_splash,
  heal_aura, hit_impact, portal, coin_spin
- Supports arbitrary WxH (8x8 .. 128x128+), arbitrary frame counts (2..60), arbitrary FPS,
  reproducible seeds, and custom color palettes!
"""

from __future__ import annotations

import math
import random
from typing import Sequence

from PIL import Image

from .canvas import BAYER4, SpriteDocument
from .color import RGBA, hex_to_rgba, load_palette, nearest_color

VFX_TYPES = (
    "explosion", "fire", "smoke", "slash", "sparkle", "magic_orb",
    "lightning", "water_splash", "heal_aura", "hit_impact", "portal", "coin_spin",
)

VFX_RAMPS: dict[str, list[str]] = {
    "explosion":    ["#2B1A2B", "#7A2338", "#D94426", "#FA941E", "#FFE85C", "#FFFDF0"],
    "fire":         ["#3D1626", "#99242C", "#E65C22", "#FCA82B", "#FFF06B", "#FFFFF2"],
    "smoke":        ["#252333", "#434057", "#6E6D87", "#A3A5BD", "#D6DAE8"],
    "slash":        ["#24284A", "#3B5DC9", "#41A6F6", "#8CF2FF", "#FFFFFF"],
    "sparkle":      ["#6E3E26", "#D98A2B", "#FFD94A", "#FFF7A8", "#FFFFFF"],
    "magic_orb":    ["#22143B", "#5A2A8A", "#9B44D4", "#E07AFF", "#FFE8FF"],
    "lightning":    ["#1A224A", "#2C5ED9", "#4CC9FF", "#B8F4FF", "#FFFFFF"],
    "water_splash": ["#1A3B66", "#2B74B8", "#4CB8F0", "#A6ECFF", "#FFFFFF"],
    "heal_aura":    ["#1A4A3B", "#2B945A", "#5CE07A", "#B8FFAB", "#F5FFF2"],
    "hit_impact":   ["#4A1A2C", "#CC2B44", "#FF784A", "#FFE066", "#FFFFFF"],
    "portal":       ["#18102E", "#48227A", "#8C3AD9", "#4CC9FF", "#B8F8FF", "#FFFFFF"],
    "coin_spin":    ["#4A2A1A", "#A86324", "#E8A62E", "#FFE055", "#FFFAD6"],
}


def _resolve_ramp(vfx_type: str, palette: str | Sequence[str] | None) -> list[RGBA]:
    raw = [hex_to_rgba(c) for c in VFX_RAMPS.get(vfx_type, VFX_RAMPS["explosion"])]
    if palette is None:
        return raw
    _, pal_rgbas = load_palette(palette)
    return [nearest_color(c, pal_rgbas) for c in raw]


def _val_to_ramp(v: float, ramp: list[RGBA], x: int, y: int, dither_width: float = 0.22) -> RGBA | None:
    """Band-edge dithered lookup from intensity v in [0, 1] into palette ramp (None if <= 0)."""
    if v <= 0.0:
        return None
    v = min(0.9999, v)
    k = len(ramp)
    if k == 1:
        return ramp[0]
    pos = v * (k - 1)
    idx = min(int(pos), k - 2)
    frac = pos - idx
    half = dither_width * 0.5
    if frac < 0.5 - half:
        return ramp[idx]
    if frac > 0.5 + half:
        return ramp[idx + 1]
    t = (frac - (0.5 - half)) / max(1e-6, dither_width)
    thr = (BAYER4[y % 4][x % 4] + 0.5) / 16.0
    return ramp[idx + 1] if t > thr else ramp[idx]


def _loop_noise(x: float, y: float, phase: float, seed: int) -> float:
    """Fast smooth deterministic looping 2D noise over phase in [0, 1)."""
    tau = 2.0 * math.pi
    a = phase * tau
    s1 = math.sin(x * 1.7 + math.cos(a) * 1.3 + seed * 0.7) * math.cos(y * 1.9 + math.sin(a) * 1.3)
    s2 = math.sin((x + y) * 2.3 - a + seed * 1.3) * 0.5
    s3 = math.cos((x * 1.3 - y * 2.1) + a * 2.0 + seed * 2.1) * 0.25
    return (s1 + s2 + s3) / 1.75


def generate_vfx(
    vfx_type: str = "explosion",
    width: int = 32,
    height: int = 32,
    frames: int = 12,
    fps: int = 16,
    palette: str | Sequence[str] | None = None,
    seed: int = 42,
) -> SpriteDocument:
    """Generate a deterministic, crisp, palette-clean pixel art VFX animation."""
    vtype = vfx_type.lower().strip()
    if vtype not in VFX_TYPES:
        raise ValueError(f"Unknown VFX type {vfx_type!r}. Valid: {VFX_TYPES}")
    frames = max(1, int(frames))
    ramp = _resolve_ramp(vtype, palette)

    doc = SpriteDocument(width, height, palette=palette, snap=(palette is not None), default_fps=fps)
    cx, cy = (width - 1) * 0.5, (height - 1) * 0.5
    rad_max = min(width, height) * 0.45
    rng = random.Random(seed)

    # Pre-seed deterministic particles for burst/spark/splash effects
    sparks = [
        (rng.uniform(0, 2 * math.pi), rng.uniform(0.45, 1.05), rng.uniform(0.0, 0.25), rng.uniform(0.5, 1.0))
        for _ in range(18)
    ]

    for fi in range(frames):
        if fi > 0:
            doc.add_frame(copy=False)
        t = fi / max(1, frames - 1) if frames > 1 else 0.5
        phase = fi / frames
        im = doc._img()
        px = im.load()

        if vtype == "explosion":
            # Flash (0..0.15) -> Fireball expand (0.15..0.55) -> Smoke billow & dissipate (0.55..1.0)
            for y in range(height):
                for x in range(width):
                    dx, dy = (x - cx) / max(1.0, rad_max), (y - cy) / max(1.0, rad_max)
                    dist = math.hypot(dx, dy)
                    n = _loop_noise(dx * 2.5, dy * 2.5, t * 0.6, seed)
                    if t < 0.16:
                        r_cur = 0.28 + t * 2.5
                        val = (1.0 - dist / r_cur) * 1.35 + 0.15 * n
                    elif t < 0.65:
                        k = (t - 0.16) / 0.49
                        r_cur = 0.68 + k * 0.42
                        ring = abs(dist - k * 0.55)
                        val = (1.0 - dist / r_cur) * (1.1 - k * 0.45) + 0.30 * n - 0.15 * k * (1.0 - min(1.0, ring * 2.0))
                    else:
                        k = (t - 0.65) / 0.35
                        r_cur = 1.05
                        # Rising puffs fading out cleanly to empty on last frame
                        val = (1.0 - dist / r_cur) * (1.0 - k) * 0.72 + 0.35 * n * (1.0 - k) - k * 0.35
                    if val > 0.12:
                        c = _val_to_ramp(val, ramp, x, y)
                        if c:
                            px[x, y] = c
            # Flying sparks
            if 0.1 < t < 0.85:
                for ang, spd, delay, life in sparks[:10]:
                    lt = (t - delay) / max(0.2, life)
                    if 0.0 < lt < 0.85:
                        sx = round(cx + math.cos(ang) * rad_max * spd * lt * 1.15)
                        sy = round(cy + math.sin(ang) * rad_max * spd * lt * 1.15 + lt * lt * rad_max * 0.3)
                        if 0 <= sx < width and 0 <= sy < height:
                            px[sx, sy] = ramp[-1] if lt < 0.3 else ramp[-2]

        elif vtype == "fire":
            # Seamless looping rising flame with torn tongues!
            for y in range(height):
                ny = 1.0 - (y / max(1, height - 1))  # 0 at bottom, 1 at top
                sway = math.sin(2.0 * math.pi * phase - ny * 4.5) * 0.18 * (ny ** 1.4)
                half_w = max(0.05, (1.0 - ny ** 1.15) * 0.44 + 0.12 * math.sin(ny * math.pi))
                for x in range(width):
                    nx = ((x - cx) / max(1.0, width * 0.5)) - sway
                    n = _loop_noise(nx * 2.6, ny * 3.2 - phase * 2.0 * math.pi / 2.0, phase, seed)
                    shape = 1.0 - (abs(nx) / half_w) ** 1.6
                    val = shape * (1.05 - ny * 0.65) + n * (0.28 + 0.35 * ny)
                    if ny < 0.08:
                        val *= ny / 0.08
                    if val > 0.18:
                        c = _val_to_ramp(min(1.0, (val - 0.15) * 1.15), ramp, x, y)
                        if c:
                            px[x, y] = c

        elif vtype == "smoke":
            # Billowing translucent-look rising puffs (quantized with dithered fade!)
            for y in range(height):
                ny = 1.0 - (y / max(1, height - 1))
                sway = math.sin(2.0 * math.pi * phase - ny * 3.0) * 0.22 * ny
                half_w = 0.18 + ny * 0.55
                for x in range(width):
                    nx = ((x - cx) / max(1.0, width * 0.5)) - sway
                    n = _loop_noise(nx * 2.2, ny * 2.6, phase, seed)
                    dist = abs(nx) / half_w
                    val = (1.0 - dist * dist) * math.sin(ny * math.pi) + 0.35 * n
                    if val > 0.24:
                        # Shade top-left brighter than bottom-right
                        light_bias = (-nx * 0.2 + ny * 0.25)
                        c = _val_to_ramp(max(0.05, min(0.95, val * 0.7 + light_bias)), ramp, x, y)
                        if c:
                            px[x, y] = c

        elif vtype == "slash":
            # Sweeping crescent melee arc with fast bright tip and trailing dissolve
            sweep_start = -math.pi * 0.72 + t * math.pi * 0.85
            sweep_end = sweep_start + math.pi * (0.68 * (1.0 - t * 0.45))
            for y in range(height):
                for x in range(width):
                    dx, dy = (x - cx) / max(1.0, rad_max), (y - cy) / max(1.0, rad_max)
                    r = math.hypot(dx, dy)
                    ang = math.atan2(dy, dx)
                    # Normalize angle diff into sweep window
                    rel = (ang - sweep_start) % (2 * math.pi)
                    span = max(0.05, sweep_end - sweep_start)
                    if 0.0 <= rel <= span:
                        u = rel / span  # 0 = trailing tail, 1 = leading blade edge
                        thick = 0.12 + 0.26 * math.sin(u * math.pi) * (1.0 - t * 0.3)
                        band = 1.0 - abs(r - 0.78) / max(0.04, thick)
                        val = band * (0.35 + 0.75 * u) * (1.0 - max(0.0, (t - 0.7) / 0.3))
                        if val > 0.15:
                            c = _val_to_ramp(val, ramp, x, y, dither_width=0.15)
                            if c:
                                px[x, y] = c

        elif vtype == "sparkle":
            # Crisp 4-point star glint + orbiting micro-stars (seamless loop!)
            pulse = math.sin(phase * math.pi)
            arm = max(2.0, rad_max * (0.25 + 0.75 * pulse))
            for y in range(height):
                for x in range(width):
                    dx, dy = abs(x - cx), abs(y - cy)
                    star = max(
                        1.0 - (dx / arm + dy / max(1.0, arm * 0.28)),
                        1.0 - (dy / arm + dx / max(1.0, arm * 0.28)),
                    )
                    if star > 0.05:
                        c = _val_to_ramp(star * 1.15, ramp, x, y, dither_width=0.1)
                        if c:
                            px[x, y] = c
            # Secondary twinkling corner dots
            for i in range(4):
                a = i * math.pi * 0.5 + math.pi * 0.25
                sp = math.sin((phase + i * 0.25) * 2.0 * math.pi)
                if sp > 0.2:
                    sx = round(cx + math.cos(a) * rad_max * 0.65)
                    sy = round(cy + math.sin(a) * rad_max * 0.65)
                    if 0 <= sx < width and 0 <= sy < height:
                        px[sx, sy] = ramp[-1] if sp > 0.65 else ramp[-2]

        elif vtype == "magic_orb":
            # Pulsing arcane core + orbiting energy wisps (seamless!)
            pulse = 1.0 + 0.12 * math.sin(phase * 2.0 * math.pi)
            for y in range(height):
                for x in range(width):
                    dx, dy = (x - cx) / max(1.0, rad_max), (y - cy) / max(1.0, rad_max)
                    r = math.hypot(dx, dy)
                    ang = math.atan2(dy, dx)
                    swirl = 0.14 * math.sin(ang * 3.0 - phase * 2.0 * math.pi + r * 4.0)
                    val = (1.0 - r / (0.72 * pulse)) + swirl
                    if val > 0.08:
                        c = _val_to_ramp(min(1.0, val * 1.1), ramp, x, y)
                        if c:
                            px[x, y] = c
            for i in range(3):
                a = phase * 2.0 * math.pi + i * (2.0 * math.pi / 3.0)
                ox = round(cx + math.cos(a) * rad_max * 0.85)
                oy = round(cy + math.sin(a) * rad_max * 0.55)
                if 0 <= ox < width and 0 <= oy < height:
                    px[ox, oy] = ramp[-1]

        elif vtype == "lightning":
            # Jagged top-to-bottom electric bolt with branching forks + flash core!
            bolt_rng = random.Random(seed + fi * 97)
            bx = cx
            pts = [(round(bx), 0)]
            steps = max(4, height // 3)
            for s in range(1, steps + 1):
                ny = round((s / steps) * (height - 1))
                bx = max(2, min(width - 3, cx + bolt_rng.uniform(-rad_max * 0.55, rad_max * 0.55) * math.sin((s / steps) * math.pi)))
                pts.append((round(bx), ny))
            # Glow aura + white core
            for i in range(len(pts) - 1):
                x0, y0 = pts[i]
                x1, y1 = pts[i + 1]
                doc.line(x0 - 1, y0, x1 - 1, y1, ramp[2])
                doc.line(x0 + 1, y0, x1 + 1, y1, ramp[2])
                doc.line(x0, y0, x1, y1, ramp[-1])
                # Fork branch
                if i == len(pts) // 2:
                    fx = max(1, min(width - 2, x1 + bolt_rng.choice((-1, 1)) * max(3, width // 5)))
                    fy = min(height - 1, y1 + max(3, height // 5))
                    doc.line(x1, y1, fx, fy, ramp[3], pixel_perfect=True)

        elif vtype == "water_splash":
            # Parabolic fountain droplets arcing upward and splashing down!
            base_y = height - 2
            # Rippling splash ring on water surface
            ring_r = rad_max * (0.2 + 0.75 * t)
            for deg in range(0, 360, 10):
                a = math.radians(deg)
                rx = round(cx + math.cos(a) * ring_r)
                ry = round(base_y - 1 + math.sin(a) * ring_r * 0.22)
                if 0 <= rx < width and 0 <= ry < height and t < 0.9:
                    px[rx, ry] = ramp[3] if t < 0.4 else ramp[1]
            # Droplets
            for ang, spd, delay, life in sparks[:14]:
                # Upward fan angles
                up_ang = -math.pi * 0.5 + (ang - math.pi) * 0.35
                lt = max(0.0, t - delay * 0.5)
                if lt > 0.0 and lt < 0.95:
                    vx = math.cos(up_ang) * rad_max * 1.4 * spd
                    vy = math.sin(up_ang) * rad_max * 2.2 * spd
                    dx = round(cx + vx * lt)
                    dy = round(base_y + vy * lt + 0.5 * (rad_max * 4.5) * lt * lt)
                    if 0 <= dx < width and 0 <= dy < height:
                        px[dx, dy] = ramp[-1] if lt < 0.35 else ramp[2]
                        if dy + 1 < height and width >= 24:
                            px[dx, dy + 1] = ramp[1]

        elif vtype == "heal_aura":
            # Rising glowing green rings + tiny plus crosses (seamless!)
            for ring_i in range(2):
                rp = (phase + ring_i * 0.5) % 1.0
                ry_c = height - 2 - rp * (height - 4)
                rx_r = rad_max * (0.85 - 0.25 * rp)
                ry_r = max(1.5, rx_r * 0.25)
                col = ramp[-1] if rp < 0.25 else (ramp[3] if rp < 0.65 else ramp[1])
                for deg in range(0, 360, 10):
                    a = math.radians(deg)
                    rx = round(cx + math.cos(a) * rx_r)
                    ry = round(ry_c + math.sin(a) * ry_r)
                    if 0 <= rx < width and 0 <= ry < height:
                        px[rx, ry] = col
            # Tiny floating '+' heal particles
            for i in range(4):
                pp = (phase + i * 0.25) % 1.0
                hx = round(cx + math.sin(i * 2.1) * rad_max * 0.6)
                hy = round(height - 3 - pp * (height - 5))
                if 1 <= hx < width - 1 and 1 <= hy < height - 1:
                    c = ramp[-1] if pp < 0.5 else ramp[2]
                    px[hx, hy] = c
                    if width >= 16:
                        px[hx - 1, hy] = px[hx + 1, hy] = px[hx, hy - 1] = px[hx, hy + 1] = ramp[2]

        elif vtype == "hit_impact":
            # Punchy white flash star + shockwave ring + radial rays (1-2 hero flash frames!)
            if t < 0.25:
                doc.circle(round(cx), round(cy), max(2, round(rad_max * 0.55)), ramp[-1], fill=True)
            ring_r = rad_max * (0.25 + t * 0.85)
            fade = max(0.0, 1.0 - t)
            if fade > 0.08:
                for deg in range(0, 360, 12):
                    a = math.radians(deg)
                    rx = round(cx + math.cos(a) * ring_r)
                    ry = round(cy + math.sin(a) * ring_r)
                    if 0 <= rx < width and 0 <= ry < height:
                        px[rx, ry] = ramp[-1] if t < 0.35 else ramp[2]
                for i in range(8):
                    a = i * math.pi * 0.25 + 0.2
                    r0 = rad_max * (0.2 + t * 0.5)
                    r1 = rad_max * (0.65 + t * 0.45)
                    doc.line(
                        round(cx + math.cos(a) * r0), round(cy + math.sin(a) * r0),
                        round(cx + math.cos(a) * r1), round(cy + math.sin(a) * r1),
                        ramp[-2] if t < 0.45 else ramp[1],
                        pixel_perfect=True,
                    )

        elif vtype == "portal":
            # Spiraling dimensional vortex (seamless loop!)
            for y in range(height):
                for x in range(width):
                    dx = (x - cx) / max(1.0, rad_max * 0.72)
                    dy = (y - cy) / max(1.0, rad_max * 1.02)
                    r = math.hypot(dx, dy)
                    if r > 1.02:
                        continue
                    ang = math.atan2(dy, dx)
                    spiral = 0.5 + 0.5 * math.sin(ang * 3.0 + r * 6.5 - phase * 2.0 * math.pi)
                    rim = max(0.0, 1.0 - abs(r - 0.82) * 4.5)
                    val = max(rim * 0.95, (1.0 - r) * 0.65 + spiral * 0.45)
                    if val > 0.14:
                        c = _val_to_ramp(min(1.0, val), ramp, x, y)
                        if c:
                            px[x, y] = c

        elif vtype == "coin_spin":
            # Crisp rotating gold coin with specular glint (seamless!)
            cos_w = abs(math.cos(phase * math.pi))
            rx = max(1, round(rad_max * 0.75 * max(0.18, cos_w)))
            ry = max(2, round(rad_max * 0.82))
            doc.ellipse(round(cx - rx), round(cy - ry), round(cx + rx), round(cy + ry), ramp[1], fill=True)
            if rx >= 2:
                doc.ellipse(round(cx - rx + 1), round(cy - ry + 1), round(cx + rx - 1), round(cy + ry - 1), ramp[2], fill=True)
                doc.rect(round(cx), round(cy - ry // 2), round(cx), round(cy + ry // 2), ramp[3])
            # Specular shine sliding vertically
            sy = round(cy - ry * 0.5 + (phase * ry))
            if 0 <= sy < height:
                doc.px(round(cx - max(0, rx // 2)), sy, ramp[-1], only="opaque")
            doc.outline(ramp[0], where="outside")

    is_loop = vtype in ("fire", "smoke", "sparkle", "magic_orb", "heal_aura", "portal", "coin_spin")
    doc.tag(vtype, 1, frames, direction="forward")
    doc.metadata = {"vfx_type": vtype, "loop": is_loop, "seed": seed, "frames": frames, "fps": fps}
    return doc
