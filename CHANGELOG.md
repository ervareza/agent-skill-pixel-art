# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [v4.0.0] - 2025-07-22

### Changed
- **Complete rewrite** following Anthropic official skill conventions (studied from `anthropics/skills` repo)
- Renamed skill from `chromamatrix-core` to `pixel-art` (kebab-case, like official skills)
- Renamed all directories to standard names: `scripts/`, `palettes/`, `templates/`, `references/` (matching `anthropics/skills` patterns)
- Rewrote `SKILL.md` with proper YAML frontmatter (`name`, `description`, `license`), decision tree, gotchas section, and reference links
- Rewrote `README.md` to follow Anthropic's clean documentation style
- All Python scripts now follow the Anthropic CLI pattern: `argparse`, `--help`, `--json`, clean exit codes

### Added
- `scripts/init_workspace.py` — workspace directory initializer
- `scripts/quality_audit.py` — pixel art quality auditor (AA, orphans, palette, grid)
- `scripts/palette_remap.py` — color remapper using Euclidean RGB distance
- `scripts/atlas_pack.py` — sprite frame packer with JSON metadata
- `scripts/export_indexed.py` — RGBA to indexed 8-bit PNG converter
- `palettes/pico-8.json` — PICO-8 16-color palette
- `palettes/gameboy.json` — Game Boy 4-color palette
- `palettes/nes.json` — NES 54-color hardware palette
- `palettes/endesga-32.json` — ENDESGA 32-color palette
- `palettes/resurrect-64.json` — Resurrect 64-color palette
- `templates/sprite_sheet.html` — interactive sprite sheet viewer
- `references/sprite_conventions.md` — frame sizes, animations, directional layouts
- `references/tileset_rules.md` — grid sizes, Wang autotile, terrain transitions
- `references/color_theory.md` — hue ramps, contrast, dithering, palette design
- `LICENSE.txt` inside skill folder

### Removed
- `chromamatrix-core/` directory and all contents
- `ManifestVault/`, `PixelProtocols/`, `RenderOrchestrators/`, `RasterBlueprints/`, `SynthesisFlow/` — replaced with standard naming
- `CONTRIBUTING.md`, `DEVELOPER_GUIDE.md`, `SECURITY.md`, `.env.example`, `index.html` — unnecessary for a skill package

## [v3.0.0] - 2025-07-21

### Added
- Initial ChromaMatrix Core rebranding (superseded by v4.0.0)
