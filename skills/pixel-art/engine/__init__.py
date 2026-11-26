"""PixelForge Engine v1.0.0 — Pure-Python 2D pixel art & game asset engine.

Synthesized from the best practices of top open-source pixel art tools and skills:
- Multi-layer × multi-frame SpriteDocument with blend modes, opacity, linked cels
- Hue-shifted color ramps, selective outlines (selout), rim light, band-edge dithering
- Layered multi-directional character rigging (1/2/4/8-dir, 8px..128px+, 2..60 frames)
- Seamless toroidal terrain & 16-tile Wang / 47-tile Blob autotiles + 2:1 isometric
- Seeded two-buffer procedural pixel VFX (color + additive light)
- Game items, weapons, ZzSprite creatures, 9-slice UI, and fake-3D sprite stacking
- Universal game engine exporters (.aseprite binary, JSON, Godot 4 .tres, Unity, Phaser, RPG Maker, LPC, GIF, Indexed PNG)
- Automated pixel art QA auditor (AA, orphans, jaggies, doubles, loop continuity, seamlessness)

Zero external binary dependencies — Python 3.9+ and Pillow only.
"""

__version__ = "1.0.0"

from .color import (
    PALETTES,
    ColorRamp,
    hex_to_rgba,
    rgba_to_hex,
    perceptual_dist2,
    nearest_color,
    mix_color,
    hue_ramp,
    load_palette,
    list_palettes,
    render_swatch,
)
from .canvas import (
    Layer,
    Frame,
    SpriteDocument,
    BAYER2,
    BAYER4,
    BAYER8,
    detect_scale,
    estimate_scale,
    block_downscale,
    strip_checker,
)

__all__ = [
    "__version__",
    "PALETTES",
    "ColorRamp",
    "hex_to_rgba",
    "rgba_to_hex",
    "perceptual_dist2",
    "nearest_color",
    "mix_color",
    "hue_ramp",
    "load_palette",
    "list_palettes",
    "render_swatch",
    "Layer",
    "Frame",
    "SpriteDocument",
    "BAYER2",
    "BAYER4",
    "BAYER8",
    "detect_scale",
    "estimate_scale",
    "block_downscale",
    "strip_checker",
]
