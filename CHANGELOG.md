# Changelog

All notable changes to **PixelMatrix Engine** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v2.0.0] - 2026-07-22

### Changed (Breaking Release)
- **Engine Rebranding**: Complete ground-up overhaul and rebranding from legacy architecture to **PixelMatrix Engine** (`v2.0.0`).
- **Total Codebase Purge**: Eradicated all legacy folders, old script runners, obsolete file names, and outdated terminology. Zero legacy traces remain.
- **Architectural Overhaul**: Re-architected engine tools into modern object-oriented Python modules:
  - `MatrixCanvasInitializer` (`canvas_initializer.py`): Workspace setup and contract specification manifests.
  - `PaletteLUTSynthesizer` (`lut_synthesizer.py`): Color palette extraction, Euclidean distance calculations, and LUT remapping.
  - `RasterSpecInspector` (`spec_inspector.py`): Automated quality control inspecting grid alignment, palette bounds, anti-aliasing detection, and orphan pixels.
  - `SpriteAtlasCompiler` (`atlas_compiler.py`): Texture atlas packing and JSON metadata manifest generation.
  - `PixelRasterPostProcessor` (`raster_processor.py`): Color quantization, orphan pixel cleaning, and indexed 8-bit PNG export.

### Added
- **Extended Canvas Presets**: Added 16x16 icon, 32x32 standard sprite, 48x48 isometric axonometric (30° projection angle), 64x64 boss, 128x128 scene element, 256x256 parallax background, and 9-slice HUD frame specs (`specs/grid_canvas_presets.json`).
- **Hardware & Aesthetic Palette LUTs**: Added NES 54-color, GameBoy 4-color DMG-01, PICO-8 16-color, Cyberpunk Neon 16, Synthwave Sunset 16, Dungeon Dark 16, Forest Pastels 16, Master System 64, and custom 24-bit HEX mapping LUTs (`specs/palette_lut_definitions.json`).
- **Sprite Animation & Autotile Matrices**: Added 4-way & 8-way directional character matrices (Idle, Walk, Run, Melee, Ranged, Magic, Hit Stun, Death), Wang-tile autotiling masks (16-tile corner & 47-tile blob), HUD elements, and particle VFX specs (`specs/sprite_matrix_specs.json`).
- **Multi-Agent Skill Compatibility**: Provided instruction manifests and integration workflows for **Claude Code**, **OpenAI Codex**, and **Antigravity IDE** (`skills/pixelmatrix-engine/SKILL.md`).
- **Web Showcase Dashboard**: Re-designed `index.html` with interactive palette LUT viewer, canvas spec generator, CLI builder, and live `/changelog` route viewer.
