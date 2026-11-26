# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [v1.0.0] - 2026-11-26

### Added
- **Pure-Python PixelForge Engine (`skills/pixel-art/engine/`)** — Ground-up modular pixel art & game asset engine (`color.py`, `canvas.py`, `character.py`, `tileset.py`, `vfx.py`, `assets.py`, `exporters.py`, `qa.py`) synthesized from 17 top-starred open-source pixel art skills and studios.
- **15-Layer Character Rig & Paper-Doll System** — Bottom-to-top rig (`shadow`, `cape_back`, `hair_back`, `arm_far`, `leg_far`, `torso`, `leg_near`, `head`, `hair_front`, `headgear`, `arm_near`, `weapon`, `shield`, `vfx`, `outline`) with blend modes (`normal`, `multiply`, `screen`, `add`, `overlay`), opacity, linked cels, and per-layer PNG sheet export.
- **True 1/2/4/8-Direction Animated Characters** — Shared landmark rows across all directions (zero turning bob), North view with zero face, darker far limbs, 8 biomechanical actions (`idle`, `walk`, `run`, `jump`, `attack`, `cast`, `hurt`, `die`), and 9 archetypes (`hero`, `knight`, `mage`, `ranger`, `rogue`, `villager`, `skeleton`, `goblin`, `slime`).
- **Arbitrary Pixel Resolutions & Frame Counts** — Resolution-tier proportions supporting `8×8`, `9×9`, `12×12`, `16×16`, `16×24`, `24×24`, `32×32`, `48×48`, `64×64`, `128×128+` and continuous kinematic phase sampling for `2`, `3`, `4`, `5`, `6`, `8`, `12`, `24`, `60` frames at `1–60 FPS`.
- **Seamless Toroidal Terrain & Autotile Engine** — 11 terrain presets, 16-tile Wang & 47-tile Blob autotiles with bitmask JSON, animated water/lava loops, and 2:1 isometric blocks.
- **12 Seeded Procedural Pixel Art VFX** — `explosion`, `fire`, `smoke`, `slash`, `sparkle`, `magic_orb`, `lightning`, `water_splash`, `heal_aura`, `hit_impact`, `portal`, `coin_spin`.
- **Game Items, ZzSprite Creatures, 9-Slice UI & Fake-3D Sprite Stacking** — 10 RPG items/weapons, symmetrical procedural creature generator, 5 UI components (9-slice panel, dynamic health bar, 3-state button, inventory slot, cursor), and 360° fake-3D stacked slice turntables.
- **Native `.aseprite` Binary Writer & Universal Game Engine Exporters** — Valid Aseprite v1.3 files preserving layers/cels/tags/palette, Godot 4 `.tres` `SpriteFrames`, Aseprite/Phaser/Unity JSON, RPG Maker MV/MZ 3×4, LPC 64×64, transparent GIFs, and alpha-preserving indexed 8-bit PNGs.
- **8 New CLI Scripts & 6 New Palettes** — 21 CLI tools (`pixel_studio.py`, `character_gen.py`, `layer_compose.py`, `tileset_gen.py`, `vfx_gen.py`, `asset_gen.py`, `sprite_stack.py`, `sprite_clean.py` + 13 upgraded tools) and 16 curated palettes (`aap-64`, `lospec-500`, `fantasy-24`, `cyberpunk-16`, `pastel-16`, `onebit`).
- **Interactive Playable 4-Dir Walk Arena & `/changelog` Page** — Live WASD/Arrow/D-pad layered character sandbox in `index.html`, new `templates/turntable_viewer.html`, upgraded `templates/sprite_sheet.html`, and 67-test `pytest` suite (`tests/test_engine.py`).

### Changed
- Complete ground-up v1.0.0 reboot on a single clean `main` branch, replacing legacy placeholder examples with verified, game-ready multi-layer showcase assets.
- Rewrote `SKILL.md` and expanded craft reference docs to 10 guides (added `layering_and_rigging.md`, `sprite_stacking.md`, `critique_and_qa.md`).

### Fixed
- `export_indexed.py` now preserves alpha transparency cleanly via a dedicated transparent index instead of destroying alpha through RGB conversion.
- `outline_generator.py` now honors `--inset` and supports directional selective outlines (`--mode selout`) and `--rim-light`.
- `noise_generator.py` now uses true 4-edge toroidal wrapping so terrain textures tile seamlessly.
- `quality_audit.py` defaults to `--grid 1` (supporting odd sizes like `9×9` and `12×12`) and adds jaggies/doubles, clipping, palette conformance, and seamlessness verification.
