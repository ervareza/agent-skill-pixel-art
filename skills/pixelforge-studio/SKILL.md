---
name: pixelforge-studio
description: >
  AI-driven 2D pixel art game asset generation system. Converts game design specs into
  pixel art sprites, tilesets, animation frame sequences, and UI elements through multi-role
  synthesis. Exports sprite sheet atlases and individual PNGs. Use when user asks to
  "create pixel art", "generate game sprites", "make tileset", "generate pixel assets",
  or mentions "pixelforge-studio" or "pixelforge".
---

# PixelForge Studio Skill

> Autonomous 2D pixel game asset synthesis engine. Converts game design descriptions into production-ready pixel art sprites, seamless tilesets, frame-by-frame animations, and UI elements through structured role orchestration.

**Core Pipeline**: `Design Specification → Forge Workspace → Style Confirmation → Strategist → [Image Acquisition] → Executor → Asset Inspector & Post-Processing → Atlas Export`

> [!CAUTION]
> ## 🚨 Global Execution Discipline (MANDATORY)
>
> **This workflow is a strict serial pipeline. The following rules have the highest priority — violating any one of them constitutes execution failure:**
>
> 1. **SERIAL EXECUTION** — Steps MUST be executed in order; the output of each step is the input for the next. Non-BLOCKING adjacent steps may proceed continuously once prerequisites are met.
> 2. **BLOCKING = HARD STOP** — Steps marked ⛔ BLOCKING require a full stop; the AI MUST wait for an explicit user response before proceeding.
> 3. **NO CROSS-PHASE BUNDLING** — Cross-phase bundling is FORBIDDEN.
> 4. **GATE BEFORE ENTRY** — Each Step has prerequisites (🚧 GATE) listed at the top; these MUST be verified before starting that Step.
> 5. **NO SPECULATIVE EXECUTION** — "Pre-preparing" content for subsequent Steps is FORBIDDEN.
> 6. **NO SUB-AGENT GENERATION** — Executor Step 6 pixel art generation is context-dependent and MUST be completed by the current main agent end-to-end.
> 7. **SEQUENTIAL ASSET GENERATION** — Assets MUST be generated sequentially in one continuous pass.
> 8. **SPEC_LOCK RE-READ PER ASSET** — Before generating each asset, Executor MUST re-read `spec_lock.md`. All colors / sizes / palettes MUST come from this file.

> [!IMPORTANT]
> ## 🌐 Language & Communication Rule
>
> - **Response language**: match the user's input. Explicit user override takes precedence.
> - **Template format**: `design_spec.md` MUST follow its original English template structure regardless of conversation language. Content values may be in the user's language.

> [!IMPORTANT]
> ## 🔌 System Compatibility
>
> - `pixelforge-studio` is a dedicated asset synthesis workflow engine.
> - Do NOT generate loose temporary files outside project workspace boundaries.
> - Follow pipeline contract standards strictly.

## Core Engine Utilities

| Utility Script | Purpose |
|----------------|---------|
| `${SKILL_DIR}/scripts/forge_workspace.py` | Workspace initialization, source importing, and validation |
| `${SKILL_DIR}/scripts/chroma_analyzer.py` | Color palette extraction, Euclidean distance calculation, and verification |
| `${SKILL_DIR}/scripts/asset_inspector.py` | Quality audit and specification contract compliance testing |
| `${SKILL_DIR}/scripts/atlas_packer.py` | Sprite atlas packing and JSON manifest generation |
| `${SKILL_DIR}/scripts/post_processor.py` | Asset quantization, stray pixel cleaning, and indexed PNG conversion |

## Template Index

| Index | Path | Purpose |
|-------|------|---------|
| Palette Library | `${SKILL_DIR}/templates/palettes/palettes_index.json` | Available pixel art color palettes |
| Size Presets | `${SKILL_DIR}/templates/sizes/sizes_index.json` | Standard pixel art canvas dimensions |
| Sprite Layouts | `${SKILL_DIR}/templates/sprites/sprites_index.json` | Sprite layout templates (character, tile, item, UI) |

## Standalone Workflows

| Workflow | Path | Purpose |
|----------|------|---------|
| `palette_synthesis` | `workflows/palette_synthesis.md` | Palette generation and color harmony workflow |
| `batch_animation` | `workflows/batch_animation.md` | Batch animation frame sequence synthesis |

---

## Synthesis Pipeline

### Step 1: Design Input Analysis

🚧 **GATE**: User provides game design concept or visual reference

| Input Type | Processing |
|-----------|-----------|
| Text description | Parse into asset requirements specification |
| Reference images | Extract color palette and pixel scale using `chroma_analyzer.py` |
| Design doc | Build comprehensive asset inventory |
| Existing sprites | Extract style signature and dimensions |

---

### Step 2: Workspace Initialization

🚧 **GATE**: Step 1 complete

```bash
python ${SKILL_DIR}/scripts/forge_workspace.py init <project_name> --size 32x32 --palette default
```

**Directory Layout**:
```
projects/<name>_<size>_<date>/
├── design_spec.md          # Human-readable design spec
├── spec_lock.md            # Machine-readable execution contract
├── images/                 # Reference visual sources
├── assets/                 # Generated PNG assets
│   ├── characters/
│   ├── tiles/
│   ├── items/
│   ├── ui/
│   ├── effects/
│   └── backgrounds/
├── animations/             # Frame sequences
├── sheets/                 # Packed atlas sprite sheets
├── notes/                  # Asset engineering notes
└── exports/                # Export packages
```

Import reference images:
```bash
python ${SKILL_DIR}/scripts/forge_workspace.py import-sources <project_path> <files...> --move
```

---

### Step 3: Visual Style Selection

🚧 **GATE**: Step 2 complete

| Style | Description | Typical Canvas | Color Budget |
|-------|-------------|---------------|--------------|
| **NES Classic** | 8-bit retro console, sharp contrast | 16x16 / 32x32 | 4-8 colors |
| **SNES Retro** | 16-bit console, smooth shading | 32x32 / 64x64 | 8-16 colors |
| **Modern Indie** | Vibrant contemporary pixel art | 32x32 / 64x64 | 16-32 colors |
| **Micro Pixel** | Ultra-minimalist icon style | 8x8 / 16x16 | 2-4 colors |
| **Hi-Tech Detail** | Dense, highly detailed sprites | 64x64 / 128x128 | 24-48 colors |

⛔ **BLOCKING** — Present style options to user, wait for confirmation.

---

### Step 4: Specification & Contract Lock

🚧 **GATE**: Step 3 confirmed

Formulate the **Six Specifications**:
1. **Canvas Base Size**: Resolution per frame (8x8 up to 2048x2048).
2. **Total Asset Inventory Count**: Number of unique sprites/tiles required.
3. **Target Runtime Engine**: Unity, Godot, RPG Maker, Web, etc.
4. **Chroma Palette**: Selected palette or derived palette code set.
5. **Pixel Rendering Mode**: Outlined, outlineless, cel-shaded, or dithered.
6. **Animation Parameters**: Directional rows and action frame counts.

⛔ **BLOCKING** — Confirm specifications with user.

Generate contract files:
- `design_spec.md`
- `spec_lock.md`

---

### Step 5: Executor Asset Synthesis

🚧 **GATE**: Step 4 confirmed, `spec_lock.md` verified

**Role rules**: see `references/executor.md`

- Generate individual assets into `assets/` subdirectories.
- Enforce strict tile tiling guidelines (`pipeline_rules.md`).
- Run `asset_inspector.py` after asset batch synthesis.

---

### Step 6: Post-Processing & Export

🚧 **GATE**: Step 5 complete and verified by `asset_inspector.py`

```bash
# 1. Post-process (quantize, clean orphan pixels, index PNG)
python ${SKILL_DIR}/scripts/post_processor.py <project_path> --all

# 2. Pack sprite atlases
python ${SKILL_DIR}/scripts/atlas_packer.py <project_path>
```

---

## Role Switch Matrix

| Phase | Active Role | Reference |
|-------|------------|-----------|
| Step 1-3 | Lead Architect | `SKILL.md` |
| Step 4 | Strategist | `references/strategist.md` |
| Step 5 | Executor | `references/executor.md` |
| Step 6 | Post-processor | `references/pipeline_rules.md` |

Announce transitions using `[Role Switch: <Role>]`.
