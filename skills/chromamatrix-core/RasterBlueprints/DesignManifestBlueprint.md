# ChromaMatrix Core Design Manifest Blueprint

```markdown
# Asset Design Manifest Blueprint: Hero Knight (4-Way Directional State Machine)

## 1. Visual Identity & Luma Strategy
- **Target LumaLUT**: `pico8_fantasy_16`
- **Key Shades**:
  - Base Armor: `#83769C` (Lavender Gray)
  - Armor Highlights: `#C2C3C7` (Silver White)
  - Armor Shadows: `#1D2B53` (Midnight Navy)
  - Trim Accent: `#FFA300` (Gold Amber)
  - Cape: `#FF004D` (Crimson Red)

## 2. Animation State Machine Breakdown
- **Idle (4 frames, 6 fps)**: Breath bob, cape wave.
- **Walk (8 frames, 12 fps)**: 4-way direction stride cycles.
- **Jump Squash & Stretch (5 frames, 14 fps)**: Kinetic squash (0.8x1.2) and stretch (1.2x0.8).
- **Melee Slash (6 frames, 18 fps)**: Sword slash with arc trail particle.
- **Death (8 frames, 8 fps)**: Collapse and pixel fade dissolve.

## 3. Grid Bounds & Pivot Metrics
- **Frame Size**: 32x32 px
- **Pivot Point**: Bottom Center `(16, 30)`
- **Shadow Footprint**: Oval 12x4 px at `(10, 28)`
```
