# PixelMatrix Engine Sprite Design Manifest Blueprint

```markdown
# Asset Design Specification: Hero Knight (4-Way Directional Matrix)

## 1. Visual Identity & Palette Strategy
- **Target Palette LUT**: `pico8_fantasy_16`
- **Key Shades**:
  - Base Armor: `#83769C` (Lavender Gray)
  - Armor Highlights: `#C2C3C7` (Silver White)
  - Armor Shadows: `#1D2B53` (Midnight Navy)
  - Trim/Visor Accent: `#FFA300` (Gold Amber)
  - Cape: `#FF004D` (Crimson Red)

## 2. Animation Matrix Breakdown
- **Idle (4 frames, 6 fps)**: Subtle breath bob, cape wave.
- **Walk (8 frames, 12 fps)**: 4-way direction stride cycles.
- **Melee Attack (6 frames, 18 fps)**: Sword slash with arc trail particle.
- **Death (8 frames, 8 fps)**: Collapse and pixel fade dissolve.

## 3. Grid & Anchor Specs
- **Frame Size**: 32x32 px
- **Pivot Point**: Bottom Center `(16, 30)`
- **Shadow Footprint**: Oval 12x4 px at `(10, 28)`
```
