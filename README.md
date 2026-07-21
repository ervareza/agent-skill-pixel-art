# 🎮 Pixel Art — AI Agent Skill

An AI agent skill for creating, auditing, exporting, and managing 2D pixel art game assets.

**13 CLI tools** · **11 palettes** · **3 interactive templates** · **7 reference guides**

Compatible with **Antigravity IDE**, **Claude Code**, **Codex CLI**, and any agent that supports the skills folder convention.

---

## What This Is

This is a **skill** — a folder of instructions, scripts, palettes, and reference documents that AI agents load dynamically to become expert pixel art assistants. When installed, your AI agent can:

- Create game-ready sprites, tilesets, character walk cycles, UI elements, and particle effects
- Enforce strict pixel art rules (no anti-aliasing, palette limits, grid alignment)
- Audit existing pixel art for quality issues and fix them
- Pack sprite frames into atlas sheets with JSON metadata for game engines
- Remap colors to target palettes (PICO-8, GameBoy, NES, SNES, CGA, etc.)
- Export animated GIFs, resize with nearest-neighbor, add outlines
- Generate procedural noise textures and dithered gradients

---

## Installation

### Antigravity IDE (Google Gemini)

```bash
cp -r skills/pixel-art ~/.gemini/config/skills/pixel-art
```

Or add to your workspace `.agents/skills/` directory:

```bash
cp -r skills/pixel-art .agents/skills/pixel-art
```

### Claude Code

```bash
# Using the built-in skills command
claude skills add ./skills/pixel-art

# Or manual install
cp -r skills/pixel-art ~/.claude/skills/pixel-art
```

### Codex CLI (OpenAI)

```bash
cp -r skills/pixel-art ~/.codex/skills/pixel-art
```

### Any Agent (Generic)

Copy the `skills/pixel-art/` folder into your agent's skills directory. The agent will read `SKILL.md` as the entry point and discover all scripts, palettes, and references automatically.

### Dependencies

The scripts require Python 3.8+ and Pillow:

```bash
pip install -r skills/pixel-art/requirements.txt

# Or directly:
pip install "Pillow>=9.0.0"
```

---

## Structure

```
skills/pixel-art/
├── SKILL.md                          # Agent entry point (YAML frontmatter + decision tree)
├── LICENSE.txt                       # MIT license
├── requirements.txt                  # Python dependencies
│
├── scripts/                          # 13 CLI tools (all support --help and --json)
│   ├── init_workspace.py             # Create project directories + manifest
│   ├── quality_audit.py              # Audit single PNG for pixel art issues
│   ├── batch_audit.py                # Audit ALL PNGs in a directory
│   ├── palette_remap.py              # Remap colors to target palette
│   ├── palette_extract.py            # Extract palette from existing image
│   ├── atlas_pack.py                 # Pack frames into sprite sheet + JSON
│   ├── export_indexed.py             # Convert RGBA → indexed PNG
│   ├── sprite_resize.py              # Nearest-neighbor resize (2x/3x/4x/8x)
│   ├── sprite_mirror.py              # Mirror horizontal/vertical (single/batch)
│   ├── gif_export.py                 # Sprite sheet or frames → animated GIF
│   ├── outline_generator.py          # Add 1px outline around sprite
│   ├── dither.py                     # Ordered Bayer matrix dithering
│   └── noise_generator.py            # Procedural value noise textures
│
├── palettes/                         # 11 palette JSON files
│   ├── pico-8.json                   # PICO-8 fantasy console (16 colors)
│   ├── gameboy.json                  # Game Boy DMG-01 (4 colors)
│   ├── nes.json                      # NES PPU (56 colors)
│   ├── snes.json                     # Super Nintendo (64 colors)
│   ├── endesga-32.json               # ENDESGA 32 (32 colors)
│   ├── resurrect-64.json             # Resurrect 64 (64 colors)
│   ├── sweetie-16.json               # Sweetie 16 game jam palette (16 colors)
│   ├── db32.json                     # DawnBringer 32 (32 colors)
│   ├── cga.json                      # IBM CGA DOS palette (16 colors)
│   └── commodore-64.json             # Commodore 64 (16 colors)
│
├── templates/                        # Interactive HTML tools
│   ├── sprite_sheet.html             # Sprite sheet viewer with animation playback
│   ├── tilemap_preview.html          # Tilemap painter with tile selection
│   └── palette_viewer.html           # Palette comparison and swatch viewer
│
└── references/                       # 7 knowledge base documents
    ├── sprite_conventions.md          # Frame sizes, animation timing, layouts
    ├── animation_principles.md        # 12 Disney principles for pixel art
    ├── tileset_rules.md              # Grid sizes, Wang autotile, terrain
    ├── isometric_guide.md            # 2:1 projection, stacking, depth sorting
    ├── color_theory.md               # Palette design, contrast, hue ramps
    ├── ui_elements.md                # Health bars, buttons, dialogs, 9-slice
    └── particle_effects.md           # Explosions, fire, smoke, sparkles
```

---

## Script Reference

Every script supports `--help` for usage info and `--json` for machine-readable output.

| Script | Purpose | Key Flags |
|---|---|---|
| `init_workspace.py` | Scaffold project directories | `--dir`, `--name` |
| `quality_audit.py` | Audit one PNG for issues | `--image`, `--grid`, `--max-colors` |
| `batch_audit.py` | Audit all PNGs in a folder | `--dir`, `--grid`, `--max-colors` |
| `palette_remap.py` | Remap to target palette | `--image`, `--palette`, `--output` |
| `palette_extract.py` | Extract palette from image | `--image`, `--max-colors`, `--output` |
| `atlas_pack.py` | Pack frames into sheet | `--frames-dir`, `--output`, `--cols`, `--padding` |
| `export_indexed.py` | Convert to indexed PNG | `--input`, `--output`, `--max-colors` |
| `sprite_resize.py` | Nearest-neighbor resize | `--input`, `--output`, `--scale` |
| `sprite_mirror.py` | Flip horizontal/vertical | `--input`/`--input-dir`, `--axis` |
| `gif_export.py` | Frames → animated GIF | `--sheet`/`--frames-dir`, `--fps`, `--output` |
| `outline_generator.py` | Add 1px outline | `--input`, `--output`, `--color` |
| `dither.py` | Bayer dithered gradient | `--width`, `--height`, `--color1`, `--color2`, `--matrix` |
| `noise_generator.py` | Procedural noise texture | `--width`, `--height`, `--scale`, `--palette` |

---

## Usage Examples

Five completely different game development scenarios, tested end-to-end. Every image shown is the **actual output** generated by the tools.

### Example 1: RPG Forest Tileset (32×32, Sweetie-16 palette)

Create seamless terrain tiles for an RPG overworld: grass, dirt path, water, stone wall, and flower grass.

Each tile uses **value noise with cosine interpolation** and **multi-tier color distribution** (70/15/10/5%) following the Tile Generation Standards.

```bash
python scripts/quality_audit.py --image tile_grass.png --grid 32 --max-colors 16 --json
# → all 5 tiles pass audit
```

#### 📸 Tile Gallery (4× zoom)

| Grass | Dirt | Water | Stone | Flowers |
|---|---|---|---|---|
| <img src="examples/uc1_rpg_forest_tileset/tile_grass_4x.png" width="96"> | <img src="examples/uc1_rpg_forest_tileset/tile_dirt_4x.png" width="96"> | <img src="examples/uc1_rpg_forest_tileset/tile_water_4x.png" width="96"> | <img src="examples/uc1_rpg_forest_tileset/tile_stone_4x.png" width="96"> | <img src="examples/uc1_rpg_forest_tileset/tile_flower_4x.png" width="96"> |

**Seamless tiling test** — 2×2 grass tiles (4× zoom):

<img src="examples/uc1_rpg_forest_tileset/grass_tiled_2x2_4x.png" width="256">

**Tools used:** `noise_generator` (technique) → `quality_audit` → `batch_audit`

---

### Example 2: Platformer Hero (32×32, 4-frame walk cycle)

A fully animated knight character with **3-tone shading** (base + shadow + highlight), consistent top-right lighting, outlined sword, and proper walk animation with leg offsets per frame.

```bash
python scripts/atlas_pack.py --frames-dir ./frames/ --output hero_walk_sheet.png --cols 4 --json
python scripts/gif_export.py --sheet hero_walk_sheet.png --frame-width 32 --frame-height 32 --fps 8 --output hero_walk.gif --json
```

#### 📸 Walk Frames (4× zoom)

| Frame 0 | Frame 1 | Frame 2 | Frame 3 |
|---|---|---|---|
| <img src="examples/uc2_platformer_hero/hero_walk_0_4x.png" width="96"> | <img src="examples/uc2_platformer_hero/hero_walk_1_4x.png" width="96"> | <img src="examples/uc2_platformer_hero/hero_walk_2_4x.png" width="96"> | <img src="examples/uc2_platformer_hero/hero_walk_3_4x.png" width="96"> |

**Animated walk cycle** (4× zoom):

<img src="examples/uc2_platformer_hero/hero_walk_4x.gif" width="96">

**Tools used:** `atlas_pack` → `gif_export` → `quality_audit`

---

### Example 3: Fantasy Item Set (16×16, PICO-8 palette)

Five game items drawn at the classic 16×16 NES size with the PICO-8 palette: iron sword, knight's shield, health potion, golden key, and magic gem. Each uses shading to convey material (metal highlight on sword, glass transparency on potion, gem sparkle).

```bash
python scripts/atlas_pack.py --frames-dir ./items_dir/ --output item_sheet.png --cols 5 --json
python scripts/batch_audit.py --dir ./items_dir/ --grid 16 --max-colors 16 --json
# → all 5 items pass
```

#### 📸 Item Gallery (4× zoom)

| Sword | Shield | Potion | Key | Gem |
|---|---|---|---|---|
| <img src="examples/uc3_fantasy_items/sword_4x.png" width="64"> | <img src="examples/uc3_fantasy_items/shield_4x.png" width="64"> | <img src="examples/uc3_fantasy_items/potion_4x.png" width="64"> | <img src="examples/uc3_fantasy_items/key_4x.png" width="64"> | <img src="examples/uc3_fantasy_items/gem_4x.png" width="64"> |

**Item sheet** (4× zoom):

<img src="examples/uc3_fantasy_items/item_sheet_4x.png" width="320">

**Tools used:** `atlas_pack` → `batch_audit` → `quality_audit`

---

### Example 4: UI Elements — Buttons + Health Bar (Endesga-32 palette)

Game UI with 3-state button (normal/hover/pressed with color shift) and health bar at 4 fill levels. The button includes pixel font "PLAY" text. The health bar uses 3-tone green fill with dark teal background.

```bash
python scripts/batch_audit.py --dir ./ui/ --grid 8 --max-colors 32 --json
```

#### 📸 Button States (4× zoom)

| Normal | Hover | Pressed |
|---|---|---|
| <img src="examples/uc4_ui_elements/button_normal_4x.png" width="192"> | <img src="examples/uc4_ui_elements/button_hover_4x.png" width="192"> | <img src="examples/uc4_ui_elements/button_pressed_4x.png" width="192"> |

#### 📸 Health Bar States (4× zoom)

| 100% | 75% | 50% | 25% |
|---|---|---|---|
| <img src="examples/uc4_ui_elements/health_full_4x.png" width="192"> | <img src="examples/uc4_ui_elements/health_75_4x.png" width="192"> | <img src="examples/uc4_ui_elements/health_50_4x.png" width="192"> | <img src="examples/uc4_ui_elements/health_25_4x.png" width="192"> |

**Tools used:** `batch_audit` → `quality_audit`

---

### Example 5: Explosion VFX (32×32, 6-frame burst, DB32 palette)

A one-shot explosion effect with 6 animation phases: **spark → expand → peak → smoke → fade → dissipate**. Uses DB32 palette with warm-to-cool color progression (yellow → orange → brown → gray → transparent).

```bash
python scripts/atlas_pack.py --frames-dir ./frames/ --output explosion_sheet.png --cols 6 --json
python scripts/gif_export.py --frames-dir ./frames/ --fps 12 --output explosion.gif --json
python scripts/batch_audit.py --dir ./frames/ --grid 32 --max-colors 32 --json
# → all 6 frames pass
```

#### 📸 Explosion Frames (4× zoom)

| Frame 0 (Spark) | Frame 1 (Expand) | Frame 2 (Peak) | Frame 3 (Smoke) | Frame 4 (Fade) | Frame 5 (Dissipate) |
|---|---|---|---|---|---|
| <img src="examples/uc5_explosion_vfx/explosion_0_4x.png" width="96"> | <img src="examples/uc5_explosion_vfx/explosion_1_4x.png" width="96"> | <img src="examples/uc5_explosion_vfx/explosion_2_4x.png" width="96"> | <img src="examples/uc5_explosion_vfx/explosion_3_4x.png" width="96"> | <img src="examples/uc5_explosion_vfx/explosion_4_4x.png" width="96"> | <img src="examples/uc5_explosion_vfx/explosion_5_4x.png" width="96"> |

**Sprite sheet** (4× zoom):

<img src="examples/uc5_explosion_vfx/explosion_sheet_4x.png" width="768">

**Animated explosion** (4× zoom):

<img src="examples/uc5_explosion_vfx/explosion_4x.gif" width="96">

**Tools used:** `atlas_pack` → `gif_export` → `batch_audit`


---

## Available Palettes

| Palette | Colors | Era / Style |
|---|---|---|
| `pico-8.json` | 16 | Fantasy console, vibrant |
| `gameboy.json` | 4 | Game Boy DMG-01, green monochrome |
| `nes.json` | 56 | NES PPU NTSC hardware |
| `snes.json` | 64 | Super Nintendo curated |
| `endesga-32.json` | 32 | ENDESGA modern pixel art |
| `resurrect-64.json` | 64 | Resurrect high-color |
| `sweetie-16.json` | 16 | Game jam favorite, warm |
| `db32.json` | 32 | DawnBringer classic indie |
| `cga.json` | 16 | IBM CGA DOS retro |
| `commodore-64.json` | 16 | C64 home computer |

All palettes follow the same JSON schema:

```json
{
  "name": "pico-8",
  "max_colors": 16,
  "colors": ["#000000", "#1D2B53", "..."]
}
```

You can create custom palettes or extract them from existing art with `palette_extract.py`.

---

## Interactive Templates

Open these HTML files in any browser. No server needed.

| Template | What It Does |
|---|---|
| `sprite_sheet.html` | Load a sprite sheet, set frame size, play animation, zoom with pixelated rendering |
| `tilemap_preview.html` | Load a tileset, select tiles, paint on a map grid, random fill, export |
| `palette_viewer.html` | View palettes side-by-side, click swatches to compare colors, load custom JSONs |

---

## Reference Knowledge Base

These markdown documents teach the agent (and you) domain-specific pixel art knowledge:

| Document | Topics Covered |
|---|---|
| `sprite_conventions.md` | Frame sizes, animation timing, 4/8-directional layouts |
| `animation_principles.md` | 12 Disney principles adapted for pixel art constraints |
| `tileset_rules.md` | Grid sizes, Wang blob autotile bitmasks, terrain transitions |
| `isometric_guide.md` | 2:1 projection, diamond tiles, depth sorting, stacking |
| `color_theory.md` | Hue ramps, contrast ratios, palette design for pixel art |
| `ui_elements.md` | 9-slice panels, health bars, buttons, dialogs, inventory |
| `particle_effects.md` | Explosions, fire, smoke, sparkles, spawn patterns, timing |

---

## Game Engine Integration

### Godot 4

```gdscript
# Import settings: Filter = Nearest, Sprite Mode = Region
# Use atlas_pack.py JSON metadata for AnimatedSprite2D:
var sheet_data = JSON.parse_string(FileAccess.open("knight_walk.json", FileAccess.READ).get_as_text())
for frame in sheet_data["frames"]:
    # frame.x, frame.y, frame.w, frame.h → AtlasTexture region
    pass
```

### Unity

1. Set texture import: **Filter Mode = Point (no filter)**, **Sprite Mode = Multiple**
2. Slice with Grid mode using your frame dimensions
3. Set **Pixels Per Unit** to match tile size (16 for 16×16)
4. Use the `atlas_pack.py` JSON for programmatic slicing

### Defold

1. Set texture sampling to **Nearest**
2. Import atlas JSON as tile source coordinates
3. Use `go.property()` for runtime palette switching

---

## Pixel Art Rules (Enforced by This Skill)

These rules are embedded in `SKILL.md` and enforced by `quality_audit.py`:

1. **Zero anti-aliasing** — Every pixel is fully opaque or fully transparent. No semi-transparency.
2. **Strict palette limits** — Never exceed the target palette color count.
3. **Grid-snap everything** — Dimensions must be exact multiples of the base grid (8, 16, 32).
4. **No orphan pixels** — Isolated single pixels with no neighbors are usually mistakes.
5. **Nearest-neighbor only** — Never use bilinear/bicubic/Lanczos when resizing.
6. **Export as indexed PNG** — Final assets should be indexed-color, not RGBA.
7. **Mirror to save memory** — Draw 5 directions, mirror for the other 3.
8. **Consistent lighting** — Top-right light source. Always.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT — see [LICENSE](skills/pixel-art/LICENSE.txt).
