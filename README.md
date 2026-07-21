# Pixel Art Skill

An AI agent skill for creating, auditing, and exporting 2D pixel art assets. Compatible with Claude Code, Codex CLI, and Antigravity IDE.

## What This Is

This is a **skill** — a folder of instructions, scripts, and resources that AI agents load dynamically to improve their performance on pixel art tasks. The skill teaches agents how to:

- Create game-ready sprites, tilesets, character sheets, and UI elements
- Enforce strict pixel art rules (no anti-aliasing, palette limits, grid alignment)
- Audit existing pixel art for quality issues
- Pack sprite frames into atlas sheets with JSON metadata
- Remap colors to target palettes (PICO-8, GameBoy, NES, etc.)

## Installation

### Claude Code
```bash
claude skills add ./skills/pixel-art
```

### Manual Installation
Copy the `skills/pixel-art/` folder into your agent's skills directory:
```bash
cp -r skills/pixel-art ~/.claude/skills/pixel-art
# or for Antigravity IDE:
cp -r skills/pixel-art ~/.gemini/config/skills/pixel-art
```

### Dependencies
The scripts require Python 3.8+ and Pillow:
```bash
pip install Pillow
```

## Structure

```
skills/pixel-art/
├── SKILL.md                          # Main instruction manifest
├── LICENSE.txt                       # MIT license
├── scripts/
│   ├── init_workspace.py             # Create project directories + manifest
│   ├── quality_audit.py              # Audit PNG for pixel art quality issues
│   ├── palette_remap.py              # Remap colors to target palette
│   ├── atlas_pack.py                 # Pack frames into sprite sheet
│   └── export_indexed.py             # Convert to indexed 8-bit PNG
├── palettes/
│   ├── pico-8.json                   # PICO-8 fantasy console (16 colors)
│   ├── gameboy.json                  # Game Boy DMG-01 (4 colors)
│   ├── nes.json                      # NES hardware palette (54 colors)
│   ├── endesga-32.json               # ENDESGA 32 (32 colors)
│   └── resurrect-64.json             # Resurrect 64 (64 colors)
├── templates/
│   └── sprite_sheet.html             # Interactive sprite sheet viewer
└── references/
    ├── sprite_conventions.md          # Frame sizes, animations, directional layouts
    ├── tileset_rules.md               # Grid sizes, Wang autotile, terrain transitions
    └── color_theory.md                # Hue ramps, contrast, dithering, palette design
```

## Quick Start

```bash
# Initialize a workspace
python skills/pixel-art/scripts/init_workspace.py --dir ./my-game --name hero --json

# Audit an existing sprite
python skills/pixel-art/scripts/quality_audit.py --image hero.png --grid 16 --max-colors 16 --json

# Remap colors to PICO-8 palette
python skills/pixel-art/scripts/palette_remap.py --image hero.png --palette skills/pixel-art/palettes/pico-8.json --output hero_pico8.png --json

# Pack frames into a sprite sheet
python skills/pixel-art/scripts/atlas_pack.py --frames-dir ./frames --output sheet.png --cols 4 --json

# Export as indexed PNG
python skills/pixel-art/scripts/export_indexed.py --input sheet.png --output sheet_indexed.png --max-colors 16 --json
```

## License

MIT — see [LICENSE.txt](skills/pixel-art/LICENSE.txt)
