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

These are 5 real-world use cases, tested end-to-end with actual PNG data. Every command shown below was run and verified.

### Example 1: Character Walk Cycle → Atlas → GIF → Game Export

Create a knight character with a 4-frame walk cycle, pack into a sprite sheet, export an animated GIF preview, and resize for game use.

```bash
# 1. Set up workspace
python scripts/init_workspace.py --dir ./knight_project --name knight_hero --json
# → Creates sprites/, tilesets/, frames/, sheets/, exports/ + manifest

# 2. Create frames (your pixel art goes into frames/)
# ... create walk_00.png through walk_03.png at 16×16 ...

# 3. Audit each frame for pixel art quality
python scripts/quality_audit.py --image frames/walk_00.png --grid 16 --max-colors 16 --json
# → {"status": "pass", "antialiasing": {"clean": true}, "orphan_pixels": {"clean": true}, ...}

# 4. Pack all frames into a sprite sheet
python scripts/atlas_pack.py --frames-dir ./frames/ --output sheets/knight_walk.png --cols 4 --json
# → {"status": "ok", "frame_count": 4, "sheet_size": [64, 16]}
# Also creates knight_walk.json with frame coordinates for game engines

# 5. Export animated GIF for preview
python scripts/gif_export.py --sheet sheets/knight_walk.png --frame-width 16 --frame-height 16 --fps 8 --output exports/knight_walk.gif --json
# → {"status": "ok", "frame_count": 4, "fps": 8, "duration_ms": 125}

# 6. Resize 4× for high-DPI displays
python scripts/sprite_resize.py --input sheets/knight_walk.png --output exports/knight_walk_4x.png --scale 4 --json
# → {"status": "ok", "original_size": [64, 16], "new_size": [256, 64]}
```

**Tools used:** `init_workspace`, `quality_audit`, `atlas_pack`, `gif_export`, `sprite_resize`

---

### Example 2: Tileset → GameBoy Palette Remap → Indexed Export

Create a terrain tileset, audit for quality, remap to the classic GameBoy 4-color palette, and export as indexed PNG for the target platform.

```bash
# 1. Audit the tileset
python scripts/quality_audit.py --image tileset.png --grid 16 --max-colors 16 --json
# → {"status": "pass", "palette": {"unique_colors": 10, "max_allowed": 16, "clean": true}, "grid_alignment": {"aligned": true}}

# 2. Remap to GameBoy palette
python scripts/palette_remap.py --image tileset.png --palette palettes/gameboy.json --output tileset_gb.png --json
# → {"status": "ok", "palette": "gameboy", "palette_colors": 4}

# 3. Export as indexed PNG (tiny file size!)
python scripts/export_indexed.py --input tileset_gb.png --output tileset_gb_indexed.png --max-colors 4 --json
# → {"status": "ok", "indexed_colors": 4, "file_size_bytes": 133}
```

**Tools used:** `quality_audit`, `palette_remap`, `export_indexed`

---

### Example 3: Extract Palette → Procedural Terrain → Dithered Sky

Extract the color palette from existing character art, use it to generate a procedural terrain noise texture and a dithered sky gradient — everything stays visually cohesive.

```bash
# 1. Extract palette from existing sprite
python scripts/palette_extract.py --image knight_walk_00.png --max-colors 16 --output palettes/custom.json --json
# → {"status": "ok", "total_unique_colors": 6, "color_frequency": [
#     {"color": "#3B5DC9", "pixels": 24, "percent": 38.7},
#     {"color": "#EF7D57", "pixels": 10, "percent": 16.1}, ...
#   ], "saved_to": "palettes/custom.json"}

# 2. Generate terrain noise with extracted palette
python scripts/noise_generator.py --width 64 --height 64 --scale 12 --octaves 3 --seed 777 --palette palettes/custom.json --output terrain.png --json
# → {"status": "ok", "size": [64, 64], "palette": "palettes/custom.json"}

# 3. Generate dithered sky gradient
python scripts/dither.py --width 64 --height 32 --color1 "#29366F" --color2 "#41A6F6" --matrix 4 --output sky.png --json
# → {"status": "ok", "size": [64, 32], "matrix": "4x4"}

# 4. Audit the terrain texture
python scripts/quality_audit.py --image terrain.png --grid 8 --max-colors 16 --json
# → {"status": "pass"}
```

**Tools used:** `palette_extract`, `noise_generator`, `dither`, `quality_audit`

---

### Example 4: Batch QA → Outline → Resize → Palette Remap

Run quality assurance on an entire folder of sprites, add outlines for visibility, resize for game export, and remap to PICO-8 palette.

```bash
# 1. Batch audit all sprites in folder
python scripts/batch_audit.py --dir ./sprites/ --grid 16 --max-colors 16 --json
# → {"status": "pass", "total_files": 4, "passed": 4, "failed": 0,
#    "results": [{"file": "walk_00.png", "status": "pass", "issues": []}, ...]}

# 2. Add dark outline for readability against busy backgrounds
python scripts/outline_generator.py --input sprites/walk_00.png --output outlined/walk_00.png --color "#1A1A2E" --json
# → {"status": "ok", "original_size": [16, 16], "outlined_size": [18, 18], "outline_color": "#1A1A2E"}

# 3. Resize 3× for game display
python scripts/sprite_resize.py --input outlined/walk_00.png --output exports/walk_00_3x.png --scale 3 --json
# → {"status": "ok", "original_size": [18, 18], "new_size": [54, 54]}

# 4. Remap to PICO-8 palette
python scripts/palette_remap.py --image outlined/walk_00.png --palette palettes/pico-8.json --output exports/walk_00_pico8.png --json
# → {"status": "ok", "palette": "pico-8", "palette_colors": 16}
```

**Tools used:** `batch_audit`, `outline_generator`, `sprite_resize`, `palette_remap`

---

### Example 5: 8-Way Character from 5 Directions (Mirror to Save Memory)

Draw only east-facing frames, automatically mirror them to create west-facing frames. Pack both into separate sprite sheets with animated GIF previews.

```bash
# 1. Create east-facing frames (draw once)
# ... create east_00.png through east_03.png ...

# 2. Auto-mirror east → west (saves 50% art time!)
python scripts/sprite_mirror.py --input-dir ./east_frames/ --output-dir ./west_frames/ --axis horizontal --json
# → {"status": "ok", "files_mirrored": 4}

# 3. Pack east sheet
python scripts/atlas_pack.py --frames-dir ./east_frames/ --output east_sheet.png --cols 4 --json
# → {"status": "ok", "frame_count": 4, "sheet_size": [64, 16]}

# 4. Pack west sheet
python scripts/atlas_pack.py --frames-dir ./west_frames/ --output west_sheet.png --cols 4 --json
# → {"status": "ok", "frame_count": 4, "sheet_size": [64, 16]}

# 5. Export GIF previews
python scripts/gif_export.py --frames-dir ./east_frames/ --fps 6 --output east_anim.gif --json
# → {"status": "ok", "frame_count": 4, "fps": 6}

python scripts/gif_export.py --frames-dir ./west_frames/ --fps 6 --output west_anim.gif --json
# → {"status": "ok", "frame_count": 4, "fps": 6}

# 6. Batch audit both directions
python scripts/batch_audit.py --dir ./east_frames/ --grid 16 --max-colors 16 --json
# → {"status": "pass", "total_files": 4, "passed": 4, "failed": 0}

python scripts/batch_audit.py --dir ./west_frames/ --grid 16 --max-colors 16 --json
# → {"status": "pass", "total_files": 4, "passed": 4, "failed": 0}
```

**Tools used:** `sprite_mirror`, `atlas_pack`, `gif_export`, `batch_audit`

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
