---
name: pixelmatrix-engine
description: Next-Generation Autonomous 2D Pixel Art, Tilemap, Character Matrix, and Palette LUT Synthesis Engine for Claude Code, OpenAI Codex, and Antigravity IDE. Use when creating 2D game sprites, tilesets, autotiles, UI elements, particle VFX, or enforcing pixel grid constraints and palette LUT compliance.
---

# PixelMatrix Engine (v2.0.0) — AI Agent Instruction Manifest

Welcome to **PixelMatrix Engine**, an enterprise-grade, deterministic AI Agent Skill for synthesizing, inspecting, quantizing, and compiling 2D Pixel Art assets for modern game engines (Godot, Unity, Defold, Unreal 2D, web canvas).

---

## Agent Auto-Detection & Intent Triggers

Activate `pixelmatrix-engine` when the user asks to:
- Generate 2D pixel art sprites, character sheets, terrain tilemaps, autotile Wang-masks, UI elements, or particle VFX.
- Enforce strict pixel grid alignment (16x16, 32x32, 48x48 isometric, 64x64, 128x128, 256x256).
- Apply hardware or modern aesthetic color palette LUTs (NES, GameBoy 4-color, PICO-8, Cyberpunk Neon, Synthwave, Dungeon Dark).
- Inspect asset quality for anti-aliasing artifacts, semi-transparent pixels, or isolated orphan pixels.
- Pack sprite frames into grid texture atlases with structured JSON metadata manifests.

---

## Engine Reference Specifications

Read specification indexes in `skills/pixelmatrix-engine/specs/` prior to asset generation:

1. **[Grid Canvas Presets](file:///Users/ervareza/CODE/agent-skill-pixel-art/skills/pixelmatrix-engine/specs/grid_canvas_presets.json)**: Canvas bounds, snapping specs, projection angles.
2. **[Palette LUT Definitions](file:///Users/ervareza/CODE/agent-skill-pixel-art/skills/pixelmatrix-engine/specs/palette_lut_definitions.json)**: NES, GameBoy, PICO-8, Cyberpunk, Synthwave LUT hex arrays.
3. **[Sprite Matrix Specs](file:///Users/ervareza/CODE/agent-skill-pixel-art/skills/pixelmatrix-engine/specs/sprite_matrix_specs.json)**: 4/8-way directional character matrices, autotile sets, HUD 9-slice elements, particle VFX.

---

## Agent Execution Protocol

### Step 1: Workspace & Asset Manifest Setup
Run `canvas_initializer.py` to create workspace folders and asset contracts:
```bash
python3 skills/pixelmatrix-engine/scripts/canvas_initializer.py \
  --workspace ./ \
  --asset-name <ASSET_NAME> \
  --preset <PRESET_KEY> \
  --palette <PALETTE_KEY> \
  --matrix <MATRIX_KEY> \
  --json
```

### Step 2: Asset Quality & Grid Inspection
Inspect generated raster assets using `spec_inspector.py`:
```bash
python3 skills/pixelmatrix-engine/scripts/spec_inspector.py \
  --image source_rasters/<ASSET_NAME>_raw.png \
  --width <WIDTH> \
  --height <HEIGHT> \
  --max-colors <MAX_COLORS> \
  --json
```

### Step 3: Post-Processing & Indexed Export
Clean anti-aliasing artifacts and export indexed 8-bit PNG via `raster_processor.py`:
```bash
python3 skills/pixelmatrix-engine/scripts/raster_processor.py \
  --input source_rasters/<ASSET_NAME>_raw.png \
  --output exports/indexed_png/<ASSET_NAME>_indexed.png \
  --max-colors <MAX_COLORS> \
  --json
```

### Step 4: Sprite Atlas Compilation
Pack sprite animation frames into a packed atlas via `atlas_compiler.py`:
```bash
python3 skills/pixelmatrix-engine/scripts/atlas_compiler.py \
  --frames-dir source_rasters/<FRAMES_DIR>/ \
  --output compiled_atlases/<ASSET_NAME>_atlas.png \
  --width <WIDTH> \
  --height <HEIGHT> \
  --json
```

---

## Strict Production Directives

1. **Zero Anti-Aliasing (AA)**: All pixels must be 100% opaque (`a = 255`) or 100% transparent (`a = 0`).
2. **Strict Color Limits**: Never exceed the `max_colors` defined in the target palette LUT.
3. **Grid Alignment**: Sprites and tiles MUST align perfectly to pixel boundaries (no sub-pixel rendering).
4. **Clean File Outputs**: Always generate structured JSON outputs alongside texture PNGs.
