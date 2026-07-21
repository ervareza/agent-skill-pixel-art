# Changelog

All notable changes to **ChromaMatrix Core** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v3.0.0] - 2026-07-22

### Changed (Major Release)
- **Engine Transformation**: Complete ground-up re-engineering and transformation into **ChromaMatrix Core** (`v3.0.0`).
- **Strict Terminology Ban Enforcement**: Eradicated 100% of banned generic terms (`template`, `spec`, `reference`, `script`, `config`, `pipeline`, `preset`, `utils`, `helpers`, `art-generator`) across file names, directories, variables, and documentation.
- **Render Orchestrators Overhaul**: Re-architected engine micro-modules:
  - `CanvasBootstrapper` (`CanvasBootstrapper.py`): Voxel canvas initialization and asset contract manifests.
  - `ChromaSynthesizer` (`ChromaSynthesizer.py`): Color palette extraction, 3D RGB distance metrics, and LumaLUT remapping.
  - `QualitySentinel` (`QualitySentinel.py`): Automated quality audit inspecting grid alignment, palette bounds, AA artifact detection, and orphan pixels.
  - `AtlasSynthesizer` (`AtlasSynthesizer.py`): Texture atlas packing and JSON metadata manifest generation.
  - `RasterRefiner` (`RasterRefiner.py`): Color quantization, orphan pixel purging, and indexed 8-bit PNG export.

### Added
- **ManifestVault Layer**:
  - `GridMatrices.json`: Dynamic resolution scaling from 8x8 micro to 128x128 HD pixel cut-ins, 48x48 isometric axonometric projection, Wang-tile autotiling masks, and 9-slice UI frame matrices.
  - `LumaPalettes.json`: PICO-8 16-color, GameBoy 4-color DMG-01, Cyberpunk Neon 16, Retro CRT Phosphor 16, Arcade Nostalgia 32, NES 54, Master System 64, and custom 24-bit HEX mapping LUTs.
  - `SpriteCore.json`: 4/8-way directional character state machines (Idle, Walk, Run, Jump Squash/Stretch, Melee Slash, Spellcast, Flinch, Death), Wang-tile autotiles, retro UI elements, and VFX particle emitters.
- **PixelProtocols & RasterBlueprints**: Comprehensive execution orchestration guides, canvas constraints, system design documentation, and asset contract blueprints.
- **Multi-Agent Capability**: Context manifests and integration commands for **Claude Code**, **OpenAI Codex**, and **Antigravity IDE** (`skills/chromamatrix-core/SKILL.md`).
- **Web Showcase Dashboard**: Re-designed `index.html` with interactive LumaLUT viewer, grid matrices viewer, CLI builder, and live `/changelog` route view.
