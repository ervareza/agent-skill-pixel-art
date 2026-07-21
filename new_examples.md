## Usage Examples (The Ultimate Showcase)

This skill supports generating pixel art across **all standard sizes, animation types, directions, and palettes**. Below are 7 exhaustive real-world use cases generated entirely by this skill, demonstrating its ability to handle anything from 16×16 retro items up to 1024×1024 cinematic scenes.

Every image shown is the **actual output** generated and validated by the tools.

### UC1: The Micro Sandbox (16×16, Sweetie-16)
**Focus:** Static items & VFX, Single direction.
**Animations:** Static (2 frames), Magic Spark VFX (12 frames).

| Rotating Coin (4×) | Magic Spark VFX (4×) |
|---|---|
| <img src="examples/uc1_micro/coin_0_4x.png" width="64"> <img src="examples/uc1_micro/coin_1_4x.png" width="64"> | <img src="examples/uc1_micro/spark.gif" width="64"> |

```bash
python scripts/gif_export.py --frames-dir ./vfx/ --fps 24 --output spark.gif
python scripts/batch_audit.py --dir ./vfx/ --grid 16 --max-colors 16 --ignore-orphans
```

---

### UC2: The 8-Way Action Hero (32×32, DB32)
**Focus:** 8-Directional movement, complex animation cycles, auto-mirroring.
**Animations:** Idle (4 frames), Walk (6 frames), Run (8 frames).
**Workflow:** Draw 5 directions (E, NE, N, SE, S). Auto-mirror 3 directions (W, NW, SW) using `sprite_mirror.py`. Total **144 frames** generated and packed!

#### 📸 Run Cycle (East, 16 FPS, 4× zoom)
<img src="examples/uc2_8way/hero_run_east.gif" width="128">

#### 📸 8-Way Sprite Atlas (Partial slice, 4× zoom)
<img src="examples/uc2_8way/hero_east_sheet_4x.png" width="100%">

```bash
python scripts/sprite_mirror.py --input-dir ./east_frames/ --output-dir ./west_frames/ --axis horizontal
python scripts/atlas_pack.py --frames-dir ./east_frames/ --output hero_east_sheet.png --cols 6
```

---

### UC3: The 4-Way Spellcaster & Overworld (64×64, Resurrect-64)
**Focus:** HD combat characters and seamless environment generation.
**Animations:** Attack (6 frames), Spell/Cast (8 frames), Hurt (3 frames).
**Environment:** Noise-generated grass/water tiles and dithered backgrounds.

#### 📸 Environment Tiles (Generated via `noise_generator.py` & `dither.py`)
| Grass (Value Noise) | Water (Value Noise) | Sky (4×4 Bayer Dither) |
|---|---|---|
| <img src="examples/uc3_hd/tiles/grass.png" width="64"> | <img src="examples/uc3_hd/tiles/water.png" width="64"> | <img src="examples/uc3_hd/tiles/dither_bg.png" width="64"> |

#### 📸 HD Spellcaster Frames (4× zoom)
| Spell Charge 0 | Spell Charge 1 | Attack Strike |
|---|---|---|
| <img src="examples/uc3_hd/wizard_spell_02_2x.png" width="128"> | <img src="examples/uc3_hd/wizard_spell_04_2x.png" width="128"> | <img src="examples/uc3_hd/frames/wizard_attack_03.png" width="64"> |

```bash
python scripts/noise_generator.py --width 64 --height 64 --scale 16 --octaves 2 --palette resurrect-64.json --output grass.png
```

---

### UC4: The Side-Scrolling Boss (128×128 → 256×256)
**Focus:** Giant boss sprites, upscaling, and outlining.
**Animations:** Jump/Fall (6 frames), Die (8 frames). Side-facing.
**Workflow:** Draw at 128×128. Resize to 256×256 (nearest-neighbor) and add a 1px outline for contrast against backgrounds.

| Giant Slime Boss (256×256, Outlined) |
|---|
| <img src="examples/uc4_boss/boss_256_outlined.png" width="258"> |

```bash
python scripts/sprite_resize.py --input boss.png --output boss_256.png --scale 2
python scripts/outline_generator.py --input boss_256.png --output boss_256_outlined.png --color "#000000"
```

---

### UC5: The Cinematic Portal (1024×1024 Ultra)
**Focus:** Massive full-screen animations and rigorous QA checks.
**Animations:** Cinematic smooth rotation (24 FPS).
**Validation:** Passing a 1-million pixel image through `quality_audit.py` to ensure absolute color purity (Max 64 colors, no anti-aliasing bleeding).

| 1024×1024 Cinematic Portal (Downscaled for preview) |
|---|
| <img src="examples/uc5_ultra/frames/portal_00.png" width="512"> |

```bash
python scripts/quality_audit.py --image portal_00.png --grid 8 --max-colors 64 --json
# Result: 1,048,576 pixels analyzed, 0 orphans, 33 unique colors -> PASS
```

---

### UC6: The Palette Multiverse (10 Palettes)
Using `palette_remap.py` to automatically recolor the same 64×64 HD Spellcaster sprite into **all 10 built-in game palettes**.

| Sweetie-16 | NES | GameBoy | PICO-8 | Commodore 64 |
|---|---|---|---|---|
| <img src="examples/uc6_palettes/wizard_sweetie-16_4x.png" width="128"> | <img src="examples/uc6_palettes/wizard_nes_4x.png" width="128"> | <img src="examples/uc6_palettes/wizard_gameboy_4x.png" width="128"> | <img src="examples/uc6_palettes/wizard_pico-8_4x.png" width="128"> | <img src="examples/uc6_palettes/wizard_commodore-64_4x.png" width="128"> |

| SNES | DB32 | Endesga-32 | Resurrect-64 | CGA |
|---|---|---|---|---|
| <img src="examples/uc6_palettes/wizard_snes_4x.png" width="128"> | <img src="examples/uc6_palettes/wizard_db32_4x.png" width="128"> | <img src="examples/uc6_palettes/wizard_endesga-32_4x.png" width="128"> | <img src="examples/uc6_palettes/wizard_resurrect-64_4x.png" width="128"> | <img src="examples/uc6_palettes/wizard_cga_4x.png" width="128"> |

---

### UC7: HTML Templates Showcase
The generated JSON files and Sprite Sheets from the commands above are natively compatible with our interactive HTML viewers.

1. **`templates/sprite_sheet.html`**: Load the `hero_east_sheet.png` and `hero_east_sheet.json` from UC2 to play back the 8-way run cycle directly in your browser.
2. **`templates/tilemap_preview.html`**: Drag and drop the `grass.png` from UC3 to paint massive tilemaps and test seamlessness in real-time.
3. **`templates/palette_viewer.html`**: Import `pico-8.json` or `db32.json` to view hex codes, RGB values, and color ramps.
