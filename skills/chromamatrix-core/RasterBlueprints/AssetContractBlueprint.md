# ChromaMatrix Core Asset Contract Blueprint

```yaml
contract_id: "CM-2026-001"
engine_version: "3.0.0"
timestamp: "2026-07-22T00:00:00Z"
status: "BOOTSTRAPPED"

asset_metadata:
  identifier: "hero_knight_sprite"
  category: "CHARACTER_SPRITE"
  target_engine: "Godot / Unity 2D"

specification:
  grid_matrix: "standard_sprite_32"
  dimensions: [32, 32]
  luma_palette: "pico8_fantasy_16"
  max_colors: 16
  sprite_core: "character_4way_matrix"

validation_criteria:
  grid_aligned: true
  zero_antialiasing: true
  zero_orphan_pixels: true
  indexed_png_export: true
```
