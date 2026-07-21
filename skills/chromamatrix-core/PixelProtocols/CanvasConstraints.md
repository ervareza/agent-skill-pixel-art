# ChromaMatrix Core — Canvas Constraints & Voxel Rules

Canvas geometry, pixel grid snapping, outline rules, and color palette LUT constraints.

---

## 1. Canvas Dimensions & Grid Bounds

All generated pixel rasters MUST adhere strictly to standard grid dimensions:

| Grid Matrix Key | Canvas Bounds | Projection Angle | Max Palette Count | Grid Snapping |
| :--- | :--- | :--- | :--- | :--- |
| `micro_icon_8` | 8x8 px | Orthographic | 4 Colors | 1 px |
| `standard_sprite_16` | 16x16 px | Orthographic | 12 Colors | 1 px |
| `standard_sprite_32` | 32x32 px | Orthographic | 16 Colors | 2 px |
| `isometric_axonometric_48` | 48x48 px | 30° Axonometric | 24 Colors | 2 px |
| `boss_entity_64` | 64x64 px | Orthographic | 32 Colors | 4 px |
| `hd_pixel_scene_128` | 128x128 px | Illustration | 48 Colors | 4 px |

---

## 2. Anti-Aliasing & Transparency Protocols

- **Zero Anti-Aliasing (AA)**: Every pixel edge must be crisp and 100% opaque (`alpha = 255`) or 100% transparent (`alpha = 0`). Semi-transparent pixels (`0 < alpha < 255`) are strictly forbidden.
- **Isolated Orphan Pixel Purge**: Single isolated pixels with zero opaque 8-way neighbors are prohibited unless representing micro particle debris.
- **Solid Outlines**: Outlines must be 1px solid values (preferably matched to the darkest shadow shade in the LumaLUT).

---

## 3. Color Palette LUT & Dithering Protocols

- **Indexed Color Quantization**: All final asset exports must use indexed PNG format (`P` mode).
- **LumaLUT Remapping**: Every color in the raster must map directly to one of the defined LumaLUTs (`ManifestVault/LumaPalettes.json`).
- **Controlled Dithering**: Bayer 2x2 or 4x4 dithering is permitted ONLY on background textures and dynamic lighting gradients.
