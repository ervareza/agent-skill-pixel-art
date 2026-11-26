# Pixel Art Critique, QA Metrics & Hybrid Cleanup Pipeline

Quality pixel art is achieved through a tight **Render → Inspect → Critique → Fix** loop. Automated checks catch mechanical bugs; human/agent visual inspection catches silhouette, value, and animation flaws.

## 1. Automated Mechanical Checks (`quality_audit.py` & `engine/qa.py`)

| Check | What It Catches | Pass Target |
|---|---|---|
| Anti-Aliasing | Semi-transparent pixels (`0 < alpha < 255`) | `0` pixels |
| Orphan Pixels | Isolated pixels with zero opaque neighbors | `0` (except intentional particle sparks) |
| Palette Conformance | Color count overflow, off-palette pixels, near-duplicates (`tol <= 8`) | `0` off-palette |
| Grid Alignment | Canvas dimensions vs target grid (`--grid 1` allows 9×9, 12×12) | Aligned |
| Edge Doubles & Clipping | L-shaped doubled corner pixels; opaque pixels clipped at canvas borders | Clean margin |
| Animation Hygiene | Empty frames, identical adjacent frames, foot baseline drift, loop seam jump | `0px` foot drift |
| Tile Seamlessness | Color delta across left↔right and top↔bottom tile borders (`--check-seamless`) | Seamless wrap |

## 2. Cold-Read Visual Critique Rubric (Top 8 Checks)

Before looking at metadata, open the upscaled contact sheet (`preview_image()`):
1. **Silhouette Read:** Squint or view `silhouette_image()`. Can you immediately tell the subject, facing direction, and action without labels?
2. **Value Contrast:** Does the lit side separate clearly from the core shadow and background?
3. **Hue-Shifted Ramps:** Are shadows cooler (blue/purple) and highlights warmer (yellow/cream), or merely darker gray mud?
4. **Directional Consistency:** Does `up` (North) have ZERO face? Does `right`/`left` show a true profile with 1 eye? Are landmark rows (head/belt/feet) level across all views?
5. **Clean Lines & Clusters:** Even diagonal step runs (`2,2,2`), no random salt-and-pepper noise, no long parallel banding stripes.
6. **Gait & Weight (Animations):** Does the walk have a clear `pass` pose with one lifted foot and opposite arm swing? Does the head lag subtly behind the hip bob?
7. **Loop Seam:** Compare the last frame beside frame 1 on the contact sheet — motion must continue without snapping.
8. **1× Delivery Test:** Check the sprite at actual game size (`1×`–`2×`), not only zoomed `10×`.

## 3. Hybrid Cleanup Pipeline for Messy / AI-Generated PNGs (`sprite_clean.py`)

When cleaning output from an image generator or screenshot, execute strictly in this order:
1. **Recover True Pixel Grid** (`detect_scale` → fallback `block_downscale` modal color per block)
2. **Strip Baked Checkerboard** (`--strip-checker`)
3. **Harden Alpha** (`alpha >= 128 → 255`, else `0`)
4. **Despeckle** (remove 4-way connected clusters smaller than `min_cluster=2`)
5. **Dedupe Near-Identical Colors** (`tol=10`)
6. **Dehalo Edges** (replace low-saturation background-contaminated edge pixels with neighbor average)
7. **Lock Palette** (`--palette endesga-32` or `--max-colors 16`)
