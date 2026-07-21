---
name: pixel-art
description: "Use this skill whenever the user wants to create, edit, audit, or export 2D pixel art assets. This includes: generating sprite sheets, character walk cycles, tilesets, autotile maps, UI elements, particle effects, or any retro-style low-resolution raster graphics. Triggers include: any mention of 'pixel art', 'sprite', 'tileset', 'autotile', '16x16', '32x32', 'retro game art', 'game sprites', 'sprite sheet', 'palette', 'NES colors', 'PICO-8', 'GameBoy palette', or requests to produce game-ready PNG assets with strict color limits and no anti-aliasing. Also use when auditing existing pixel art for quality issues (orphan pixels, semi-transparent artifacts, palette violations). Do NOT use for vector art, SVG illustrations, 3D models, photo editing, or high-resolution digital painting."
license: MIT
---

# 2D Pixel Art Asset Creation

Create game-ready 2D pixel art assets — sprites, tilesets, autotiles, UI elements, and particle effects — with strict pixel-grid alignment, palette enforcement, and quality auditing.

**Scripts Available** (paths relative to this skill's directory):

| Script | What it does |
|---|---|
| `scripts/init_workspace.py` | Creates project directories and an asset manifest |
| `scripts/palette_remap.py` | Remaps image colors to a target palette using nearest-color matching |
| `scripts/quality_audit.py` | Audits a PNG for anti-aliasing, orphan pixels, palette violations, and grid alignment |
| `scripts/atlas_pack.py` | Packs multiple sprite frames into a single sprite sheet with JSON metadata |
| `scripts/export_indexed.py` | Converts RGBA PNGs to indexed 8-bit PNGs with optional color reduction |

**Always run scripts with `--help` first** to see usage. Do NOT read the source until you try running the script first and find that a customized solution is absolutely necessary.

## Decision Tree

```
User task → What type of pixel art?
    ├─ Single sprite/icon (≤64x64)
    │     1. Read palettes/*.json to pick a color palette
    │     2. Create the sprite as a PNG at the target resolution
    │     3. Run: python scripts/quality_audit.py <image> --json
    │     4. Fix any reported issues, re-audit until clean
    │
    ├─ Character sprite sheet (walk cycle, attack, etc.)
    │     1. Read palettes/*.json for palette + references/sprite_conventions.md for frame layout
    │     2. Create individual frames as separate PNGs
    │     3. Run: python scripts/atlas_pack.py --frames-dir <dir> --output sheet.png --json
    │     4. Run: python scripts/quality_audit.py sheet.png --json
    │
    ├─ Tileset / Autotile map
    │     1. Read references/tileset_rules.md for grid and autotile conventions
    │     2. Create tiles at the target grid size (8x8, 16x16, 32x32)
    │     3. Run: python scripts/quality_audit.py <tileset> --json
    │
    └─ Palette remap (recolor existing art)
          1. Run: python scripts/palette_remap.py --image <input> --palette palettes/<name>.json --output <out> --json
          2. Run: python scripts/quality_audit.py <out> --json
```

## Gotchas — Pixel Art Rules

- **Zero anti-aliasing.** Every pixel must be fully opaque (`alpha=255`) or fully transparent (`alpha=0`). No semi-transparent pixels. Ever.
- **Strict palette limits.** Never exceed the color count defined by the target palette. PICO-8 = 16 colors. GameBoy = 4 colors. If you're over, remap first.
- **Grid-snap everything.** Sprite dimensions must be exact multiples of the base grid (8, 16, 32). A 24x30 sprite is wrong — use 32x32 and leave transparent padding.
- **No orphan pixels.** A single isolated pixel with zero opaque neighbors is almost always a mistake. Audit and clean them.
- **Nearest-neighbor scaling only.** Never use bilinear, bicubic, or Lanczos when resizing pixel art. Only `Image.Resampling.NEAREST`.
- **Export as indexed PNG.** Final game assets should be indexed-color PNGs, not RGBA. Use `scripts/export_indexed.py`.
- **Mirror to save texture memory.** For 8-way character sheets, draw only East-facing frames and mirror for West. Don't duplicate art.

## Palette References

Palette JSON files live in `palettes/`. Each file contains a `name`, `colors` array (hex strings), and `max_colors` count:

```json
{
  "name": "pico-8",
  "max_colors": 16,
  "colors": ["#000000", "#1D2B53", "#7E2553", "..."]
}
```

Available palettes: `pico-8.json`, `gameboy.json`, `nes.json`, `endesga-32.json`, `resurrect-64.json`

## Template Reference

The `templates/` directory contains starter templates for common pixel art tasks:

- `templates/sprite_sheet.html` — Interactive HTML viewer for previewing sprite sheets with animation playback
- `templates/tilemap_preview.html` — Grid-based tilemap layout previewer

## Further Reading

- [Sprite Conventions](references/sprite_conventions.md) — Frame sizes, animation timing, directional layouts
- [Tileset Rules](references/tileset_rules.md) — Grid sizes, Wang autotile bitmasks, terrain transitions
- [Color Theory](references/color_theory.md) — Palette design, contrast ratios, hue ramps for pixel art
