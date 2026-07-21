# Artistic Pixel Art Generation Guide

A comprehensive guide for generating commercial-grade, artistic 2D pixel art sprites, tilesets, foliage, characters, and VFX.

---

## 1. Core Principles of Professional Pixel Art

### A. Cluster Shading (Not Per-Pixel Noise)
- **Do NOT scatter single pixels randomly.** Pixel art reads best when pixels form distinct **clusters** (contiguous color patches).
- Group pixels into light, mid-tone, and shadow masses to define form and volume.
- Avoid "salt-and-pepper" noise or random dithering on small sprites.

### B. Hue Shifting
Never adjust brightness alone (e.g. RGB `(100,0,0)` to `(200,0,0)`).
- **Highlights**: Shift hue toward **warm** (yellow/gold/cyan), increase brightness, slightly lower saturation.
- **Shadows**: Shift hue toward **cool** (blue/purple/violet), decrease brightness, increase saturation.
- *Example for Green Foliage*:
  - Highlight: Bright Lime Green (`#A7F070`)
  - Base: Mid Emerald (`#38B764`)
  - Shadow: Cool Deep Teal (`#257179`)
  - Deep Shadow: Dark Navy-Blue (`#1A1C2C`)

### C. Selective Outlining (Selout)
- Outlines don't have to be flat black.
- Use **Selective Outlining**: Light outline where light hits the sprite, dark outline on shaded sides.
- Makes sprites pop against both light and dark backgrounds.

---

## 2. Procedural Organic Generation Algorithms

When generating pixel art programmatically (via Python scripts or AI agents), use these math-backed artistic algorithms:

### A. Foliage & Tree Generation (Sakura, Willow, Oak, Pine, Bamboo)
Trees are composed of 3 layers:
1. **Trunk & Branches**: Organic curved paths with bark shading (highlight left/top, dark right/bottom).
2. **Foliage Clusters**: Overlapping circular or elliptical blobs of varying radii.
3. **Cluster Shading**:
   - Each leaf cluster gets its own 3-tone gradient (top-left highlight, center base, bottom-right shadow).
   - Add scattered falling leaves/petals (1-3% density) for dynamism.

```python
# Pseudo-algorithm for organic foliage cluster
def draw_foliage_cluster(canvas, center_x, center_y, radius, palette_ramp):
    for dx in range(-radius, radius+1):
        for dy in range(-radius, radius+1):
            dist = (dx*dx + dy*dy) ** 0.5
            if dist <= radius:
                # Angle and distance determine shade
                shade_val = (dx - dy) / (radius * 1.414) # -1 (top-left light) to +1 (bottom-right shadow)
                if shade_val < -0.3:
                    color = palette_ramp['highlight']
                elif shade_val < 0.3:
                    color = palette_ramp['base']
                elif shade_val < 0.7:
                    color = palette_ramp['shadow']
                else:
                    color = palette_ramp['dark_shadow']
                canvas.set_pixel(center_x + dx, center_y + dy, color)
```

### B. Voronoi Cells for Stone Paths & Bricks
For cobblestone, cracked clay, tiles, and dragon scales:
1. Place $N$ random feature points on the canvas (wrapping coordinates for seamless tiles).
2. For each pixel, calculate distance to nearest feature point (using Manhattan or Euclidean distance with 4-edge wrapping).
3. Border pixels (where distance to 1st nearest $\approx$ distance to 2nd nearest) become **grout/mortar lines** (dark color).
4. Cell interiors get shaded based on light direction (light top-left, shadow bottom-right).

### C. Low-Frequency Value Noise for Terrain (Grass, Sand, Dirt, Water)
- Use **Value Noise + Cosine Interpolation** wrapped across edges for seamless tiling.
- Multi-tier color distribution:
  - **70% Base color**
  - **15% Dark accent (-1 step)**
  - **10% Light accent (+1 step)**
  - **5% Deep feature / detail**

---

## 3. Character & Creature Design Rules

### A. Proportions & Grid Scale
- **16×16**: Minimalist / Chibi (head 50% of height, body 50%).
- **32×32**: Retro Hero (head 35%, torso 35%, legs 30%).
- **64×64**: Detailed RPG Character / Boss (head 25%, torso 40%, legs 35%, detailed face/gear).

### B. Action Frames & Key Poses
- **Idle**: 2–4 frames (subtle 1px chest bob + weapon idle).
- **Walk/Run**: 4–6 frames (contact frame → recoil → passing → high point).
- **Wind Sway (Trees/Plants)**: 4–6 frames (sine wave distortion `dx = sin(time + y * 0.1) * amplitude`).

---

## 4. Quality Audit Standards

Every generated pixel asset must pass:
1. **Zero anti-aliasing**: 100% opaque or 100% transparent pixels.
2. **Palette Quantization**: All colors strictly belong to the chosen palette.
3. **Seamless Tiling (for tiles)**: 2×2 grid check produces no visible seam lines.
4. **Readable Silhouette**: Recognizable as a solid dark fill.
