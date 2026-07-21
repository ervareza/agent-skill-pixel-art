# PixelMatrix Engine — Canvas Constraints & Raster Rules

Strict canvas geometry, pixel grid alignment, outline rules, and color palette LUT constraints for AI Agents.

---

## 1. Canvas Dimensions & Grid Alignment

All generated pixel rasters MUST adhere strictly to standard grid dimensions:

| Preset Key | Grid Bounds | Projection Angle | Max Palette Count | Grid Snapping |
| :--- | :--- | :--- | :--- | :--- |
| `micro_icon_16` | 16x16 px | Orthographic | 8 Colors | 1 px |
| `standard_sprite_32` | 32x32 px | Orthographic | 16 Colors | 2 px |
| `isometric_axonometric_48` | 48x48 px | 30° Axonometric | 24 Colors | 2 px |
| `boss_entity_64` | 64x64 px | Orthographic | 32 Colors | 4 px |
| `scene_element_128` | 128x128 px | Illustration | 48 Colors | 4 px |
| `parallax_background_256` | 256x256 px | Seamless Loop | 64 Colors | 8 px |

---

## 2. Anti-Aliasing & Alpha Transparency Rules

- **Zero Anti-Aliasing (AA)**: Every pixel edge must be crisp and 100% opaque (`alpha = 255`) or 100% transparent (`alpha = 0`). Semi-transparent pixels (`0 < alpha < 255`) are strictly forbidden.
- **Orphan Pixel Ban**: Isolated single pixels surrounded by transparent canvas are prohibited unless explicitly representing micro particle debris.
- **Outline Consistency**: Outlines must be 1px solid dark values (preferably matched to the darkest shadow shade in the palette LUT, rather than pure `#000000` unless on GameBoy specs).

---

## 3. Color Palette LUT & Dithering Rules

- **Indexed Color Quantization**: All final asset exports must use indexed PNG format (`P` mode).
- **Color LUT Remapping**: Every color in the raster must map directly to one of the defined palette LUTs (`specs/palette_lut_definitions.json`).
- **Controlled Dithering**: Bayer 2x2 or 4x4 matrix dithering is permitted ONLY on background textures and dynamic lighting gradients. Character sprites must use flat cell shading with 2-3 shadow tones per color ramp.
