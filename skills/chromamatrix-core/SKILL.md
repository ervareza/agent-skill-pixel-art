---
name: chromamatrix-core
description: Next-Generation Autonomous 2D Pixel Art, Tilemap, Character Matrix & Luma Palette Synthesis Engine for Claude Code, OpenAI Codex, and Antigravity IDE. Use when creating 2D game sprites, tilesets, autotiles, UI elements, particle VFX, or enforcing pixel grid constraints and LumaLUT compliance.
---

# ChromaMatrix Core (v3.0.0) — AI Agent Instruction & Context Manifest

Welcome to **ChromaMatrix Core**, an enterprise-grade, deterministic AI Agent Skill for synthesizing, auditing, quantizing, and compiling 2D Pixel Art assets for modern game engines (Godot, Unity, Defold, Unreal 2D, web canvas).

---

## Agent Auto-Detection & Intent Triggers

Activate `chromamatrix-core` when asked to:
- Synthesize 2D pixel art sprites, character sheets, terrain tilemaps, autotile Wang-masks, UI elements, or particle VFX.
- Enforce strict pixel grid alignment (8x8 micro, 16x16, 32x32, 48x48 isometric axonometric, 64x64 boss, 128x128 HD pixel).
- Apply hardware or modern aesthetic color LumaLUTs (PICO-8, GameBoy 4-color, Cyberpunk Neon, Retro CRT Phosphor, Arcade Nostalgia, NES).
- Perform quality control audits for anti-aliasing artifacts, semi-transparent pixels, or isolated orphan pixels.
- Pack sprite frames into grid texture atlases with structured JSON metadata manifests.

---

## Manifest Vault References

Read specification indexes in `skills/chromamatrix-core/ManifestVault/` prior to asset generation:

1. **[Grid Matrices](file:///Users/ervareza/CODE/agent-skill-pixel-art/skills/chromamatrix-core/ManifestVault/GridMatrices.json)**: Canvas bounds, snapping specs, projection angles.
2. **[Luma Palettes](file:///Users/ervareza/CODE/agent-skill-pixel-art/skills/chromamatrix-core/ManifestVault/LumaPalettes.json)**: PICO-8, GameBoy, Cyberpunk, CRT Phosphor, Arcade LUT hex arrays.
3. **[Sprite Core](file:///Users/ervareza/CODE/agent-skill-pixel-art/skills/chromamatrix-core/ManifestVault/SpriteCore.json)**: 4/8-way directional character matrices, autotile rulesets, retro UI, particle VFX.

---

## Render Orchestration Protocol

### Step 1: Voxel Canvas & Contract Setup
Run `CanvasBootstrapper.py` to create canvas directories and asset contracts:
```bash
python3 skills/chromamatrix-core/RenderOrchestrators/CanvasBootstrapper.py \
  --canvas ./ \
  --asset-id <ASSET_ID> \
  --grid-matrix <GRID_MATRIX_KEY> \
  --palette-lut <PALETTE_LUT_KEY> \
  --sprite-core <SPRITE_CORE_KEY> \
  --json
```

### Step 2: Quality Sentinel Audit
Audit generated raster assets using `QualitySentinel.py`:
```bash
python3 skills/chromamatrix-core/RenderOrchestrators/QualitySentinel.py \
  --image source_rasters/<ASSET_ID>_raw.png \
  --width <WIDTH> \
  --height <HEIGHT> \
  --max-colors <MAX_COLORS> \
  --json
```

### Step 3: Raster Refinement & Indexed Export
Clean anti-aliasing artifacts and export indexed 8-bit PNG via `RasterRefiner.py`:
```bash
python3 skills/chromamatrix-core/RenderOrchestrators/RasterRefiner.py \
  --input source_rasters/<ASSET_ID>_raw.png \
  --output exports/indexed_png/<ASSET_ID>_indexed.png \
  --max-colors <MAX_COLORS> \
  --json
```

### Step 4: Sprite Atlas Synthesis
Pack sprite animation frames into a packed atlas via `AtlasSynthesizer.py`:
```bash
python3 skills/chromamatrix-core/RenderOrchestrators/AtlasSynthesizer.py \
  --frames-dir source_rasters/<FRAMES_DIR>/ \
  --output compiled_atlases/<ASSET_ID>_atlas.png \
  --width <WIDTH> \
  --height <HEIGHT> \
  --json
```

---

## Production Rules

1. **Zero Anti-Aliasing (AA)**: All pixels must be 100% opaque (`a = 255`) or 100% transparent (`a = 0`).
2. **Strict Color Limits**: Never exceed the `max_colors` defined in the target LumaLUT.
3. **Grid Alignment**: Sprites and tiles MUST align perfectly to pixel boundaries.
4. **Clean File Outputs**: Always generate structured JSON metadata alongside texture PNGs.
