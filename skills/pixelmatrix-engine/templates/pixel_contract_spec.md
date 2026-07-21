# PixelMatrix Engine Asset Contract Specification

```yaml
contract_id: "PX-2026-001"
engine_version: "2.0.0"
timestamp: "2026-07-22T00:00:00Z"
status: "INITIALIZED"

asset_metadata:
  name: "hero_knight_sprite"
  category: "CHARACTER_SPRITE"
  target_engine: "Godot / Unity 2D"

specification:
  canvas_preset: "standard_sprite_32"
  dimensions: [32, 32]
  palette_lut: "pico8_fantasy_16"
  max_colors: 16
  sprite_matrix: "character_4way_matrix"

validation_criteria:
  grid_aligned: true
  zero_antialiasing: true
  zero_orphan_pixels: true
  indexed_png_export: true
```
