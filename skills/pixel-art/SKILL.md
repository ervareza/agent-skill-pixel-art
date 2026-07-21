---
name: pixel-art
description: "Use this skill whenever the user wants to create, edit, audit, or export 2D pixel art assets. This includes: generating sprite sheets, character walk cycles, tilesets, autotile maps, UI elements, particle effects, isometric art, or any retro-style low-resolution raster graphics. Triggers include: any mention of 'pixel art', 'sprite', 'tileset', 'autotile', '16x16', '32x32', 'retro game art', 'game sprites', 'sprite sheet', 'palette', 'NES colors', 'PICO-8', 'GameBoy palette', 'isometric', 'particle effect', 'pixel UI', or requests to produce game-ready PNG assets with strict color limits and no anti-aliasing. Also use when auditing existing pixel art for quality issues (orphan pixels, semi-transparent artifacts, palette violations), resizing sprites, extracting palettes, mirroring frames, adding outlines, generating noise textures, creating dithered gradients, or exporting animated GIFs. Do NOT use for vector art, SVG illustrations, 3D models, photo editing, or high-resolution digital painting."
license: MIT
---

# 2D Pixel Art Asset Creation

Create game-ready 2D pixel art assets — sprites, tilesets, autotiles, UI elements, particle effects, and isometric art — with strict pixel-grid alignment, palette enforcement, quality auditing, and game engine export.

**Scripts Available** (paths relative to this skill's directory):

| Script | What it does |
|---|---|
| `scripts/init_workspace.py` | Creates project directories and an asset manifest |
| `scripts/quality_audit.py` | Audits a PNG for anti-aliasing, orphan pixels, palette violations, and grid alignment |
| `scripts/batch_audit.py` | Audits ALL PNGs in a directory at once for mass QA |
| `scripts/palette_remap.py` | Remaps image colors to a target palette using nearest-color matching |
| `scripts/palette_extract.py` | Extracts the color palette from an existing image with frequency analysis |
| `scripts/atlas_pack.py` | Packs multiple sprite frames into a single sprite sheet with JSON metadata |
| `scripts/export_indexed.py` | Converts RGBA PNGs to indexed 8-bit PNGs with optional color reduction |
| `scripts/sprite_resize.py` | Resizes pixel art with nearest-neighbor ONLY (no blurring) |
| `scripts/sprite_mirror.py` | Mirrors sprites horizontally or vertically (single or batch) |
| `scripts/gif_export.py` | Converts sprite sheets or frame directories to animated GIFs |
| `scripts/outline_generator.py` | Adds 1px outline around opaque pixels for readability |
| `scripts/dither.py` | Generates ordered dithered gradients using Bayer matrix |
| `scripts/noise_generator.py` | Generates procedural noise textures for terrain |

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
    │     1. Read references/sprite_conventions.md + references/animation_principles.md
    │     2. Create individual frames as separate PNGs
    │     3. Run: python scripts/atlas_pack.py --frames-dir <dir> --output sheet.png --cols 4 --json
    │     4. Run: python scripts/quality_audit.py sheet.png --json
    │     5. Preview: open templates/sprite_sheet.html, load the sheet
    │     6. Optional: python scripts/gif_export.py --sheet sheet.png --frame-width 16 --frame-height 16 --fps 8 --output preview.gif --json
    │
    ├─ 8-way character sheet (from 5 directions)
    │     1. Draw 5 directions: S, SW, W, NW, N
    │     2. Run: python scripts/sprite_mirror.py --input-dir ./east_frames/ --output-dir ./west_frames/ --axis horizontal --json
    │     3. Pack all directions into atlas
    │
    ├─ Tileset / Autotile map
    │     1. Read references/tileset_rules.md for grid and autotile conventions
    │     2. Create tiles at the target grid size (8x8, 16x16, 32x32)
    │     3. Run: python scripts/quality_audit.py <tileset> --json
    │     4. Preview: open templates/tilemap_preview.html, load the tileset
    │
    ├─ Isometric art
    │     1. Read references/isometric_guide.md for projection, stacking, depth
    │     2. Use 2:1 pixel ratio (64×32 diamonds for standard tiles)
    │     3. Consistent lighting: top-right source
    │
    ├─ UI elements (health bars, buttons, dialogs)
    │     1. Read references/ui_elements.md for 9-slice, bar styles, button states
    │     2. Create at target resolution, use 9-slice for scalable panels
    │
    ├─ Particle effects (explosion, fire, smoke)
    │     1. Read references/particle_effects.md for spawn patterns and timing
    │     2. Create frame-by-frame, pack into atlas
    │
    ├─ Palette remap (recolor existing art)
    │     1. Run: python scripts/palette_remap.py --image <input> --palette palettes/<name>.json --output <out> --json
    │     2. Run: python scripts/quality_audit.py <out> --json
    │
    ├─ Extract palette from reference art
    │     1. Run: python scripts/palette_extract.py --image <ref> --max-colors 16 --output palettes/custom.json --json
    │
    ├─ Resize for export
    │     1. Run: python scripts/sprite_resize.py --input <img> --output <out> --scale 2 --json
    │
    ├─ Add outline for readability
    │     1. Run: python scripts/outline_generator.py --input <img> --output <out> --color "#1A1A2E" --json
    │
    ├─ Generate terrain texture
    │     1. Run: python scripts/noise_generator.py --width 64 --height 64 --palette palettes/pico-8.json --output terrain.png --json
    │
    └─ Batch QA before release
          1. Run: python scripts/batch_audit.py --dir <sprites_folder> --grid 16 --max-colors 16 --json
```

## Gotchas — Pixel Art Rules

- **Zero anti-aliasing.** Every pixel must be fully opaque (`alpha=255`) or fully transparent (`alpha=0`). No semi-transparent pixels. Ever.
- **Strict palette limits.** Never exceed the color count defined by the target palette. PICO-8 = 16 colors. GameBoy = 4 colors. If you're over, remap first.
- **Grid-snap everything.** Sprite dimensions must be exact multiples of the base grid (8, 16, 32). A 24x30 sprite is wrong — use 32x32 and leave transparent padding.
- **No orphan pixels.** A single isolated pixel with zero opaque neighbors is almost always a mistake. Audit and clean them.
- **Nearest-neighbor scaling only.** Never use bilinear, bicubic, or Lanczos when resizing pixel art. Only `Image.Resampling.NEAREST`. Use `scripts/sprite_resize.py`.
- **Export as indexed PNG.** Final game assets should be indexed-color PNGs, not RGBA. Use `scripts/export_indexed.py`.
- **Mirror to save texture memory.** For 8-way character sheets, draw only 5 directions and mirror for the other 3. Use `scripts/sprite_mirror.py`.
- **Consistent light source.** Always illuminate from top-right. Shadows bottom-left. This is the pixel art convention.
- **Exaggerate at low resolution.** At 16×16, subtlety is invisible. Push poses ±2px further than realistic. Read `references/animation_principles.md`.

## Palette References

Palette JSON files live in `palettes/`. Each file contains a `name`, `colors` array (hex strings), and `max_colors` count:

```json
{
  "name": "pico-8",
  "max_colors": 16,
  "colors": ["#000000", "#1D2B53", "#7E2553", "..."]
}
```

Available palettes: `pico-8.json`, `gameboy.json`, `nes.json`, `endesga-32.json`, `resurrect-64.json`, `sweetie-16.json`, `db32.json`, `cga.json`, `commodore-64.json`, `snes.json`

You can also extract a palette from any existing image: `python scripts/palette_extract.py --image reference.png --max-colors 16 --output palettes/custom.json --json`

## Template Reference

The `templates/` directory contains interactive HTML tools:

- `templates/sprite_sheet.html` — Sprite sheet viewer with animation playback, zoom, frame navigation
- `templates/tilemap_preview.html` — Tilemap painter: select tiles, paint on grid, random fill
- `templates/palette_viewer.html` — Palette comparison tool with swatch display and color picker

## Further Reading

- [Sprite Conventions](references/sprite_conventions.md) — Frame sizes, animation timing, directional layouts
- [Artistic Generation](references/artistic_generation.md) — Cluster shading, hue shifting, Voronoi, foliage & tree algorithms
- [Animation Principles](references/animation_principles.md) — 12 Disney principles applied to pixel art
- [Tileset Rules](references/tileset_rules.md) — Grid sizes, Wang autotile bitmasks, terrain transitions
- [Isometric Guide](references/isometric_guide.md) — 2:1 projection, tile stacking, depth sorting
- [Color Theory](references/color_theory.md) — Palette design, contrast ratios, hue ramps for pixel art
- [UI Elements](references/ui_elements.md) — Health bars, buttons, dialog boxes, 9-slice panels
- [Particle Effects](references/particle_effects.md) — Explosions, fire, smoke, sparkles, magic VFX

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Blurry after resize | Used bilinear/bicubic | Use `sprite_resize.py` (nearest-neighbor only) |
| Visible seams in tileset | Tiles don't tile seamlessly | Check center tile (MM) edges match on all sides |
| Colors look wrong in-game | Exported as RGBA, engine expects indexed | Use `export_indexed.py` |
| Animation looks choppy | Not enough frames | Minimum 4 frames for walk cycle, read `animation_principles.md` |
| Sprite hard to see on background | No outline, low contrast | Use `outline_generator.py` or increase palette contrast |
| Too many colors for target platform | No palette enforcement | Run `palette_remap.py` before export |
| File size too large | RGBA with transparency | Export as indexed PNG, trim unused colors |

## Engine-Specific Tips

### Godot 4
- Import PNGs with `Texture2D` filter mode set to **Nearest**
- Use `AnimatedSprite2D` with atlas from `atlas_pack.py` JSON metadata
- Tileset: import to `TileSet` resource, set tile size to match grid

### Unity
- Set texture import as **Point (no filter)**, **Sprite Mode: Multiple**
- Slice with Automatic or Grid mode matching your frame dimensions
- Set **Pixels Per Unit** to match your tile size (16 for 16×16 tiles)

### Defold
- Set texture sampling to **Nearest**
- Import atlas JSON metadata as tile source
- Use `go.property` for palette switching at runtime
