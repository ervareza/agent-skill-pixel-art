# Color Theory for Pixel Art

Practical color theory rules for creating readable, aesthetically pleasing pixel art with limited palettes.

## Hue Ramps

A hue ramp is a gradient from dark to light where each step shifts slightly in hue (not just brightness). This makes pixel art feel alive instead of flat.

**Warm ramp** (shadows shift toward blue/purple, highlights toward yellow):
```
Dark purple → Deep red → Orange → Yellow → Pale cream
```

**Cool ramp** (shadows shift toward blue, highlights toward cyan/white):
```
Dark navy → Blue → Teal → Cyan → White
```

## Contrast Rules

- **Minimum 3:1 contrast ratio** between adjacent colors that need to be distinguishable.
- **Outlines** should be darker than the darkest fill color. Use a desaturated dark tone, not pure black (#000000). Try dark blue (#1A1A2E) or dark brown (#2A1F1A).
- **Highlights** should be lighter and slightly warmer than the main fill.

## Palette Design Guidelines

1. **Start with 3 colors**: base, shadow, highlight. This covers 90% of a simple sprite.
2. **Add accent colors** sparingly. One warm accent + one cool accent is enough for most sprites.
3. **Keep palette cohesive**: All colors should look like they belong together. Use a shared underlying hue shift.
4. **Avoid pure colors**: Pure red (#FF0000), pure green (#00FF00), pure blue (#0000FF) look harsh. Desaturate slightly and shift hue.

## Dithering

Use ordered dithering (Bayer matrix) sparingly for gradients in backgrounds or large surfaces. Avoid dithering on small sprites — it adds visual noise at low resolutions.

**2×2 Bayer matrix** for subtle gradients:
```
0  2
3  1
```

**4×4 Bayer matrix** for smoother gradients:
```
 0  8  2 10
12  4 14  6
 3 11  1  9
15  7 13  5
```

Only dither between adjacent colors in your palette. Never dither between colors that are far apart.

## Common Palette Sizes

| Colors | Style | Examples |
|---|---|---|
| 2 | 1-bit monochrome | Black & white, stamp art |
| 4 | Game Boy era | DMG-01 green palette |
| 8 | Minimalist modern | CGA, limited jam palettes |
| 16 | Fantasy console | PICO-8, Sweetie 16 |
| 32 | Rich indie | ENDESGA 32 |
| 64 | Full spectrum | Resurrect 64, AAP-64 |
