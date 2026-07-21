---
name: pixel-art
description: "Use this skill whenever the user wants to create, edit, audit, or export 2D pixel art assets. This includes: generating sprite sheets, character walk cycles, tilesets, autotile maps, UI elements, particle effects, isometric art, or any retro-style low-resolution raster graphics. Triggers include: any mention of 'pixel art', 'sprite', 'tileset', 'autotile', '16x16', '32x32', 'retro game art', 'game sprites', 'sprite sheet', 'palette', 'NES colors', 'PICO-8', 'GameBoy palette', 'isometric', 'particle effect', 'pixel UI', or requests to produce game-ready PNG assets with strict color limits and no anti-aliasing. Also use when auditing existing pixel art for quality issues (orphan pixels, semi-transparent artifacts, palette violations), resizing sprites, extracting palettes, mirroring frames, adding outlines, generating noise textures, creating dithered gradients, or exporting animated GIFs. Do NOT use for vector art, SVG illustrations, 3D models, photo editing, or high-resolution digital painting."
license: MIT
---

# 2D Pixel Art Asset Creation

Create game-ready 2D pixel art assets — sprites, tilesets, autotiles, UI elements, particle effects, and isometric art — with strict pixel-grid alignment, palette enforcement, quality auditing, and game engine export.

**Core Pipeline**: `Design Brief → Style Selection → Spec Lock → Generate Assets → Quality Audit → Post-process → Pack & Export`

> [!CAUTION]
> ## 🚨 Global Execution Discipline (MANDATORY)
>
> 1. **PALETTE FIRST** — Select or extract a palette BEFORE generating any pixel. Every pixel MUST use only colors from the locked palette.
> 2. **SPEC LOCK RE-READ** — Before generating EACH asset, re-read the palette and size constraints. AI memory drifts during long sessions.
> 3. **SEQUENTIAL GENERATION** — Generate assets one at a time. Finish, audit, fix, then move to next.
> 4. **NO ANTI-ALIASING** — Every pixel must be fully opaque (alpha=255) or fully transparent (alpha=0). Zero exceptions.
> 5. **AUDIT BEFORE EXPORT** — Never export an asset that hasn't passed `quality_audit.py`.

---

## Scripts Available

| Script | What it does |
|---|---|
| `scripts/init_workspace.py` | Creates project directories and asset manifest |
| `scripts/quality_audit.py` | Audits a PNG for anti-aliasing, orphan pixels, palette violations, grid alignment |
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

**Always run scripts with `--help` first** to see usage.

---

## Style Presets

Before generating ANY pixel art, select a style preset. This determines canvas size, color budget, and shading technique.

| Style | Canvas Size | Colors Per Sprite | Shading | Use Case |
|---|---|---|---|---|
| **NES Classic** | 16×16 / 32×32 | 3-4 (excl. transparency) | Flat / 2-tone | Classic 8-bit console |
| **SNES Retro** | 32×32 / 64×64 | 8-15 | 2-tone / 3-tone | 16-bit era games |
| **Modern Pixel** | 32×32 / 64×64 | 16-31 | 3-tone / cel-shaded | Contemporary indie |
| **Minimalist** | 8×8 / 16×16 | 2-4 | Flat only | Ultra-simple, game jams |
| **Dense Detail** | 64×64 / 128×128 | 24-48 | Dithered / textured | Rich, detailed worlds |
| **High-Res Pixel** | 256×256 / 512×512 | 64-96 | Full shading | Illustration-grade |
| **Cinematic Pixel** | 1024×1024+ | 128-256 | Full shading + dither | Print/billboard quality |

**Recommendation logic**:
- User says "NES", "8-bit", "retro" → NES Classic at 16×16
- User says "SNES", "16-bit" → SNES Retro at 32×32
- User says "indie", "modern" → Modern Pixel at 32×32 or 64×64
- User says "detailed", "boss", "large" → Dense Detail at 64×64+
- User says "HD pixel art" → High-Res Pixel at 256×256+
- No preference → Default Modern Pixel at 32×32

---

## Pixel Art Generation Guidelines

### Core Principles

- **Pixel-perfect**: Every pixel is intentional; no sub-pixel rendering
- **Palette adherence**: Every pixel color MUST be from the declared palette
- **Readable silhouette**: Assets must be recognizable at target size
- **Consistent lighting**: Light source top-right across ALL assets in a project
- **Edge quality**: Outlines (if used) must be consistent width and color

### Shading & Depth Techniques

| Technique | When to Use | How |
|---|---|---|
| **Flat shading** | Minimalist, ≤16×16 | Single color per surface |
| **2-tone shading** | NES style, 16×16-32×32 | Base + 1 shadow |
| **3-tone shading** | SNES/Modern, 32×32+ | Base + shadow + highlight |
| **Dithered shading** | Retro texture, limited palette | Bayer pattern for smooth gradients |
| **Cel shading** | Clean modern style | Hard shadow edges, flat color regions |
| **Selective outline** | Any style | Dark outline on light areas, light on dark |

**Shading direction** (top-right light, bottom-left shadow):
```
Highlight (top-right edges)
    ╲
     ┌──────┐
     │ BASE │
     │      │
     └──────┘
              ╲
        Shadow (bottom-left edges)
```

### Per-Sprite Color Budget

| Style | Max Colors (excl. transparency) |
|---|---|
| NES Classic | 3 |
| Minimalist | 3 |
| SNES Retro | 15 |
| Modern Pixel | 31 |
| Dense Detail | 47 |
| High-Res Pixel | 95 |

---

## 🧱 Tile Generation Standards (MANDATORY)

> Tiles are the most common asset type and the easiest to make look "fake". ALL 9 rules must be satisfied for EVERY tile.

### 1. Canvas & Format
- **Default size**: match project canvas (16×16 / 32×32 / 64×64)
- **Format**: RGB (no transparency for ground tiles), RGBA for overlays
- **Palette**: Strict quantization to declared palette

### 2. NO Obvious Geometric Patterns ⛔
The #1 cause of "fake-looking" tiles. Forbidden in repeatable terrain:

| ❌ Anti-pattern | ✅ Replace with |
|---|---|
| Centered cross / star / plus | Random off-center features |
| 4 equal quadrants | Voronoi 8-15 irregular cells |
| Regular sine waves | Low-frequency value noise |
| Horizontal stripe layers | Diagonal/random color blobs |
| Symmetric corner motifs | Single asymmetric accent |
| Straight diagonal cracks | Random walk segments |

### 3. Multi-Tier Color Distribution
Each pixel sampled by probability:
- **70%** main color (palette base)
- **15%** dark accent (-1 palette step)
- **10%** light accent (+1 palette step)
- **5%** emphasis color (rare highlight/feature)

### 4. Low-Frequency Value Noise (Required for natural tiles)
Use value noise with cosine interpolation for natural color variation:
```python
import math, random
def cos_lerp(a, b, t):
    f = (1 - math.cos(t * math.pi)) / 2
    return a * (1 - f) + b * f

nodes = [[random.uniform(-1, 1) for _ in range(gw)] for _ in range(gh)]
# CRITICAL: wrap edges for seamless tiling
for row in nodes: row[gw-1] = row[0]
nodes[gh-1] = list(nodes[0])
# Cosine-lerp at each pixel for smooth noise
```
**Recommended scales**: Main blob 8-16px per node, detail 3-6px per node, combine 2 octaves.

### 5. Seamless Tiling (4-Edge Wrap) ⛔
Tiles MUST repeat without visible seams:
- Use modulo coordinates: `img.putpixel((x % W, y % H), color)`
- Wrap noise nodes: last row/col equals first
- **Test**: Place 2×2 instances side-by-side; no visible borders

### 6. Sparse Feature Points (≤1% of pixels)
Cracks, veins, moss, droplets:
- Random-walk paths for cracks (short, never straight)
- Scattered points (not clustered, not aligned)
- Total feature pixels ≤1% of canvas area

### 7. Low-Noise Visual Coherence
Terrain tiles must feel calm and continuous:
- **No salt-and-pepper noise** or snow-like white speckles
- **No white/near-white** for ground tiles (use warm ochre, muted gray instead)
- **Prefer broad color regions** over per-pixel randomness
- **Keep hard pixel edges**; do not blur or anti-alias

### 8. Edge Color Continuity
Edges within ±1 palette step of interior:
- ❌ Black border around tile (creates grid effect when tiled)
- ❌ Drastically different color in 1-pixel border
- ✅ Same color distribution on edges as interior

### 9. Mandatory Tile Validation
Before declaring done:
- [ ] 2×2 grid → no visible seams
- [ ] Adjacent tiles → color transition feels natural
- [ ] No symmetric features (rotate 90° / flip → looks different)
- [ ] Quantized to exact palette
- [ ] Feature density ≤1%
- [ ] No visible white speckle noise at game scale

---

## Sprite Templates

### Character Sprites

| Template | Facing | Actions | Frames/Action | Recommended Size |
|---|---|---|---|---|
| `character_simple` | side-only | idle, walk | 3-4 | 16×16, 32×32 |
| `character_4dir` | 4-dir | walk | 4 per direction | 32×32, 64×64 |
| `character_rpg` | 4-dir | idle, walk, attack, hurt, die | 3-6 per action | 32×32, 64×64 |
| `character_platformer` | side-only | idle, run, jump, attack, hurt | 3-6 per action | 32×32, 64×64 |
| `character_full` | 4-dir | idle, walk, run, jump, fall, attack, hurt, die, cast | 3-8 per action | 64×64, 128×128 |

### Common Actions & Frame Counts

| Action | Frames | FPS | Description |
|---|---|---|---|
| `idle` | 2-4 | 6-8 | Standing breathing / subtle motion |
| `walk` | 4-6 | 8-12 | Slow-paced walking cycle |
| `run` | 6-8 | 12-16 | Fast running cycle |
| `jump` | 4-6 | 12-16 | Jump ascent + peak |
| `fall` | 2-4 | 12-16 | Falling / descent |
| `attack` | 4-6 | 12-16 | Melee / ranged attack |
| `hurt` | 2-3 | 8-12 | Taking damage reaction |
| `die` | 4-6 | 6-10 | Death animation |
| `cast` | 4-6 | 8-12 | Magic / skill casting |
| `interact` | 2-4 | 8-12 | Opening chest / picking up |
| `climb` | 4-6 | 8-12 | Ladder / wall climbing |
| `crouch` | 2-3 | 8-12 | Crouching / sneaking |
| `roll` | 4-6 | 12-16 | Dodge roll |
| `swim` | 4-6 | 8-12 | Swimming cycle |

**Frame naming**: `<asset>_<action>_<frame>.png` (e.g., `player_idle_0.png`, `player_walk_3.png`)

### Other Asset Templates

| Category | Templates |
|---|---|
| **Tiles** | `tile_basic` (single), `tile_autotile_9` (9-slice), `tile_autotile_47` (bitmask), `tile_animated` (N frames) |
| **Items** | `item_single` (1 icon), `item_animated` (spinning coin, floating potion, 4-8 frames) |
| **UI** | `ui_button_3state` (normal/hover/pressed), `ui_9slice` (scalable panel), `ui_bar` (health/mana) |
| **Effects** | `effect_burst` (one-shot, 4-8 frames), `effect_loop` (fire/smoke/aura, 4-8 frames) |
| **Backgrounds** | `bg_parallax_layer` (wide, horizontally tileable), `bg_full` (full screen 16:9 or 4:3) |

---

## Banned Features Blacklist

The following are FORBIDDEN in generated pixel art:

| Banned Feature | Reason |
|---|---|
| Anti-aliasing | Breaks pixel-perfect aesthetic |
| Sub-pixel rendering | Not possible at pixel scale |
| Gradient fills | Use dithering instead |
| Partial opacity (1-254 alpha) | Pixel art = fully opaque or fully transparent |
| Blur effects | Breaks crisp edges |
| Bezier curves | Pixels are axis-aligned |
| Vector scaling artifacts | Must be pixel-perfect at declared size |
| Colors outside declared palette | Violates palette consistency |

---

## Decision Tree

```
User task → What type of pixel art?
    ├─ Single sprite/icon (≤64×64)
    │     1. Select style preset (see table above)
    │     2. Read palettes/*.json to pick a color palette
    │     3. Create the sprite as a PNG at the target resolution
    │     4. Run: python scripts/quality_audit.py <image> --json
    │     5. Fix any reported issues, re-audit until clean
    │
    ├─ Character sprite sheet (walk cycle, attack, etc.)
    │     1. Select style preset and character template
    │     2. Read references/sprite_conventions.md + references/animation_principles.md
    │     3. Create individual frames as separate PNGs
    │     4. Run: python scripts/atlas_pack.py --frames-dir <dir> --output sheet.png --cols 4 --json
    │     5. Run: python scripts/quality_audit.py sheet.png --json
    │     6. Optional: python scripts/gif_export.py --sheet sheet.png --frame-width W --frame-height H --fps 8 --output preview.gif --json
    │
    ├─ 8-way character sheet (from 5 directions)
    │     1. Draw 5 directions: S, SW, W, NW, N
    │     2. Run: python scripts/sprite_mirror.py --input-dir ./east_frames/ --output-dir ./west_frames/ --axis horizontal --json
    │     3. Pack all directions into atlas
    │
    ├─ Tileset / Autotile map
    │     1. Read the Tile Generation Standards section above (9 mandatory rules)
    │     2. Read references/tileset_rules.md for grid and autotile conventions
    │     3. Create tiles following the 9 rules
    │     4. Run: python scripts/quality_audit.py <tileset> --json
    │     5. Preview: open templates/tilemap_preview.html
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

---

## Palette References

Palette JSON files live in `palettes/`. Each file contains `name`, `colors` array (hex strings), and `max_colors`:

Available palettes: `pico-8.json` (16), `gameboy.json` (4), `nes.json` (56), `snes.json` (64), `endesga-32.json` (32), `resurrect-64.json` (64), `sweetie-16.json` (16), `db32.json` (32), `cga.json` (4), `commodore-64.json` (16), `lospec-500.json` (32)

**Palette selection guide**:
| Palette | Colors | Best For |
|---|---|---|
| PICO-8 | 16 | Game jams, tiny games, fantasy console |
| Sweetie-16 | 16 | Cute/chibi, pastel worlds |
| GameBoy | 4 | Monochrome retro |
| DB32 | 32 | General indie (most versatile) |
| Endesga-32 | 32 | Vibrant colorful worlds |
| Resurrect-64 | 64 | Complex detailed environments |
| NES | 56 | Classic 8-bit console hardware |
| SNES | 64 | 16-bit era games |
| CGA | 4 | PC retro |
| Commodore-64 | 16 | C64-style games |

## Template Reference

The `templates/` directory contains interactive HTML tools:

- `templates/sprite_sheet.html` — Sprite sheet viewer with animation playback, zoom, frame navigation
- `templates/tilemap_preview.html` — Tilemap painter: select tiles, paint on grid, random fill
- `templates/palette_viewer.html` — Palette comparison tool with swatch display and color picker

## Further Reading

- [Sprite Conventions](references/sprite_conventions.md) — Frame sizes, animation timing, directional layouts
- [Animation Principles](references/animation_principles.md) — 12 Disney principles applied to pixel art
- [Tileset Rules](references/tileset_rules.md) — Grid sizes, Wang autotile bitmasks, terrain transitions
- [Isometric Guide](references/isometric_guide.md) — 2:1 projection, tile stacking, depth sorting
- [Color Theory](references/color_theory.md) — Palette design, contrast ratios, hue ramps
- [UI Elements](references/ui_elements.md) — Health bars, buttons, dialog boxes, 9-slice panels
- [Particle Effects](references/particle_effects.md) — Explosions, fire, smoke, sparkles, magic VFX

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Blurry after resize | Used bilinear/bicubic | Use `sprite_resize.py` (nearest-neighbor only) |
| Visible seams in tileset | Tiles don't wrap | Follow Tile Generation Standards rule 5 |
| Colors look wrong in-game | Exported as RGBA | Use `export_indexed.py` |
| Animation looks choppy | Not enough frames | Min 4 frames for walk, read animation_principles.md |
| Sprite hard to see | No outline, low contrast | Use `outline_generator.py` |
| Too many colors | No palette enforcement | Run `palette_remap.py` before export |
| Tiles look fake | Geometric patterns | Follow Tile Generation Standards rule 2 |
| Colors drift between assets | Memory drift | Re-read palette before EACH asset |

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

### RPG Maker MV/MZ
- Tile size: 48×48 (RPG Maker standard)
- Sprite sheets: 12 frames per character (3 frames × 4 directions)
- Use `atlas_pack.py` with `--cols 3` for RPG Maker format
