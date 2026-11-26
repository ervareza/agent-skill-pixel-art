"""Layered Multi-Directional Character Rig & Articulated Animation Engine.

Supports:
- Any pixel resolution: 8x8, 9x9, 12x12, 16x16, 24x24, 32x32, 48x48, 64x64, 128x128, or custom WxH
- True multi-layer character rig (paper-doll ready & exportable to native .aseprite):
    shadow, cape_back, hair_back, arm_far, leg_far, torso, leg_near,
    head, hair_front, headgear, arm_near, weapon, shield, vfx, outline
- True directional anatomy (shared landmark rows, zero turn-bobbing):
    1-dir (down), 2-dir (right, left), 4-dir (down, left, right, up),
    8-dir (s, se, e, ne, n, nw, w, sw)
- Arbitrary frame counts (1, 2, 3, 4, 5, 6, 8, 12, 16, 24, 60) & FPS (1..60)
- 8 biomechanical actions: idle, walk, run, jump, attack, cast, hurt, die
- 9 archetypes + customizable hair, outfit, headgear, cape, weapon, shield, palette
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence

from PIL import Image

from .canvas import SpriteDocument
from .color import ColorRamp, RGBA, hex_to_rgba, hue_ramp, load_palette, nearest_color

RIG_LAYERS = [
    "shadow",
    "cape_back",
    "hair_back",
    "arm_far",
    "leg_far",
    "torso",
    "leg_near",
    "head",
    "hair_front",
    "headgear",
    "arm_near",
    "weapon",
    "shield",
    "vfx",
    "outline",
]

DIR_SETS: dict[str, list[str]] = {
    "1": ["down"],
    "2": ["right", "left"],
    "4": ["down", "left", "right", "up"],
    "8": ["down", "se", "right", "ne", "up", "nw", "left", "sw"],
}

DIR_ALIASES = {
    "s": "down", "south": "down", "front": "down", "down": "down",
    "n": "up", "north": "up", "back": "up", "up": "up",
    "e": "right", "east": "right", "right": "right",
    "w": "left", "west": "left", "left": "left",
    "se": "se", "southeast": "se",
    "sw": "sw", "southwest": "sw",
    "ne": "ne", "northeast": "ne",
    "nw": "nw", "northwest": "nw",
}

ACTIONS = ("idle", "walk", "run", "jump", "attack", "cast", "hurt", "die")

ARCHETYPES = ("hero", "knight", "mage", "ranger", "rogue", "villager", "skeleton", "goblin", "slime")


@dataclass
class CharacterSpec:
    archetype: str = "hero"
    skin: str = "#F2B88B"
    hair: str = "#7A492C"
    tunic: str = "#3878B8"
    accent: str = "#E6B84C"
    pants: str = "#3D446B"
    boots: str = "#75482E"
    cape: str = "#C43B4B"
    metal: str = "#B6C4D4"
    magic: str = "#5CE8F5"
    eye: str = "#1F1827"
    outline: str = "#1E182B"
    has_cape: bool = True
    headgear: str = "none"       # none | helmet | wizard_hat | hood | crown | headband
    weapon: str = "sword"        # none | sword | staff | bow | dagger | axe
    shield: str = "none"         # none | kite | round
    hair_style: str = "short"    # short | long | spiky | bob | bald


def preset_spec(archetype: str) -> CharacterSpec:
    a = archetype.lower().strip()
    if a == "knight":
        return CharacterSpec(
            archetype="knight",
            skin="#F0B890", hair="#5A3928", tunic="#8C9DB5", accent="#E8BF4A",
            pants="#48536B", boots="#586378", cape="#C23642", metal="#D2DCE8",
            magic="#66E0FF", headgear="helmet", weapon="sword", shield="kite", has_cape=True,
        )
    if a == "mage":
        return CharacterSpec(
            archetype="mage",
            skin="#F5C4A0", hair="#D9D4E6", tunic="#5B4299", accent="#F2C85B",
            pants="#372963", boots="#4F342A", cape="#3C2B73", metal="#B8C4D4",
            magic="#5CF2FF", headgear="wizard_hat", weapon="staff", shield="none",
            has_cape=True, hair_style="long",
        )
    if a == "ranger":
        return CharacterSpec(
            archetype="ranger",
            skin="#EBB083", hair="#8C532B", tunic="#3D8A4E", accent="#D49B4B",
            pants="#4E3F33", boots="#633D26", cape="#2C663D", metal="#AAB6C2",
            magic="#9AF26B", headgear="hood", weapon="bow", shield="none",
            has_cape=True, hair_style="short",
        )
    if a == "rogue":
        return CharacterSpec(
            archetype="rogue",
            skin="#E8AE84", hair="#2C2738", tunic="#383B52", accent="#D94A5A",
            pants="#262838", boots="#3A2D2B", cape="#A83244", metal="#C4CFD9",
            magic="#C46BFF", headgear="headband", weapon="dagger", shield="none",
            has_cape=True, hair_style="spiky",
        )
    if a == "villager":
        return CharacterSpec(
            archetype="villager",
            skin="#F4BE95", hair="#A86538", tunic="#C96A42", accent="#E8C974",
            pants="#4A6B8C", boots="#6B442A", cape="#8A4B38", metal="#B0BAC4",
            has_cape=False, headgear="none", weapon="none", shield="none", hair_style="bob",
        )
    if a == "skeleton":
        return CharacterSpec(
            archetype="skeleton",
            skin="#E4E0D4", hair="#C7C1B2", tunic="#52566B", accent="#B54444",
            pants="#393C4D", boots="#4A4540", cape="#6E2D38", metal="#B8C4D4",
            eye="#1B1626", has_cape=True, headgear="none", weapon="sword", shield="round",
            hair_style="bald",
        )
    if a == "goblin":
        return CharacterSpec(
            archetype="goblin",
            skin="#6DB854", hair="#2F4D2A", tunic="#8A5636", accent="#D9A84E",
            pants="#4D382B", boots="#3D2B22", cape="#593525", metal="#B8C4CC",
            eye="#F24B4B", has_cape=False, headgear="none", weapon="dagger", shield="none",
            hair_style="spiky",
        )
    if a == "slime":
        return CharacterSpec(
            archetype="slime",
            skin="#42C272", hair="#9AF2A6", tunic="#2B945A", accent="#E6FFE8",
            pants="#1E6B4B", boots="#174D3C", cape="#2B945A", magic="#A8FFCC",
            eye="#181425", has_cape=False, headgear="none", weapon="none", shield="none",
        )
    # Default: hero adventurer (rich royal blue tunic + warm auburn hair + crimson cape)
    return CharacterSpec(
        archetype="hero",
        skin="#F3BC92", hair="#7A482B", tunic="#1E78C8", accent="#F4C844",
        pants="#36447A", boots="#7A462B", cape="#D43B47", metal="#D2DCE8",
        magic="#2CE8F5", headgear="none", weapon="sword", shield="none",
        has_cape=True, hair_style="short",
    )


@dataclass
class _Ramps:
    skin: ColorRamp
    hair: ColorRamp
    tunic: ColorRamp
    accent: ColorRamp
    pants: ColorRamp
    boots: ColorRamp
    cape: ColorRamp
    metal: ColorRamp
    magic: ColorRamp
    eye: RGBA
    outline: RGBA
    shadow_col: RGBA
    white: RGBA


def _build_ramps(spec: CharacterSpec, palette_rgba: Sequence[RGBA] | None) -> _Ramps:
    def _mk(name: str, base: str) -> ColorRamp:
        r = ColorRamp.from_base(name, base, steps=4, hue_shift=16.0)
        return r.snap_to(palette_rgba) if palette_rgba else r

    def _snap(c: str) -> RGBA:
        rgba = hex_to_rgba(c)
        return nearest_color(rgba, palette_rgba) if palette_rgba else rgba

    # Pick darkest palette tone for outline when palette is locked
    out_c = _snap(spec.outline)
    if palette_rgba:
        # Ensure outline is dark enough compared to midtones
        darkest = min(palette_rgba, key=lambda p: p[0] * 0.299 + p[1] * 0.587 + p[2] * 0.114)
        if (out_c[0] + out_c[1] + out_c[2]) > (darkest[0] + darkest[1] + darkest[2]) + 140:
            out_c = darkest

    return _Ramps(
        skin=_mk("skin", spec.skin),
        hair=_mk("hair", spec.hair),
        tunic=_mk("tunic", spec.tunic),
        accent=_mk("accent", spec.accent),
        pants=_mk("pants", spec.pants),
        boots=_mk("boots", spec.boots),
        cape=_mk("cape", spec.cape),
        metal=_mk("metal", spec.metal),
        magic=_mk("magic", spec.magic),
        eye=_snap(spec.eye),
        outline=out_c,
        shadow_col=_snap("#1A1726"),
        white=_snap("#FFF8EE"),
    )


@dataclass
class _Metrics:
    w: int
    h: int
    tier: str          # micro | small | standard | hibit
    cx: float
    ground_y: int
    body_h: int
    head_w: int
    head_h: int
    torso_w: int
    torso_h: int
    leg_h: int
    leg_w: int
    arm_w: int
    arm_h: int
    head_y0: int
    torso_y0: int
    hip_y: int
    use_outline: bool


def _compute_metrics(w: int, h: int, is_slime: bool = False, tall_headgear: bool = False) -> _Metrics:
    if h <= 11 or w <= 11:
        tier = "micro"
        margin_b = 0 if h <= 9 else 1
        margin_t = 0 if h <= 9 else 1
        use_outline = False
    elif h <= 20:
        tier = "small"
        margin_b = 1
        margin_t = 2 if tall_headgear else 1
        use_outline = True
    elif h <= 40:
        tier = "standard"
        margin_b = max(2, h // 14)
        margin_t = max(5, h // 6) if tall_headgear else max(2, h // 12)
        use_outline = True
    else:
        tier = "hibit"
        margin_b = max(3, h // 14)
        margin_t = max(8, h // 6) if tall_headgear else max(3, h // 12)
        use_outline = True

    ground_y = h - 1 - margin_b
    avail_h = max(6, ground_y - margin_t + 1)

    if tier == "micro":
        head_h = max(3, round(avail_h * 0.44))
        torso_h = max(2, round(avail_h * 0.30))
        leg_h = max(2, avail_h - head_h - torso_h)
        head_w = max(4, min(w - 2, round(head_h * 1.25)))
        torso_w = max(3, min(w - 2, head_w - 1))
        leg_w = max(1, torso_w // 3)
        arm_w = 1
        arm_h = max(2, torso_h)
    elif tier == "small":
        head_h = max(5, round(avail_h * 0.43))
        torso_h = max(4, round(avail_h * 0.30))
        leg_h = max(3, avail_h - head_h - torso_h)
        head_w = max(6, min(w - 4, round(head_h * 1.18)))
        torso_w = max(5, min(w - 4, round(head_w * 0.92)))
        leg_w = max(2, round(torso_w * 0.34))
        arm_w = max(1, round(torso_w * 0.24))
        arm_h = max(3, torso_h)
    elif tier == "standard":
        head_h = max(7, round(avail_h * 0.35))
        torso_h = max(7, round(avail_h * 0.32))
        leg_h = max(6, avail_h - head_h - torso_h)
        head_w = max(8, min(w - 6, round(head_h * 1.10)))
        torso_w = max(7, min(w - 6, round(head_w * 0.96)))
        leg_w = max(2, round(torso_w * 0.34))
        arm_w = max(2, round(torso_w * 0.26))
        arm_h = max(5, round(torso_h * 1.02))
    else:
        head_h = max(11, round(avail_h * 0.31))
        torso_h = max(12, round(avail_h * 0.34))
        leg_h = max(12, avail_h - head_h - torso_h)
        head_w = max(12, min(w - 10, round(head_h * 1.06)))
        torso_w = max(11, min(w - 10, round(head_w * 1.04)))
        leg_w = max(3, round(torso_w * 0.33))
        arm_w = max(3, round(torso_w * 0.25))
        arm_h = max(8, round(torso_h * 1.02))

    # Match odd/even parity between head and torso for crisp centering
    if (head_w % 2) != (w % 2) and head_w + 1 <= w - (2 if use_outline else 0):
        head_w += 1
    if (torso_w % 2) != (head_w % 2) and torso_w + 1 <= w - (2 if use_outline else 0):
        torso_w += 1

    body_h = head_h + torso_h + leg_h
    head_y0 = ground_y - body_h + 1
    torso_y0 = head_y0 + head_h
    hip_y = torso_y0 + torso_h

    return _Metrics(
        w=w, h=h, tier=tier, cx=(w - 1) * 0.5, ground_y=ground_y,
        body_h=body_h, head_w=head_w, head_h=head_h,
        torso_w=torso_w, torso_h=torso_h, leg_h=leg_h, leg_w=leg_w,
        arm_w=arm_w, arm_h=arm_h, head_y0=head_y0, torso_y0=torso_y0,
        hip_y=hip_y, use_outline=use_outline,
    )


@dataclass
class _Pose:
    """Normalized kinematic pose derived from action + continuous phase p in [0, 1)."""
    body_dy: float = 0.0
    head_dy: float = 0.0
    body_dx: float = 0.0
    lean_x: float = 0.0
    stride_l: float = 0.0        # -1 (back) .. +1 (forward)
    stride_r: float = 0.0
    lift_l: float = 0.0          # 0 (ground) .. 1 (tucked high)
    lift_r: float = 0.0
    arm_l: float = 0.0           # -1 (back) .. +1 (forward/up)
    arm_r: float = 0.0
    cape_wave: float = 0.0
    weapon_angle: float = 0.0    # -1 (windup back) .. 0 (rest) .. +1 (slash forward)
    slash_alpha: float = 0.0     # > 0 draws melee slash arc VFX
    cast_glow: float = 0.0       # > 0 draws spell cast VFX
    blink: bool = False
    flash: bool = False
    collapse: float = 0.0        # 0 (standing) .. 1 (fallen flat on ground)
    squash_x: float = 1.0
    squash_y: float = 1.0
    shadow_scale: float = 1.0
    airborne_dy: float = 0.0     # negative = lifted off ground


def _compute_pose(action: str, frame_idx: int, num_frames: int) -> tuple[_Pose, float]:
    """Compute biomechanical pose and relative duration multiplier for arbitrary frame count."""
    p = (frame_idx / num_frames) if num_frames > 0 else 0.0
    # Special clean RPG Maker 3-frame mapping for walk/run so frame 1 is neutral stand!
    if num_frames == 3 and action in ("walk", "run"):
        p = (0.0, 0.25, 0.5)[frame_idx]

    tau = 2.0 * math.pi
    pose = _Pose()
    dur_mult = 1.0

    if action == "idle":
        # Gentle breathing sine + blink on ~75% phase
        breath = math.sin(tau * p)
        pose.body_dy = 0.5 * max(0.0, breath)
        pose.head_dy = 0.5 * max(0.0, math.sin(tau * (p - 0.1)))
        pose.cape_wave = 0.35 * math.sin(tau * p)
        pose.arm_l = 0.08 * breath
        pose.arm_r = -0.08 * breath
        pose.blink = (num_frames >= 4 and frame_idx == int(num_frames * 0.75))
        dur_mult = 1.25 if abs(breath) > 0.7 else 0.9

    elif action == "walk":
        # Contact (0.0) -> Down (0.125) -> Pass (0.25) -> Up (0.375) -> Contact2 (0.5) ...
        pose.stride_l = math.cos(tau * p)
        pose.stride_r = -pose.stride_l
        pose.lift_l = max(0.0, -math.sin(tau * p))
        pose.lift_r = max(0.0, math.sin(tau * p))
        # Arms oppose legs cleanly
        pose.arm_l = -pose.stride_l * 0.85
        pose.arm_r = -pose.stride_r * 0.85
        # Triangle-like hip bob: lowest at down (0.125, 0.625), highest at pass (0.25, 0.75)
        bob_phase = (p * 2.0) % 1.0
        # 0.0 contact -> 0, 0.25 down -> +1 (down on screen), 0.5 pass -> -1 (high), 0.75 up -> 0
        pose.body_dy = math.sin(tau * bob_phase)
        head_bob_phase = ((p - 0.08) * 2.0) % 1.0
        pose.head_dy = math.sin(tau * head_bob_phase)
        pose.cape_wave = math.sin(tau * (p - 0.15))
        pose.lean_x = 0.22
        # Hold contact slightly longer than pass (Williams timing rule)
        dur_mult = 1.15 if abs(pose.stride_l) > 0.7 else 0.92

    elif action == "run":
        pose.stride_l = math.cos(tau * p) * 1.35
        pose.stride_r = -pose.stride_l
        pose.lift_l = max(0.0, -math.sin(tau * p)) * 1.35
        pose.lift_r = max(0.0, math.sin(tau * p)) * 1.35
        pose.arm_l = -math.cos(tau * p) * 1.25
        pose.arm_r = math.cos(tau * p) * 1.25
        bob_phase = (p * 2.0) % 1.0
        # Flight phase near bob_phase ~ 0.65..0.85 lifts whole body off ground!
        flight = max(0.0, math.sin(tau * (bob_phase - 0.35)))
        pose.airborne_dy = -1.3 * flight
        pose.body_dy = 0.8 * math.sin(tau * bob_phase)
        pose.head_dy = 0.8 * math.sin(tau * ((bob_phase - 0.1) % 1.0))
        pose.lean_x = 0.75
        pose.cape_wave = 1.3 + 0.5 * math.sin(tau * (p - 0.18))
        pose.shadow_scale = 1.0 - 0.22 * flight
        dur_mult = 1.1 if flight > 0.5 else 0.9

    elif action == "jump":
        # 0.0..0.18 crouch -> 0.18..0.55 rise/apex -> 0.55..0.85 fall -> 0.85..1.0 land squash
        if p < 0.2:
            t = p / 0.2
            pose.body_dy = 1.4 * math.sin(t * math.pi * 0.5)
            pose.squash_x, pose.squash_y = 1.12, 0.88
            pose.arm_l = pose.arm_r = -0.6
            dur_mult = 1.0
        elif p < 0.82:
            t = (p - 0.2) / 0.62
            arc = math.sin(t * math.pi)
            pose.airborne_dy = -3.8 * arc
            pose.lift_l = 0.8 * arc
            pose.lift_r = 0.5 * arc
            pose.arm_l = pose.arm_r = 0.9 * arc
            pose.shadow_scale = max(0.45, 1.0 - 0.5 * arc)
            pose.cape_wave = 1.2 * arc
            pose.squash_x, pose.squash_y = (0.92, 1.08) if arc < 0.75 else (1.0, 1.0)
            dur_mult = 1.4 if 0.35 < t < 0.65 else 0.85
        else:
            t = (p - 0.82) / 0.18
            pose.body_dy = 1.5 * (1.0 - t)
            pose.squash_x, pose.squash_y = 1.14, 0.86
            pose.arm_l = pose.arm_r = -0.4
            dur_mult = 1.1

    elif action == "attack":
        # Wind-up (0..0.32) -> Fast Strike (0.32..0.58) -> Impact Hold (0.58..0.75) -> Recover (0.75..1.0)
        if p < 0.32:
            t = p / 0.32
            pose.weapon_angle = -1.0 * t
            pose.body_dx = -0.7 * t
            pose.body_dy = 0.5 * t
            pose.arm_r = -1.0 * t
            pose.arm_l = 0.4 * t
            pose.stride_l = -0.4 * t
            pose.stride_r = 0.4 * t
            dur_mult = 1.3
        elif p < 0.62:
            t = (p - 0.32) / 0.30
            pose.weapon_angle = -1.0 + 2.2 * t
            pose.body_dx = -0.7 + 2.1 * t
            pose.lean_x = 0.75 * t
            pose.arm_r = 1.25
            pose.arm_l = -0.6
            pose.stride_l = 0.85
            pose.stride_r = -0.75
            pose.slash_alpha = math.sin(t * math.pi)
            pose.cape_wave = 1.2 * t
            dur_mult = 0.65
        elif p < 0.78:
            pose.weapon_angle = 1.15
            pose.body_dx = 1.2
            pose.lean_x = 0.6
            pose.arm_r = 1.1
            pose.stride_l = 0.8
            pose.stride_r = -0.7
            pose.slash_alpha = 0.4
            dur_mult = 1.2
        else:
            t = (p - 0.78) / 0.22
            pose.weapon_angle = 1.15 * (1.0 - t)
            pose.body_dx = 1.2 * (1.0 - t)
            pose.lean_x = 0.6 * (1.0 - t)
            pose.arm_r = 1.1 * (1.0 - t)
            pose.stride_l = 0.8 * (1.0 - t)
            pose.stride_r = -0.7 * (1.0 - t)
            dur_mult = 1.0

    elif action == "cast":
        charge = math.sin(p * math.pi)
        pose.arm_l = 1.15 * charge
        pose.arm_r = 1.15 * charge
        pose.weapon_angle = -0.6 * charge
        pose.body_dy = -0.5 * charge
        pose.cape_wave = 1.4 * math.sin(tau * p * 2.0) * charge
        pose.cast_glow = charge
        dur_mult = 1.2 if charge > 0.8 else 0.9

    elif action == "hurt":
        recoil = math.sin(p * math.pi)
        pose.body_dx = -1.5 * recoil
        pose.body_dy = 0.7 * recoil
        pose.lean_x = -0.8 * recoil
        pose.arm_l = -0.9 * recoil
        pose.arm_r = 0.9 * recoil
        pose.flash = (p < 0.45)
        dur_mult = 0.8 if pose.flash else 1.1

    elif action == "die":
        t = min(1.0, p / 0.85) if num_frames > 1 else 1.0
        pose.collapse = t
        pose.body_dx = -1.8 * t
        pose.flash = (frame_idx == 0 and num_frames >= 3)
        pose.shadow_scale = 1.0 + 0.35 * t
        dur_mult = 1.4 if t >= 0.95 else 1.0

    return pose, dur_mult


def _facing_info(direction: str) -> tuple[str, int]:
    """Return (canonical_view, x_sign) where canonical_view in {down, up, side, diag_front, diag_back}."""
    d = DIR_ALIASES.get(direction.lower().strip(), "down")
    if d == "down":
        return "down", 1
    if d == "up":
        return "up", 1
    if d == "right":
        return "side", 1
    if d == "left":
        return "side", -1
    if d == "se":
        return "diag_front", 1
    if d == "sw":
        return "diag_front", -1
    if d == "ne":
        return "diag_back", 1
    if d == "nw":
        return "diag_back", -1
    return "down", 1


def _shade_rect(
    doc: SpriteDocument,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    ramp: ColorRamp,
    lit_left: bool = True,
    rounded: bool = False,
    radius: int = 1,
) -> None:
    """Draw a cleanly 3-tone hue-shifted shaded block (top-left consistent light)."""
    if x1 < x0 or y1 < y0:
        return
    if rounded and (x1 - x0) >= 3 and (y1 - y0) >= 3:
        doc.rounded_rect(x0, y0, x1, y1, ramp.mid, radius=radius, fill=True)
    else:
        doc.rect(x0, y0, x1, y1, ramp.mid, fill=True)
    # Shadow on bottom & right side (fixed global top-left light!)
    if y1 - y0 >= 2:
        doc.rect(x0, y1, x1, y1, ramp.shadow, fill=True, only="opaque")
    if x1 - x0 >= 2:
        sx = x1 if lit_left else x0
        doc.rect(sx, y0, sx, y1, ramp.shadow, fill=True, only="opaque")
    # Highlight on top & lit side
    if y1 - y0 >= 2:
        doc.rect(x0, y0, x1 - (1 if x1 - x0 >= 2 else 0), y0, ramp.light, fill=True, only="opaque")
    if x1 - x0 >= 3 and y1 - y0 >= 3:
        hx = x0 if lit_left else x1
        doc.rect(hx, y0, hx, max(y0, y1 - 1), ramp.light, fill=True, only="opaque")


def _draw_slime_frame(
    doc: SpriteDocument,
    m: _Metrics,
    ramps: _Ramps,
    spec: CharacterSpec,
    direction: str,
    pose: _Pose,
) -> None:
    """Render an expressive layered gelatinous slime in all 8 directions & 8 actions."""
    view, xsign = _facing_info(direction)
    bob_scale = max(1.0, m.h / 16.0)
    cx = m.cx + pose.body_dx * bob_scale * xsign * 0.7
    cy_base = m.ground_y + pose.airborne_dy * bob_scale

    # Dynamic hop/wobble squash-and-stretch
    hop = max(0.0, pose.lift_l, pose.lift_r)
    sx = pose.squash_x * (1.0 - 0.12 * hop) * (1.0 + 0.35 * pose.collapse)
    sy = pose.squash_y * (1.0 + 0.14 * hop) * (1.0 - 0.65 * pose.collapse)
    hop_lift = -round(hop * max(1.0, m.h * 0.12))

    bw = max(5, round(m.w * 0.66 * sx))
    bh = max(3, round(m.h * 0.50 * sy))
    x0 = round(cx - bw * 0.5)
    x1 = x0 + bw - 1
    y1 = round(cy_base + hop_lift)
    y0 = y1 - bh + 1

    # Layer 1: Shadow
    doc.layer("shadow")
    sh_rx = max(2, round(bw * 0.48 * pose.shadow_scale))
    sh_ry = max(1, round(m.h * 0.07))
    doc.ellipse(round(cx - sh_rx), m.ground_y - sh_ry + 1, round(cx + sh_rx), m.ground_y + 1, ramps.shadow_col, fill=True)

    # Layer 2: Body (torso)
    doc.layer("torso")
    body_mid = ramps.white if pose.flash else ramps.skin.mid
    body_sh = ramps.skin.light if pose.flash else ramps.skin.shadow
    body_hi = ramps.white if pose.flash else ramps.skin.highlight
    doc.ellipse(x0, y0, x1, y1, body_sh, fill=True)
    # Shifted lighter interior toward top-left light
    doc.ellipse(x0, y0, max(x0, x1 - 1), max(y0, y1 - max(1, bh // 5)), body_mid, fill=True, only="opaque")
    # Glossy top-left highlight cluster
    hl_w = max(1, bw // 5)
    hl_h = max(1, bh // 5)
    doc.ellipse(x0 + max(1, bw // 5), y0 + max(1, bh // 5), x0 + max(1, bw // 5) + hl_w, y0 + max(1, bh // 5) + hl_h, body_hi, fill=True, only="opaque")

    # Layer 3: Eyes (head) — directional! Up/Back shows NO eyes!
    doc.layer("head")
    if view != "up" and pose.collapse < 0.7 and not pose.blink:
        eye_y = y0 + max(1, round(bh * 0.45))
        eye_h = max(1, bh // 6)
        eye_w = max(1, bw // 10)
        if view == "down":
            gap = max(1, bw // 5)
            for ex in (round(cx - gap), round(cx + gap - eye_w + 1)):
                doc.rect(ex, eye_y, ex + eye_w - 1, eye_y + eye_h - 1, ramps.eye)
                if m.h >= 24:
                    doc.px(ex, eye_y, ramps.white)
        elif view == "diag_front":
            shift = xsign * max(1, bw // 6)
            gap = max(1, bw // 6)
            for ex in (round(cx + shift - gap), round(cx + shift + gap - eye_w + 1)):
                doc.rect(ex, eye_y, ex + eye_w - 1, eye_y + eye_h - 1, ramps.eye)
                if m.h >= 24:
                    doc.px(ex, eye_y, ramps.white)
        elif view == "side":
            ex = round(cx + xsign * (bw * 0.26))
            doc.rect(ex, eye_y, ex + eye_w - 1, eye_y + eye_h - 1, ramps.eye)
            if m.h >= 24:
                doc.px(ex, eye_y, ramps.white)

    # Layer 4: VFX
    if pose.slash_alpha > 0.1 or pose.cast_glow > 0.1:
        doc.layer("vfx")
        fx_x = round(cx + xsign * (bw * 0.55))
        fx_y = (y0 + y1) // 2
        doc.circle(fx_x, fx_y, max(1, m.w // 8), ramps.magic.light, fill=False)
        doc.px(fx_x, fx_y, ramps.white)

    # Final unified selective outline (excluding shadow & vfx)
    if m.use_outline:
        _apply_unified_outline(doc, ramps)


def _apply_unified_outline(doc: SpriteDocument, ramps: _Ramps) -> None:
    """Compute a clean 1px selective outline around all body/equipment layers onto the `outline` layer."""
    body_layers = [l.name for l in doc.layers if l.name not in ("shadow", "vfx", "outline")]
    merged = doc.composite(doc.current_frame, layers=body_layers)
    spx = merged.load()
    doc.layer("outline")
    out_im = doc._img()
    opx = out_im.load()
    w, h = doc.width, doc.height
    dark = ramps.outline

    for y in range(h):
        for x in range(w):
            if spx[x, y][3] > 0:
                continue
            neighbors = []
            lit_dot = 0
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and spx[nx, ny][3] > 0:
                    neighbors.append(spx[nx, ny])
                    # Fixed top-left light (-1, -1): outward normal (-dx, -dy)
                    lit_dot += (-dx * -1) + (-dy * -1)
            if not neighbors:
                continue
            # Selective outline: blend slightly toward neighbor color on lit side, darker ink on shadow side
            ar = sum(p[0] for p in neighbors) // len(neighbors)
            ag = sum(p[1] for p in neighbors) // len(neighbors)
            ab = sum(p[2] for p in neighbors) // len(neighbors)
            t = 0.24 if lit_dot > 0 else 0.08
            r = round(dark[0] + (ar - dark[0]) * t)
            g = round(dark[1] + (ag - dark[1]) * t)
            b = round(dark[2] + (ab - dark[2]) * t)
            c = (r, g, b, 255)
            if doc.palette and doc.snap:
                p = nearest_color(c, doc.palette)
                c = (p[0], p[1], p[2], 255)
            opx[x, y] = c


def _draw_humanoid_frame(
    doc: SpriteDocument,
    m: _Metrics,
    ramps: _Ramps,
    spec: CharacterSpec,
    direction: str,
    pose: _Pose,
) -> None:
    """Render one frame of a multi-layer rigged humanoid character in any direction/size/action."""
    view, xsign = _facing_info(direction)
    scale = max(0.5, m.h / 32.0)

    # Collapse transform for `die` action
    if pose.collapse > 0.65:
        _draw_fallen_humanoid(doc, m, ramps, spec, view, xsign, pose)
        if m.use_outline:
            _apply_unified_outline(doc, ramps)
        return

    # Dynamic vertical bob (integer-snapped cleanly per size tier)
    bob_amp = 0.45 if m.tier == "micro" else (0.9 if m.tier == "small" else (1.5 if m.tier == "standard" else max(2.0, m.h * 0.045)))
    body_dy = round(pose.body_dy * bob_amp + pose.airborne_dy * max(1.0, m.h * 0.065) + pose.collapse * m.leg_h * 0.55)
    head_dy = round(pose.head_dy * bob_amp + pose.airborne_dy * max(1.0, m.h * 0.065) + pose.collapse * m.leg_h * 0.65)
    body_dx = round(pose.body_dx * max(1.0, m.w * 0.08) * xsign)
    lean_px = round(pose.lean_x * max(0.6, m.w * 0.06) * xsign) if view in ("side", "diag_front", "diag_back") else 0

    cx = m.cx + body_dx
    torso_y0 = m.torso_y0 + body_dy
    torso_y1 = torso_y0 + m.torso_h - 1
    head_y0 = m.head_y0 + head_dy
    head_y1 = head_y0 + m.head_h - 1
    hip_y = torso_y1

    # Width by view (Rule 5 from views-and-directions: side narrower, 3/4 intermediate, front/back full!)
    if view == "side":
        tw = max(3, round(m.torso_w * 0.72))
        hw = max(4, round(m.head_w * 0.88))
    elif view in ("diag_front", "diag_back"):
        tw = max(3, round(m.torso_w * 0.88))
        hw = max(4, round(m.head_w * 0.95))
    else:
        tw = m.torso_w
        hw = m.head_w

    # Apply subtle squash & stretch on torso during jump/land
    tw = max(3, round(tw * pose.squash_x))

    # Helper to tint ramp white on hurt flash
    tunic_r = ColorRamp("flash", (ramps.tunic.light, ramps.white, ramps.white, ramps.white)) if pose.flash else ramps.tunic
    skin_r = ColorRamp("flash", (ramps.skin.light, ramps.white, ramps.white, ramps.white)) if pose.flash else ramps.skin
    pants_r = ColorRamp("flash", (ramps.pants.light, ramps.white, ramps.white, ramps.white)) if pose.flash else ramps.pants
    boots_r = ColorRamp("flash", (ramps.boots.light, ramps.white, ramps.white, ramps.white)) if pose.flash else ramps.boots

    # ---- 1. SHADOW LAYER (always anchored on ground_y!) ----
    doc.layer("shadow")
    if m.h >= 12:
        sh_rx = max(2, round(tw * 0.56 * pose.shadow_scale))
        sh_ry = max(1, round(m.h * 0.045))
        doc.ellipse(round(cx - sh_rx), m.ground_y - sh_ry + 1, round(cx + sh_rx), m.ground_y + 1, ramps.shadow_col, fill=True)

    # ---- 2. CAPE BACK / HAIR BACK ----
    if spec.has_cape and m.h >= 12:
        doc.layer("cape_back")
        wave = round(pose.cape_wave * max(1.0, m.w * 0.06))
        cape_top = torso_y0 + max(0, m.torso_h // 6)
        cape_bot = min(m.ground_y - 1, hip_y + max(2, round(m.leg_h * 0.65)))
        if view == "up":
            # Prominent flowing cape across entire back!
            cw_top = max(3, tw)
            cw_bot = max(4, tw + max(2, m.w // 12))
            for y in range(cape_top, cape_bot + 1):
                t = (y - cape_top) / max(1, cape_bot - cape_top)
                half_w = (cw_top + (cw_bot - cw_top) * t) * 0.5
                sway = round(wave * t * t)
                lx0 = round(cx - half_w + sway)
                lx1 = round(cx + half_w + sway)
                col = ramps.cape.light if t < 0.25 else (ramps.cape.mid if t < 0.78 else ramps.cape.shadow)
                doc.rect(lx0, y, lx1, y, col)
                if lx1 - lx0 >= 3:
                    doc.px(lx1, y, ramps.cape.shadow)
        elif view == "down":
            # Subtle cape peeking behind shoulders & hem
            cw = tw + 2
            for y in range(cape_top + 1, cape_bot + 1):
                t = (y - cape_top) / max(1, cape_bot - cape_top)
                sway = round(wave * 0.5 * t)
                lx0 = round(cx - cw * 0.5 + sway)
                lx1 = round(cx + cw * 0.5 + sway)
                doc.rect(lx0, y, lx1, y, ramps.cape.shadow if t > 0.6 else ramps.cape.mid)
        elif view in ("side", "diag_front", "diag_back"):
            # Cape billows BEHIND the character (-xsign side!)
            back_dir = -xsign
            base_x = cx + back_dir * (tw * 0.35)
            for y in range(cape_top, cape_bot + 1):
                t = (y - cape_top) / max(1, cape_bot - cape_top)
                flare = (1.5 + abs(pose.cape_wave) * 1.4 + t * max(2.0, m.w * 0.14)) * back_dir
                x_a = round(base_x + back_dir * t * 1.0)
                x_b = round(base_x + flare + back_dir * (wave * 0.4 * t))
                col = ramps.cape.light if (t < 0.3 and view == "diag_back") else (ramps.cape.mid if t < 0.72 else ramps.cape.shadow)
                doc.rect(min(x_a, x_b), y, max(x_a, x_b), y, col)

    # Long hair back layer
    if spec.hair_style == "long" and view != "up" and m.h >= 16:
        doc.layer("hair_back")
        hw_b = max(3, hw + (1 if view == "down" else 0))
        hb_y0 = head_y0 + m.head_h // 2
        hb_y1 = min(torso_y1, hb_y0 + max(2, m.torso_h // 2))
        shift_b = -xsign * max(1, hw // 5) if view in ("side", "diag_front") else 0
        doc.rect(round(cx - hw_b * 0.45 + shift_b), hb_y0, round(cx + hw_b * 0.45 + shift_b), hb_y1, ramps.hair.shadow)

    # ---- 3. LEGS (leg_far & leg_near — true biomechanical stride!) ----
    stride_px = max(1.0, m.w * (0.14 if m.tier == "micro" else 0.16))
    lift_px = max(1.0, m.leg_h * (0.28 if m.tier == "micro" else 0.32))
    boot_h = max(1, round(m.leg_h * 0.32))

    def _draw_leg(layer_name: str, leg_cx: float, stride: float, lift: float, is_far: bool) -> None:
        doc.layer(layer_name)
        p_col = pants_r.shadow if is_far else pants_r.mid
        p_hi = pants_r.mid if is_far else pants_r.light
        b_col = boots_r.shadow if is_far else boots_r.mid
        b_hi = boots_r.mid if is_far else boots_r.light

        foot_y = min(m.ground_y, round(m.ground_y + pose.airborne_dy * max(1.0, m.h * 0.065) - lift * lift_px))
        if view in ("down", "up"):
            # Top-down / front-back step: trailing leg lifts & shortens slightly, leading leg stays planted!
            step_lift = round(max(0.0, lift) * max(1.0, m.leg_h * 0.28))
            fy = min(m.ground_y, round(m.ground_y + pose.airborne_dy * max(1.0, m.h * 0.065) - step_lift))
            lx0 = round(leg_cx - m.leg_w * 0.5)
            lx1 = lx0 + m.leg_w - 1
            leg_top = max(torso_y1, hip_y)
            boot_top = max(leg_top, fy - boot_h + 1)
            if boot_top > leg_top:
                doc.rect(lx0, leg_top, lx1, boot_top - 1, p_col)
                if m.leg_w >= 2 and not is_far:
                    doc.rect(lx0, leg_top, lx0, boot_top - 1, p_hi)
            # Boot slightly wider on ground
            bx0, bx1 = lx0, lx1
            if m.h >= 24:
                bx0 = lx0 - (1 if leg_cx < cx else 0)
                bx1 = lx1 + (1 if leg_cx >= cx else 0)
            doc.rect(bx0, boot_top, bx1, fy, b_col)
            if not is_far and boot_h >= 2:
                doc.rect(bx0, boot_top, bx1, boot_top, b_hi)
        else:
            # Side & 3/4 diagonal: true articulated 2-segment stride!
            dir_factor = 1.0 if view == "side" else 0.78
            foot_x = leg_cx + stride * stride_px * xsign * dir_factor
            hip_pt_x = leg_cx
            hip_pt_y = float(hip_y)
            # Knee bends slightly forward during swing/lift
            knee_bend = (0.35 + 0.65 * lift) * max(1.0, m.leg_w * 0.7) * xsign
            knee_x = (hip_pt_x + foot_x) * 0.5 + knee_bend
            knee_y = (hip_pt_y + foot_y) * 0.5

            leg_rad = max(0.6, m.leg_w * 0.48)
            ankle_y = max(hip_pt_y + 1, foot_y - boot_h + 0.5)
            if m.tier == "micro":
                doc.line(round(hip_pt_x), round(hip_pt_y), round(foot_x), max(round(hip_pt_y), foot_y - 1), p_col)
                doc.px(round(foot_x), foot_y, b_col)
                if m.w >= 9:
                    doc.px(round(foot_x) + xsign, foot_y, b_col)
            else:
                doc.capsule(hip_pt_x, hip_pt_y, knee_x, knee_y, leg_rad, leg_rad * 0.9, p_col)
                doc.capsule(knee_x, knee_y, foot_x, ankle_y, leg_rad * 0.9, leg_rad * 0.8, p_col)
                if not is_far and m.leg_w >= 2:
                    doc.line(round(hip_pt_x), round(hip_pt_y), round(knee_x), round(knee_y), p_hi)
                # Boot with toe extending in facing direction!
                toe_ext = max(1, round(m.leg_w * 0.55)) * xsign
                bx_a = round(foot_x - leg_rad * 0.6 * xsign)
                bx_b = round(foot_x + toe_ext)
                doc.rect(min(bx_a, bx_b), round(ankle_y), max(bx_a, bx_b), foot_y, b_col)
                if not is_far and boot_h >= 2:
                    doc.rect(min(bx_a, bx_b), round(ankle_y), max(bx_a, bx_b), round(ankle_y), b_hi)
                # Subtle dark seam separating near leg over far leg at >=24px
                if not is_far and m.h >= 24:
                    doc.line(round(hip_pt_x - xsign * leg_rad), round(hip_pt_y + 1), round(knee_x - xsign * leg_rad), round(knee_y), ramps.outline, only="empty")

    if view in ("down", "up"):
        sep = max(1.0, tw * 0.24)
        _draw_leg("leg_far", cx - sep, pose.stride_l, pose.lift_l, is_far=(pose.lift_l > 0.25))
        _draw_leg("leg_near", cx + sep, pose.stride_r, pose.lift_r, is_far=(pose.lift_r > 0.25))
    else:
        sep = 0.0 if view == "side" else max(1.0, tw * 0.18)
        _draw_leg("leg_far", cx - sep * xsign, pose.stride_r, pose.lift_r, is_far=True)
        _draw_leg("leg_near", cx + sep * xsign, pose.stride_l, pose.lift_l, is_far=False)

    # ---- 4. FAR ARM (behind torso — anchored strictly to torso edge, zero floating!) ----
    tx0 = round(cx + lean_px * 0.5 - tw * 0.5)
    tx1 = tx0 + tw - 1
    shoulder_y = torso_y0 + (1 if m.torso_h >= 5 else 0)

    def _draw_arm(layer_name: str, sh_x: float, swing: float, is_far: bool, side_anchor: str = "center") -> tuple[int, int]:
        """Draw arm + contrasting hand, returning hand (x, y) socket for weapon/shield."""
        doc.layer(layer_name)
        s_col = tunic_r.shadow if is_far else tunic_r.mid
        s_hi = tunic_r.mid if is_far else tunic_r.light
        h_col = skin_r.shadow if is_far else skin_r.mid
        hand_h = max(1, round(m.arm_h * 0.30))

        if view in ("down", "up"):
            dy_sw = round(swing * max(1.0, m.arm_h * 0.22))
            if side_anchor == "left":
                ax1 = tx0 - 1
                ax0 = ax1 - m.arm_w + 1
            elif side_anchor == "right":
                ax0 = tx1 + 1
                ax1 = ax0 + m.arm_w - 1
            else:
                ax0 = round(sh_x - m.arm_w * 0.5)
                ax1 = ax0 + m.arm_w - 1
            ay0 = shoulder_y + (dy_sw // 2)
            ay1 = ay0 + m.arm_h - 1
            hand_y0 = max(ay0 + 1, ay1 - hand_h + 1)
            doc.rect(ax0, ay0, ax1, hand_y0 - 1, s_col)
            if not is_far and m.arm_w >= 2:
                doc.rect(ax0, ay0, ax0, hand_y0 - 1, s_hi)
            doc.rect(ax0, hand_y0, ax1, ay1, h_col)
            return ((ax0 + ax1) // 2, ay1)
        else:
            # Side & 3/4 view: articulated swinging arm!
            ang = swing * 0.72 * xsign
            elbow_x = sh_x + math.sin(ang) * (m.arm_h * 0.55)
            elbow_y = shoulder_y + math.cos(ang) * (m.arm_h * 0.55)
            hand_x = elbow_x + math.sin(ang * 1.25 + 0.2 * xsign) * (m.arm_h * 0.48)
            hand_y = elbow_y + math.cos(ang * 1.15) * (m.arm_h * 0.42)
            if m.tier == "micro":
                doc.line(round(sh_x), shoulder_y, round(hand_x), round(hand_y), s_col)
                doc.px(round(hand_x), round(hand_y), h_col)
            else:
                arad = max(0.55, m.arm_w * 0.45)
                doc.capsule(sh_x, shoulder_y, elbow_x, elbow_y, arad, arad * 0.9, s_col)
                doc.capsule(elbow_x, elbow_y, hand_x, hand_y, arad * 0.85, arad * 0.75, s_col)
                if not is_far and m.arm_w >= 2:
                    doc.line(round(sh_x), shoulder_y, round(elbow_x), round(elbow_y), s_hi)
                hr = max(0.6, arad * 0.85)
                doc.capsule(hand_x, hand_y, hand_x, hand_y, hr, hr, h_col)
            return (round(hand_x), round(hand_y))

    if view in ("down", "up"):
        far_hand = _draw_arm("arm_far", tx0 - 1, pose.arm_l, is_far=(pose.arm_l < 0), side_anchor="left")
    else:
        far_sh_x = cx + xsign * (tw * 0.28) + lean_px * 0.5
        far_hand = _draw_arm("arm_far", far_sh_x, pose.arm_l, is_far=True)

    # ---- 5. TORSO LAYER (tunic / armor / belt / buckle / skeleton ribs) ----
    doc.layer("torso")
    _shade_rect(doc, tx0, torso_y0, tx1, torso_y1, tunic_r, lit_left=True, rounded=(m.h >= 24), radius=max(1, tw // 8))

    # Skeleton rib detail
    if spec.archetype == "skeleton" and m.torso_h >= 5:
        for ry in range(torso_y0 + 1, torso_y1 - 1, 2):
            doc.rect(tx0 + 1, ry, tx1 - 1, ry, ramps.skin.mid)
    else:
        # Collar / neckline V on front/3/4
        if view in ("down", "diag_front") and m.torso_h >= 4 and tw >= 5:
            collar_cx = round(cx + (xsign * max(1, tw // 6) if view == "diag_front" else 0))
            doc.px(collar_cx, torso_y0, skin_r.shadow)
            if m.h >= 32:
                doc.px(collar_cx - 1, torso_y0, tunic_r.highlight)
                doc.px(collar_cx + 1, torso_y0, tunic_r.highlight)
        # Knight armor chestplate highlight
        if spec.archetype == "knight" and m.torso_h >= 6 and tw >= 6:
            doc.rect(tx0 + 1, torso_y0 + 1, tx1 - 1, torso_y0 + max(1, m.torso_h // 3), ramps.metal.light)
            doc.rect(tx0 + 1, torso_y0 + 1, max(tx0 + 1, tx0 + tw // 3), torso_y0 + 1, ramps.metal.highlight)
        # Belt & buckle (anchored near bottom of torso!)
        if m.torso_h >= 3:
            belt_y = torso_y1 - (1 if m.torso_h >= 7 else 0)
            doc.rect(tx0, belt_y, tx1, belt_y, ramps.boots.shadow)
            if view != "up" and tw >= 5:
                bk_x = round(cx + (xsign * max(1, tw // 5) if view in ("side", "diag_front") else 0))
                bk_x = max(tx0, min(tx1, bk_x))
                doc.px(bk_x, belt_y, ramps.accent.highlight)
                if m.h >= 48 and bk_x + 1 <= tx1:
                    doc.px(bk_x + 1, belt_y, ramps.accent.mid)
        # Mage robe skirt extending cleanly over upper legs!
        if spec.archetype == "mage" and m.leg_h >= 3:
            skirt_y1 = min(m.ground_y - max(1, boot_h), torso_y1 + max(2, round(m.leg_h * 0.62)))
            for y in range(torso_y1 + 1, skirt_y1 + 1):
                t = (y - torso_y1) / max(1, skirt_y1 - torso_y1)
                extra = round(t * max(1, tw // 4))
                doc.rect(tx0 - extra, y, tx1 + extra, y, tunic_r.mid)
                doc.px(tx0 - extra, y, tunic_r.light)
                doc.px(tx1 + extra, y, tunic_r.shadow)
            # Gold hem trim
            doc.rect(tx0 - max(1, tw // 4), skirt_y1, tx1 + max(1, tw // 4), skirt_y1, ramps.accent.mid)

    # ---- 6. HEAD & DIRECTIONAL FACE LAYER ----
    doc.layer("head")
    hx_center = cx + lean_px
    hx0 = round(hx_center - hw * 0.5)
    hx1 = hx0 + hw - 1
    head_rad = max(1, hw // 5)

    # Base head shape (rounded pixel cranium!)
    if view == "up":
        # Back of head: NO face — filled with hair (except skeleton skull & nape strip)!
        base_head_r = skin_r if spec.hair_style == "bald" else ramps.hair
        _shade_rect(doc, hx0, head_y0, hx1, head_y1, base_head_r, lit_left=True, rounded=(hw >= 5), radius=head_rad)
        # Subtle skin nape at very bottom row
        if m.head_h >= 6 and spec.hair_style != "bald":
            nape_w = max(2, hw // 3)
            doc.rect(round(hx_center - nape_w * 0.5), head_y1, round(hx_center + nape_w * 0.5), head_y1, skin_r.shadow)
    else:
        _shade_rect(doc, hx0, head_y0, hx1, head_y1, skin_r, lit_left=True, rounded=(hw >= 5), radius=head_rad)

        # Goblin pointed ears sticking out cleanly!
        if spec.archetype == "goblin" and m.h >= 12:
            ear_y = head_y0 + max(1, m.head_h // 2)
            ear_len = max(2, hw // 3)
            if view in ("down", "up"):
                doc.rect(hx0 - ear_len, ear_y, hx0 - 1, ear_y, skin_r.mid)
                doc.rect(hx1 + 1, ear_y, hx1 + ear_len, ear_y, skin_r.shadow)
            else:
                back_x = hx0 - ear_len if xsign > 0 else hx1 + 1
                doc.rect(back_x, ear_y, back_x + ear_len - 1, ear_y, skin_r.mid)

        # Eyes (strictly following Rule 6 of views-and-directions!)
        eye_y = head_y0 + max(1, round(m.head_h * 0.54))
        eye_h = 2 if m.head_h >= 8 else 1
        eye_w = 2 if hw >= 14 else 1
        if not pose.blink:
            if view == "down":
                gap = max(1, round(hw * 0.22))
                for ex in (round(hx_center - gap - (eye_w - 1)), round(hx_center + gap)):
                    ex = max(hx0 + 1, min(hx1 - eye_w, ex))
                    doc.rect(ex, eye_y, ex + eye_w - 1, min(head_y1 - 1, eye_y + eye_h - 1), ramps.eye)
                    if eye_w >= 2:
                        doc.px(ex, eye_y, ramps.white)
                # Subtle mouth hint on >=32px
                if m.head_h >= 10:
                    doc.rect(round(hx_center) - 1, min(head_y1 - 1, eye_y + eye_h + 1), round(hx_center), min(head_y1 - 1, eye_y + eye_h + 1), skin_r.shadow)
            elif view == "diag_front":
                shift = xsign * max(1, round(hw * 0.14))
                gap = max(1, round(hw * 0.20))
                for ex in (round(hx_center + shift - gap), round(hx_center + shift + gap)):
                    ex = max(hx0 + 1, min(hx1 - eye_w, ex))
                    doc.rect(ex, eye_y, ex + eye_w - 1, min(head_y1 - 1, eye_y + eye_h - 1), ramps.eye)
                    if eye_w >= 2:
                        doc.px(ex, eye_y, ramps.white)
            elif view == "side":
                # ONE eye hugging the front edge!
                ex = (hx1 - eye_w) if xsign > 0 else (hx0 + 1)
                doc.rect(ex, eye_y, ex + eye_w - 1, min(head_y1 - 1, eye_y + eye_h - 1), ramps.eye)
                if eye_w >= 2:
                    doc.px(ex, eye_y, ramps.white)
            elif view == "diag_back":
                pass
        else:
            if view in ("down", "diag_front"):
                doc.rect(hx0 + 2, eye_y, hx1 - 2, eye_y, skin_r.shadow)

    # ---- 7. HAIR FRONT LAYER ----
    if spec.hair_style != "bald":
        doc.layer("hair_front")
        cap_h = max(1, round(m.head_h * (0.36 if m.tier == "micro" else 0.38)))
        if view == "up":
            # Back view hair shine cluster & silhouette contour
            hi_y = head_y0 + max(1, m.head_h // 4)
            doc.rect(hx0 + max(1, hw // 4), hi_y, hx1 - max(1, hw // 3), hi_y, ramps.hair.light)
            if spec.hair_style == "spiky" and m.h >= 16:
                doc.px(round(hx_center) - 1, head_y0 - 1, ramps.hair.mid)
                doc.px(round(hx_center) + 1, head_y0 - 1, ramps.hair.mid)
        elif view == "diag_back":
            # Hair covers 75-80% of head, leaving a small cheek sliver on facing edge!
            _shade_rect(doc, hx0, head_y0, hx1, head_y1, ramps.hair, lit_left=True, rounded=(hw >= 5))
            # Reveal small cheek sliver on facing edge
            sliver_x = hx1 if xsign > 0 else hx0
            doc.rect(sliver_x, head_y0 + cap_h + 1, sliver_x, max(head_y0 + cap_h + 1, head_y1 - 1), skin_r.mid)
        elif view == "side":
            # Crown hair + back hair covering back half of head (away from facing side!)
            _shade_rect(doc, hx0, head_y0, hx1, head_y0 + cap_h - 1, ramps.hair, lit_left=True, rounded=False)
            back_w = max(2, round(hw * 0.44))
            if xsign > 0:
                doc.rect(hx0, head_y0, hx0 + back_w - 1, head_y1 - 1, ramps.hair.mid)
                doc.rect(hx0, head_y0 + 1, hx0, head_y1 - 1, ramps.hair.shadow)
            else:
                doc.rect(hx1 - back_w + 1, head_y0, hx1, head_y1 - 1, ramps.hair.mid)
                doc.rect(hx1, head_y0 + 1, hx1, head_y1 - 1, ramps.hair.shadow)
            # Highlight cluster on crown
            if hw >= 6:
                doc.rect(hx0 + 1, head_y0 + (1 if cap_h >= 2 else 0), hx0 + max(2, hw // 3), head_y0 + (1 if cap_h >= 2 else 0), ramps.hair.light)
        else:
            # Front (down) & Front 3/4 (diag_front): crown + sideburns + asymmetric bangs!
            _shade_rect(doc, hx0, head_y0, hx1, head_y0 + cap_h - 1, ramps.hair, lit_left=True, rounded=False)
            # Hair side framing
            if hw >= 6 and m.head_h >= 5:
                doc.rect(hx0, head_y0 + 1, hx0, head_y1 - 2, ramps.hair.mid)
                doc.rect(hx1, head_y0 + 1, hx1, head_y1 - 2, ramps.hair.shadow)
                # Asymmetric fringe tuft breaking symmetry!
                fringe_x = round(hx_center + (xsign if view == "diag_front" else 1))
                doc.px(min(hx1 - 1, max(hx0 + 1, fringe_x)), head_y0 + cap_h, ramps.hair.mid)
            if spec.hair_style == "spiky" and m.h >= 16:
                doc.px(hx0 + 1, head_y0 - 1, ramps.hair.light)
                doc.px(round(hx_center), head_y0 - 1, ramps.hair.mid)
                doc.px(hx1 - 1, head_y0 - 1, ramps.hair.shadow)

    # ---- 8. HEADGEAR LAYER (helmet, wizard_hat, hood, crown, headband) ----
    if spec.headgear != "none":
        doc.layer("headgear")
        if spec.headgear == "wizard_hat":
            brim_y = head_y0 + max(1, m.head_h // 5)
            brim_ext = max(1, hw // 3)
            doc.rect(hx0 - brim_ext, brim_y, hx1 + brim_ext, brim_y, ramps.tunic.shadow)
            if m.h >= 24:
                doc.rect(hx0 - brim_ext + 1, brim_y - 1, hx1 + brim_ext - 1, brim_y - 1, ramps.tunic.mid)
                doc.rect(hx0, brim_y - 1, hx1, brim_y - 1, ramps.accent.mid)  # Hat band!
            cone_h = max(2, round(m.head_h * 0.72))
            for i in range(1, cone_h + 1):
                t = i / cone_h
                cw_i = max(1, round(hw * (1.0 - t * 0.85)))
                tip_shift = round((t * t) * max(1, hw // 3) * (-xsign if view == "side" else 1))
                cx0 = round(hx_center - cw_i * 0.5 + tip_shift)
                cx1 = cx0 + cw_i - 1
                cy = max(0, brim_y - 1 - i)
                doc.rect(cx0, cy, cx1, cy, ramps.tunic.light if t > 0.5 else ramps.tunic.mid)
                if cx1 > cx0:
                    doc.px(cx1, cy, ramps.tunic.shadow)
        elif spec.headgear == "helmet":
            helm_y1 = head_y0 + max(2, round(m.head_h * 0.52))
            _shade_rect(doc, hx0, head_y0, hx1, helm_y1, ramps.metal, lit_left=True, rounded=(hw >= 5))
            # Plume crest on top!
            plume_h = max(1, m.head_h // 3)
            px_c = round(hx_center)
            doc.rect(px_c - (1 if m.h >= 32 else 0), max(0, head_y0 - plume_h), px_c + (1 if m.h >= 32 else 0), head_y0 - 1, ramps.cape.light)
            if view == "side":
                doc.rect(px_c - xsign * max(1, hw // 3), max(0, head_y0 - plume_h + 1), px_c, max(0, head_y0 - 1), ramps.cape.mid)
        elif spec.headgear == "hood":
            _shade_rect(doc, hx0 - (1 if m.h >= 24 else 0), head_y0, hx1 + (1 if m.h >= 24 else 0), head_y0 + max(2, round(m.head_h * 0.42)), ramps.cape, lit_left=True, rounded=True)
            if view != "up" and hw >= 6:
                doc.rect(hx0, head_y0 + 1, hx0, head_y1, ramps.cape.mid)
                doc.rect(hx1, head_y0 + 1, hx1, head_y1, ramps.cape.shadow)
        elif spec.headgear == "headband":
            band_y = head_y0 + max(1, round(m.head_h * 0.32))
            doc.rect(hx0, band_y, hx1, band_y, ramps.accent.mid)
            if view in ("up", "side", "diag_back") and m.h >= 16:
                tail_x = (hx0 - 2) if xsign > 0 else (hx1 + 1)
                doc.rect(tail_x, band_y + 1, tail_x + 1, band_y + 2, ramps.accent.shadow)
        elif spec.headgear == "crown":
            cy = max(0, head_y0 - 1)
            doc.rect(hx0 + 1, cy, hx1 - 1, cy, ramps.accent.highlight)
            doc.px(hx0 + 1, max(0, cy - 1), ramps.accent.highlight)
            doc.px(round(hx_center), max(0, cy - 1), ramps.accent.highlight)
            doc.px(hx1 - 1, max(0, cy - 1), ramps.accent.highlight)

    # ---- 9. NEAR ARM LAYER (in front of torso) ----
    if view in ("down", "up"):
        near_hand = _draw_arm("arm_near", tx1 + 1, pose.arm_r, is_far=(pose.arm_r < 0), side_anchor="right")
    else:
        near_sh_x = cx - xsign * (tw * 0.14) + lean_px * 0.5
        near_hand = _draw_arm("arm_near", near_sh_x, pose.arm_r, is_far=False)

    # ---- 10. WEAPON & SHIELD LAYERS (modular equipment!) ----
    if spec.weapon != "none" and m.h >= 12:
        _draw_weapon_layer(doc, m, ramps, spec, view, xsign, near_hand, pose)

    if spec.shield != "none" and m.h >= 16:
        doc.layer("shield")
        sx, sy = far_hand if view in ("down", "up") else (round(cx + xsign * (tw * 0.35)), torso_y0 + m.torso_h // 2)
        srx = max(2, round(m.w * 0.10))
        sry = max(2, round(m.h * 0.12))
        doc.rounded_rect(sx - srx, sy - sry, sx + srx, sy + sry, ramps.metal.mid, radius=1, fill=True)
        doc.rect(sx - srx, sy - sry, sx + srx, sy - sry, ramps.metal.highlight)
        doc.rect(sx - srx + 1, sy - sry + 1, sx + srx - 1, sy + sry - 1, ramps.tunic.mid)
        doc.px(sx, sy, ramps.accent.highlight)

    # ---- 11. VFX LAYER (slash arc / spell glow) ----
    if pose.slash_alpha > 0.15 and m.h >= 12:
        doc.layer("vfx")
        arc_r = max(3, round(m.w * 0.32))
        acx = near_hand[0] + xsign * max(1, arc_r // 3)
        acy = near_hand[1] - max(1, arc_r // 4)
        for deg in range(-65, 70, 12):
            rad = math.radians(deg)
            px_ = round(acx + math.cos(rad) * arc_r * xsign)
            py_ = round(acy + math.sin(rad) * arc_r)
            col = ramps.white if abs(deg) < 25 else ramps.magic.light
            doc.px(px_, py_, col)
            if m.h >= 32:
                doc.px(px_ - xsign, py_, ramps.magic.mid)

    if pose.cast_glow > 0.2 and m.h >= 12:
        doc.layer("vfx")
        gx = near_hand[0] + (xsign * max(2, m.w // 8) if view != "down" else 0)
        gy = max(2, head_y0 + (0 if view == "up" else m.head_h // 2))
        gr = max(1, round(pose.cast_glow * max(2, m.w * 0.14)))
        doc.circle(gx, gy, gr, ramps.magic.mid, fill=False)
        doc.circle(gx, gy, max(0, gr - 1), ramps.magic.highlight, fill=True)
        doc.px(gx, gy, ramps.white)

    # ---- 12. UNIFIED SELECTIVE OUTLINE ----
    if m.use_outline:
        _apply_unified_outline(doc, ramps)


def _draw_weapon_layer(
    doc: SpriteDocument,
    m: _Metrics,
    ramps: _Ramps,
    spec: CharacterSpec,
    view: str,
    xsign: int,
    hand: tuple[int, int],
    pose: _Pose,
) -> None:
    doc.layer("weapon")
    hx, hy = hand
    wlen = max(4, round(m.h * 0.30))

    if spec.weapon == "sword":
        if view in ("down", "up"):
            # Angled cleanly down-right or lifted on attack
            ang = math.radians(-115 if pose.weapon_angle < -0.2 else (25 if pose.weapon_angle > 0.3 else 55))
            tx = round(hx + math.cos(ang) * wlen * 0.75)
            ty = round(hy + math.sin(ang) * wlen * 0.75)
            doc.line(hx, hy, tx, ty, ramps.metal.highlight, pixel_perfect=True)
            if m.h >= 32:
                doc.line(hx + 1, hy, tx + 1, ty, ramps.metal.mid, pixel_perfect=True)
            doc.rect(hx - 1, hy, hx + 1, hy, ramps.accent.mid)
        else:
            # Side & 3/4 view: crisp sweeping sword arc!
            base_ang = -45.0 + pose.weapon_angle * 75.0
            rad = math.radians(base_ang)
            tx = round(hx + math.cos(rad) * wlen * xsign)
            ty = round(hy + math.sin(rad) * wlen)
            doc.line(hx, hy, tx, ty, ramps.metal.highlight, pixel_perfect=True)
            if m.h >= 24:
                doc.line(hx, hy + 1, tx, ty + 1, ramps.metal.mid, pixel_perfect=True)
            doc.px(hx, hy, ramps.accent.highlight)
            doc.px(hx, max(0, hy - 1), ramps.accent.mid)
            doc.px(hx, min(m.h - 1, hy + 1), ramps.accent.shadow)

    elif spec.weapon == "staff":
        staff_h = max(6, round(m.h * 0.56))
        top_y = max(1, hy - round(staff_h * 0.65) - round(pose.cast_glow * 2))
        bot_y = min(m.ground_y, hy + round(staff_h * 0.35))
        sx = hx + (xsign if view != "down" else 1)
        sx = max(1, min(m.w - 2, sx))
        doc.line(sx, top_y, sx, bot_y, ramps.boots.mid)
        # Glowing crystal orb at top!
        orb_r = max(1, m.w // 18)
        doc.circle(sx, top_y, orb_r, ramps.magic.mid, fill=True)
        doc.px(sx, top_y, ramps.white if pose.cast_glow > 0.3 else ramps.magic.highlight)

    elif spec.weapon == "dagger":
        dlen = max(3, round(m.h * 0.16))
        tx = hx + xsign * dlen
        ty = hy + round(pose.weapon_angle * 3)
        doc.line(hx, hy, tx, ty, ramps.metal.highlight, pixel_perfect=True)
        doc.px(hx, hy, ramps.accent.mid)

    elif spec.weapon == "bow":
        bh = max(4, round(m.h * 0.28))
        bx = hx + (xsign * 2 if view != "down" else 1)
        bx = max(1, min(m.w - 2, bx))
        doc.line(bx, hy - bh // 2, bx + xsign, hy, ramps.boots.light)
        doc.line(bx + xsign, hy, bx, hy + bh // 2, ramps.boots.mid)
        doc.line(bx, hy - bh // 2, bx, hy + bh // 2, ramps.white)

    elif spec.weapon == "axe":
        alen = max(4, round(m.h * 0.28))
        rad = math.radians(-40.0 + pose.weapon_angle * 75.0)
        tx = round(hx + math.cos(rad) * alen * xsign)
        ty = round(hy + math.sin(rad) * alen)
        doc.line(hx, hy, tx, ty, ramps.boots.mid)
        doc.rect(tx - 1, ty - 1, tx + 1, ty + 1, ramps.metal.light)
        doc.px(tx + xsign, ty, ramps.metal.highlight)


def _draw_fallen_humanoid(
    doc: SpriteDocument,
    m: _Metrics,
    ramps: _Ramps,
    spec: CharacterSpec,
    view: str,
    xsign: int,
    pose: _Pose,
) -> None:
    """Render collapsed death final pose cleanly grounded on `ground_y`."""
    cx = m.cx
    gy = m.ground_y
    doc.layer("shadow")
    if m.h >= 12:
        doc.ellipse(round(cx - m.w * 0.36), gy - 1, round(cx + m.w * 0.36), gy + 1, ramps.shadow_col, fill=True)
    # Horizontal fallen body
    body_w = max(6, round(m.body_h * 0.65))
    body_t = max(2, round(m.torso_w * 0.45))
    x0 = max(1, round(cx - body_w * 0.5))
    x1 = min(m.w - 2, x0 + body_w - 1)
    y1 = gy
    y0 = max(1, y1 - body_t)
    doc.layer("torso")
    _shade_rect(doc, x0 + body_w // 4, y0, x1 - body_w // 5, y1, ramps.tunic)
    doc.layer("leg_near")
    doc.rect(x1 - body_w // 4, y0 + 1, x1, y1, ramps.boots.shadow)
    doc.layer("head")
    hx0 = x0
    hx1 = min(x1, x0 + max(3, m.head_h // 2))
    _shade_rect(doc, hx0, max(1, y0 - 1), hx1, y1, ramps.hair if view == "up" else ramps.skin, rounded=True)
    if spec.has_cape and m.h >= 16:
        doc.layer("cape_back")
        doc.rect(x0 + 2, y0, x1 - 2, y0 + 1, ramps.cape.shadow)


# ---------------------------------------------------------------------------
# Public High-Level Character Builder API
# ---------------------------------------------------------------------------


def build_character_action(
    width: int = 32,
    height: int = 32,
    action: str = "walk",
    direction: str = "down",
    frames: int = 8,
    fps: int = 10,
    archetype: str = "hero",
    palette: str | Sequence[str] | None = "endesga-32",
    spec: CharacterSpec | None = None,
) -> SpriteDocument:
    """Build a multi-layer SpriteDocument for ONE (action, direction) at ANY resolution & frame count."""
    action = action.lower().strip()
    if action not in ACTIONS:
        raise ValueError(f"Unknown action {action!r}. Valid actions: {ACTIONS}")
    frames = max(1, int(frames))
    spec = spec or preset_spec(archetype)

    pal_rgbas = None
    if palette is not None:
        _, pal_rgbas = load_palette(palette)

    doc = SpriteDocument(width, height, palette=palette, snap=(palette is not None), default_fps=fps)
    doc.ensure_rig_layers(RIG_LAYERS)
    ramps = _build_ramps(spec, pal_rgbas)
    metrics = _compute_metrics(
        width, height,
        is_slime=(spec.archetype == "slime"),
        tall_headgear=(spec.headgear in ("wizard_hat", "helmet", "crown")),
    )
    base_ms = max(16, round(1000.0 / max(1, fps)))

    for fi in range(frames):
        if fi > 0:
            doc.add_frame(copy=False)
        pose, dur_mult = _compute_pose(action, fi, frames)
        doc.set_duration(max(16, round(base_ms * dur_mult)))
        if spec.archetype == "slime":
            _draw_slime_frame(doc, metrics, ramps, spec, direction, pose)
        else:
            _draw_humanoid_frame(doc, metrics, ramps, spec, direction, pose)

    d_clean = DIR_ALIASES.get(direction.lower().strip(), direction.lower().strip())
    tag_dir = "pingpong" if (action == "idle" and frames == 2) else "forward"
    doc.tag(f"{action}_{d_clean}", 1, frames, direction=tag_dir)
    doc.metadata = {
        "archetype": spec.archetype,
        "action": action,
        "direction": d_clean,
        "frames": frames,
        "fps": fps,
        "tier": metrics.tier,
        "ground_y": metrics.ground_y,
    }
    return doc


def build_character_pack(
    width: int = 32,
    height: int = 32,
    actions: Sequence[str] = ("idle", "walk", "run", "attack"),
    directions: str | Sequence[str] = "4",
    frames: int | dict[str, int] = 8,
    fps: int | dict[str, int] = 10,
    archetype: str = "hero",
    palette: str | Sequence[str] | None = "endesga-32",
    spec: CharacterSpec | None = None,
) -> tuple[SpriteDocument, dict[tuple[str, str], SpriteDocument]]:
    """Build a complete multi-action × multi-direction character sheet with intact layers & tags!

    Returns:
        (master_doc, per_clip_docs)
        where `master_doc` contains ALL frames & animation tags (`{action}_{dir}`) on a shared rig!
    """
    if isinstance(directions, str):
        dir_list = DIR_SETS[directions] if directions in DIR_SETS else [d.strip() for d in directions.split(",") if d.strip()]
    else:
        dir_list = list(directions)

    spec = spec or preset_spec(archetype)
    pal_rgbas = None
    if palette is not None:
        _, pal_rgbas = load_palette(palette)

    master = SpriteDocument(width, height, palette=palette, snap=(palette is not None))
    master.ensure_rig_layers(RIG_LAYERS)
    per_clip: dict[tuple[str, str], SpriteDocument] = {}

    first_frame_used = False
    for act in actions:
        n_f = frames[act] if isinstance(frames, dict) else int(frames)
        act_fps = fps[act] if isinstance(fps, dict) else int(fps)
        for d in dir_list:
            clip = build_character_action(
                width=width, height=height, action=act, direction=d,
                frames=n_f, fps=act_fps, archetype=archetype, palette=palette, spec=spec,
            )
            d_clean = DIR_ALIASES.get(d.lower().strip(), d.lower().strip())
            per_clip[(act, d_clean)] = clip

            start_idx = 1 if not first_frame_used else master.n_frames + 1
            for fi, fr in enumerate(clip.frames):
                if not first_frame_used:
                    master.frames[0].duration_ms = fr.duration_ms
                    master.frames[0].cels = {k: v.copy() for k, v in fr.cels.items()}
                    first_frame_used = True
                else:
                    master.add_frame(copy=False, duration_ms=fr.duration_ms)
                    master.frames[-1].cels = {k: v.copy() for k, v in fr.cels.items()}
            end_idx = master.n_frames
            tag_dir = "pingpong" if (act == "idle" and n_f == 2) else "forward"
            master.tag(f"{act}_{d_clean}", start_idx, end_idx, direction=tag_dir)

    master.metadata = {
        "archetype": spec.archetype,
        "actions": list(actions),
        "directions": [DIR_ALIASES.get(d.lower().strip(), d) for d in dir_list],
        "size": [width, height],
        "total_frames": master.n_frames,
    }
    return master, per_clip
