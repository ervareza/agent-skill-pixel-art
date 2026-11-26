---
name: pixel-art
description: "Complete 2D pixel art & game asset engine and agent skill (PixelForge v1.0.0). Use whenever the user wants to create, layer, animate, clean, audit, or export 2D pixel art game assets: multi-directional walking/running/combat characters (1/2/4/8-dir, any size 8x8/9x9/12x12/16x16/24x24/32x32/48x48/64x64/WxH, any frame count 2..60 frames & 1..60 FPS) with paper-doll layer rigs, seamless terrain tiles, 16-tile Wang & 47-tile Blob autotiles, animated water/lava, 2:1 isometric blocks, procedural pixel VFX (fire, explosion, slash, lightning, magic, smoke, portal), game items & weapons, ZzSprite procedural creatures, 9-slice UI panels/bars/buttons, fake-3D sprite stacking turntables, AI-art pixel cleanup, native .aseprite binary export, Godot 4 .tres SpriteFrames, Unity/Phaser/Aseprite JSON, RPG Maker 3x4, transparent GIFs, or pixel art quality audits."
license: MIT
---

# PixelForge — 2D Pixel Art & Game Asset Agent Skill (v1.0.0)

Build production-ready, layered, animated 2D pixel art game assets deterministically in pure Python (Pillow only — zero Aseprite binary or diffusion model required), inspect every frame visually with your own eyes, pass automated pixel-art QA, and export directly into **Aseprite (`.aseprite`)**, **Godot 4 (`.tres`)**, **Unity**, **Phaser 3**, **RPG Maker MV/MZ**, **LPC**, **GIF**, and **Indexed PNG**.

**The Quality Loop (MANDATORY — NEVER SKIP):**
`Design Brief → Palette Lock → Layer Rig → Generate / Author → Render Contact Sheet & LOOK → Critique & QA Audit → Refine → Export`

> [!CAUTION]
> ## Global Pixel-Art Craft Discipline
> 1. **PALETTE & RAMP FIRST** — Lock a palette (or build hue-shifted ramps via `hue_ramp()`) before drawing. Shadows cool toward blue/purple; highlights warm toward yellow/cream. Never shade by just moving a brightness slider.
> 2. **RIG BEFORE ANIMATING** — Keep characters split into animatable layers (`shadow`, `cape_back`, `hair_back`, `arm_far`, `leg_far`, `torso`, `leg_near`, `head`, `hair_front`, `headgear`, `arm_near`, `weapon`, `shield`, `vfx`, `outline`). Baking everything flat destroys editability and paper-doll equipment swaps.
> 3. **SHARED LANDMARK ROWS ACROSS DIRECTIONS** — Head top, eyes, shoulders, belt, hip, and foot baseline (`ground_y`) MUST stay identical across Down, Left, Right, Up, and diagonals so the character never bobs when turning. **North (Up) view NEVER has a face.**
> 4. **ZERO ANTI-ALIASING** — Every pixel is either opaque (`alpha=255`) or transparent (`alpha=0`). Nearest-neighbor scaling ONLY (`Image.Resampling.NEAREST`).
> 5. **LOOK AT THE CONTACT SHEET, NOT JUST THE GIF** — Vision tools only see frame 1 of a GIF. Always inspect a labeled contact sheet (`doc.preview_image()` or `--preview`) + run `quality_audit.py` before shipping.

---

## Quick Decision Tree

```
What game asset does the user want?
├── Animated Character (4-dir / 8-dir / side-scroller / RPG / paper-doll layers)
│     1. Read references/layering_and_rigging.md + references/animation_principles.md
│     2. Run scripts/character_gen.py with exact --size (8|9|12|16|24|32|48|64|WxH),
│        --dirs (1|2|4|8), --actions (idle,walk,run,jump,attack,cast,hurt,die),
│        --frames (2..60), --fps (1..60), --aseprite --export-layers --gif --godot --rpgmaker --preview
│     3. Inspect *_preview.png visually + audit with scripts/quality_audit.py
│
├── Custom Hand-Authored Pixel Art (Python DSL / ASCII grids / multi-layer build script)
│     1. Import `SpriteDocument`, `hue_ramp`, `ColorRamp` from `engine`
│     2. Build silhouette first → flat color masses → shifted-shape shading (`only="opaque"`)
│        → `rim_light()` → `selout()` (selective hue-shifted outline)
│     3. Inspect `doc.preview_image(scale=6)` and `doc.ascii_view()` → iterate 2-3x
│     4. Export via `engine.exporters` (`.aseprite`, spritesheet + JSON, `.tres`, GIF)
│
├── Tileset / Autotile / Animated Terrain / Isometric 2:1
│     1. Read references/tileset_rules.md (or references/isometric_guide.md)
│     2. Run scripts/tileset_gen.py (--mode single | wang16 | blob47 | animated | isometric)
│     3. Verify 4-edge seamless wrap via scripts/quality_audit.py --check-seamless
│
├── Pixel Art VFX (Explosion, Fire, Smoke, Slash, Lightning, Magic, Portal, Splash, Heal)
│     1. Read references/particle_effects.md
│     2. Run scripts/vfx_gen.py --type <vfx> --size WxH --frames N --fps F --gif --aseprite
│
├── Game Items, Weapons, Procedural Monsters (ZzSprite), or 9-Slice UI
│     1. Read references/ui_elements.md
│     2. Run scripts/asset_gen.py --category item|zzsprite|ui --type <name> --size WxH
│
├── Fake-3D Rotatable Sprite Stacking (Cars, Props, Trees, Towers, Turntables)
│     1. Read references/sprite_stacking.md
│     2. Run scripts/sprite_stack.py --preset car|crate|tree|tower|chest (or --strip) --slices N --frames 16 --gif
│
├── Clean Messy / AI-Generated PNG into Strict Pixel Art
│     1. Read references/critique_and_qa.md
│     2. Run scripts/sprite_clean.py --input raw.png --output clean.png --strip-checker --palette endesga-32
│
└── Layer Editing / Post-Processing / Batch QA
      -scripts/layer_compose.py (toggle/opacity/blend/split/merge -> .aseprite)
      -scripts/outline_generator.py (--mode outside|inset|selout --rim-light)
      -scripts/palette_remap.py / palette_extract.py / export_indexed.py / atlas_pack.py / gif_export.py
      -scripts/quality_audit.py / batch_audit.py
```

---

## Complete Toolkit (21 CLI Scripts — All Support `--help` and `--json`)

Master dispatcher: `python scripts/pixel_studio.py <command> [args]` (run `pixel_studio.py info` to list all presets & palettes).

### Asset Generation & Layer Engine
| Script | Purpose | Key Flags |
|---|---|---|
| `character_gen.py` | Multi-layer 1/2/4/8-dir animated characters (9 archetypes, paper-doll gear) | `--archetype`, `--size`, `--dirs`, `--actions`, `--frames`, `--fps`, `--weapon`, `--headgear`, `--shield`, `--aseprite`, `--export-layers`, `--godot`, `--rpgmaker`, `--gif`, `--preview` |
| `layer_compose.py` | Compose, hide/show, opacity, blend modes, split layers, export `.aseprite` | `--project`/`--layers`, `--hide`, `--show-only`, `--opacity`, `--blend`, `--aseprite`, `--split-dir` |
| `tileset_gen.py` | Seamless terrain, 16-tile Wang & 47-tile Blob autotiles, animated water/lava, 2:1 isometric | `--terrain`, `--size`, `--mode`, `--frames`, `--fps`, `--palette`, `--gif` |
| `vfx_gen.py` | 12 seeded procedural VFX (explosion, fire, smoke, slash, sparkle, magic_orb, lightning, water_splash, heal_aura, hit_impact, portal, coin_spin) | `--type`, `--size`, `--frames`, `--fps`, `--palette`, `--seed`, `--gif`, `--aseprite` |
| `asset_gen.py` | 10 RPG items/weapons, ZzSprite procedural creatures, 5 UI components (9-slice, bars, 3-state buttons) | `--category`, `--type`, `--size`, `--style`, `--seed`, `--gif` |
| `sprite_stack.py` | Fake-3D sprite stacking slice strips & 360° rotatable turntables | `--preset`/`--strip`, `--slices`, `--frames`, `--squash`, `--spacing`, `--gif` |
| `sprite_clean.py` | AI/messy PNG cleanup (auto-scale detect, strip checker, harden alpha, despeckle, dedupe, dehalo, palette snap) | `--input`, `--output`, `--scale`, `--strip-checker`, `--palette`, `--max-colors` |
| `pixel_studio.py` | Unified master CLI dispatcher + `info` & `palettes` inspection | `info`, `palettes`, `<subcommand>` |

### Post-Processing, Packing & Quality Assurance
| Script | Purpose | Key Flags |
|---|---|---|
| `quality_audit.py` | Single PNG QA: AA, orphans, palette conformance, near-dups, jaggies/doubles, clipping, seamless wrap | `--image`, `--grid` (default `1`), `--max-colors`, `--palette`, `--ignore-orphans`, `--check-seamless` |
| `batch_audit.py` | Directory-wide recursive QA | `--dir`, `--grid`, `--max-colors`, `--palette`, `--ignore-orphans` |
| `atlas_pack.py` | Pack frame PNGs into sheet + Aseprite/Phaser/Unity/simple JSON + optional Godot `.tres` & `.aseprite` | `--frames-dir`, `--output`, `--cols`, `--padding`, `--format`, `--godot`, `--aseprite` |
| `gif_export.py` | Crisp transparent animated GIF (1..60 FPS, nearest-neighbor scaling) | `--sheet`/`--frames-dir`, `--fps`, `--scale`, `--bg`, `--output` |
| `outline_generator.py` | Add 1px outside, inset, or selective (`selout`) outline + optional `--rim-light` | `--input`, `--output`, `--mode`, `--inset`, `--rim-light`, `--color` |
| `palette_remap.py` | Perceptual redmean color remapping to any built-in palette name or JSON (+ optional Bayer dither) | `--image`, `--palette`, `--output`, `--dither` |
| `palette_extract.py` | Extract color palette with pixel frequency analysis | `--image`, `--max-colors`, `--output` |
| `export_indexed.py` | Convert RGBA PNG to indexed 8-bit PNG while **preserving alpha transparency** | `--input`, `--output`, `--max-colors` |
| `dither.py` | Ordered Bayer (2×2 / 4×4 / 8×8) & Codixel band-edge (`--strip`) dithering | `--width`, `--height`, `--color1`, `--color2`, `--matrix`, `--axis`, `--strip` |
| `noise_generator.py` | Guaranteed 4-edge seamless toroidal FBM Value noise & Toroidal Voronoi | `--width`, `--height`, `--type`, `--scale`, `--cells`, `--palette` |
| `sprite_resize.py` | Nearest-neighbor integer scaling ONLY | `--input`, `--output`, `--scale` |
| `sprite_mirror.py` | Horizontal / vertical mirroring (single or batch) | `--input`/`--input-dir`, `--axis` |
| `init_workspace.py` | Scaffold standard 10-folder PixelForge game asset workspace | `--dir`, `--name` |

---

## Python Engine API (For Custom Authoring Scripts)

For bespoke art beyond presets, write a clean Python build script importing from `engine/`:

```python
import sys; sys.path.insert(0, "skills/pixel-art")
from engine import SpriteDocument, ColorRamp, hue_ramp
from engine.exporters import export_aseprite, export_spritesheet, export_gif

body = ColorRamp.from_base("slime", "#38B764", steps=4)
doc = SpriteDocument(32, 32, palette="endesga-32", default_fps=8)
doc.ensure_rig_layers(["shadow", "body", "eyes", "outline"])

for fi, squash in enumerate((0, 2, -1, 1)):
    if fi > 0:
        doc.add_frame(copy=False)
    doc.layer("shadow").ellipse(8, 26, 23, 29, "#181425")
    doc.layer("body").ellipse(6 - squash, 12 + squash, 25 + squash, 27, body.shadow)
    doc.ellipse(6 - squash, 11 + squash, 24 + squash, 25, body.mid, only="opaque")
    doc.ellipse(9, 14 + squash, 14, 17 + squash, body.highlight, only="opaque")
    doc.layer("eyes").rect(11, 19 + squash, 12, 20 + squash, "#181425")
    doc.rect(19, 19 + squash, 20, 20 + squash, "#181425")
    doc.layer("outline").selout("#181425", composite_mode=True)

doc.tag("bounce", 1, 4)
doc.preview_image(scale=6, grid=True).save("preview.png")   # LOOK at this!
export_aseprite(doc, "slime.aseprite")
export_spritesheet(doc, "slime_sheet.png", cols=4)
export_gif([doc.composite(i+1) for i in range(4)], "slime.gif", durations_ms=120, scale=4)
```

---

## Resolution & Frame-Count Flexibility

PixelForge natively adapts anatomy, proportions, line weights, and gait kinematics across ANY canvas size and frame budget:

| Resolution Tier | Examples | Anatomy & Outline Strategy |
|---|---|---|
| **Micro** (`8–11px`) | `8×8`, `9×9`, `10×10` | No interior outlines; pure silhouette + value contrast; crisp 1×1 directional eyes |
| **Small Chibi** (`12–20px`) | `12×12`, `16×16`, `16×24` | 42% chibi head; crisp 1px outer selective outline; Pokémon/Stardew walk readability |
| **Standard Indie** (`21–40px`) | `24×24`, `32×32`, `24×32` | 3–3.5 heads; 3-tone hue-shifted shading; belt/buckle/cape/weapon layers; far limbs darker |
| **Hi-Bit Detailed** (`41–128px+`) | `48×48`, `64×64`, `96×96`, `128×128` | 4–5 head heroic proportions; detailed headgear, armor highlights, articulated limbs |

| Frame Budget | Best Use | Kinematic Sampling |
|---|---|---|
| `2` frames | 8-bit micro walk / idle blink | Left stride ↔ Right stride |
| `3` frames | RPG Maker MV/MZ classic 3×4 | Step L → Neutral Pass → Step R |
| `4` frames | Pokémon / Stardew / game jam | Contact L → Pass → Contact R → Pass |
| `5–6` frames | Action RPG compact smooth loop | Smooth phase interpolation + uneven timing |
| `8` frames | Fluid standard (Williams gait) | Contact → Down → Pass → Up (×2 mirrored) |
| `12–24` frames | Hi-bit smooth animation (Owlboy / Dead Cells) | Silky gait + delayed head bob + billowing cape |
| `60` frames | Ultra-high FPS showcase / slow-mo | Continuous kinematic phase sampling at 60 FPS |

---

## 16 Built-In Curated Palettes (`palettes/*.json`)

`onebit` (2) · `gameboy` (4) · `cga` (16) · `commodore-64` (16) · `pico-8` (16) · `sweetie-16` (16) · `cyberpunk-16` (16) · `pastel-16` (16) · `fantasy-24` (24) · `db32` (32) · `endesga-32` (32) · `lospec-500` (32) · `nes` (56) · `snes` (64) · `resurrect-64` (64) · `aap-64` (64)

---

## Reference Knowledge Base (`references/`)

- [Layering & Rigging](references/layering_and_rigging.md) — Standard character rig, paper-doll swaps, blend modes, linked cels, `.aseprite`
- [Sprite Conventions](references/sprite_conventions.md) — Proportions by size (8px..128px), 4/8-dir turnarounds, shared landmark rows
- [Animation Principles](references/animation_principles.md) — Contact-down-pass-up walk/run tables, top-down animation, non-uniform timing
- [Color Theory](references/color_theory.md) — Hue-shifted ramps, selective outlines (`selout`), rim light, band-edge dithering
- [Tileset Rules](references/tileset_rules.md) — 9 mandatory tile rules, toroidal noise/Voronoi, Wang 16 & Blob 47 bitmasks
- [Isometric Guide](references/isometric_guide.md) — 2:1 pixel ratio diamonds, wall shading, painter's depth sorting
- [Sprite Stacking](references/sprite_stacking.md) — Fake-3D 4-view carving, symmetric pivots `(w-1)*0.5`, post-stack outlines
- [UI Elements](references/ui_elements.md) — 9-slice panels, dynamic health bars, 3-state buttons, dialogs
- [Particle Effects](references/particle_effects.md) — Seeded VFX, two-buffer glow, hit-stop & anticipation timing
- [Critique & QA](references/critique_and_qa.md) — Cold-read pixel critic rubric, jaggies/doubles/banding, hybrid AI cleanup pipeline

## Interactive HTML5 Templates (`templates/`)

- `templates/sprite_sheet.html` — Sprite sheet inspector + **WASD/Arrow 4-dir & 8-dir playable walk tester** + onion skin + 1–60 FPS
- `templates/tilemap_preview.html` — Interactive tilemap painter + 2×2 seamless check
- `templates/palette_viewer.html` — All 16 palettes + hue-ramp builder + contrast ratio checker
- `templates/turntable_viewer.html` — 360° fake-3D sprite stacking turntable & slice scanner
