# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [v4.1.0] - 2025-07-22

### Added
- **8 new CLI scripts:** `sprite_resize.py`, `gif_export.py`, `palette_extract.py`, `batch_audit.py`, `sprite_mirror.py`, `outline_generator.py`, `dither.py`, `noise_generator.py`
- **6 new palettes:** `sweetie-16.json`, `db32.json`, `cga.json`, `commodore-64.json`, `snes.json`
- **2 new HTML templates:** `tilemap_preview.html` (interactive tilemap painter), `palette_viewer.html` (palette comparison tool)
- **4 new reference docs:** `particle_effects.md`, `ui_elements.md`, `isometric_guide.md`, `animation_principles.md`
- `requirements.txt` for pip install

### Changed
- **SKILL.md** expanded: 15-branch decision tree, troubleshooting table, engine-specific tips (Godot 4, Unity, Defold)
- **README.md** completely rewritten: 5 real-world usage examples, complete script reference, palette table, engine integration guides, installation for Antigravity/Claude/Codex

### Fixed
- `tilemap_preview.html` was referenced in SKILL.md but didn't exist — now implemented
- Pillow deprecation warnings (`getdata()` → `px.load()`)
- RGBA quantization bug in `export_indexed.py`
- NES palette `max_colors` mismatch (was 54, actual 56)

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
