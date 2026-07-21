# Isometric Pixel Art Guide

Complete guide for creating isometric pixel art: projection, tile stacking, depth sorting, and character placement.

## Projection Angles

Pixel art isometric uses a **2:1 ratio** (not true 30° isometric). For every 2 pixels horizontal, go 1 pixel vertical.

```
True isometric: 30°     Pixel isometric: ~26.57° (atan(1/2))
     /\                       /\
    /  \                     /  \
   /    \                   /    \
```

The 2:1 ratio snaps perfectly to pixel grid — no sub-pixel artifacts.

## Tile Dimensions

| Tile Style | Diamond Size | Height (flat) | Notes |
|---|---|---|---|
| Small | 32×16 | 8px walls | Micro environments |
| Standard | 64×32 | 16px walls | Most common |
| Large | 128×64 | 32px walls | Detailed builds |

The "diamond" is the ground plane. Wall height is added on top.

## Diamond Construction

```
Step 1: Draw the diamond base      Step 2: Add wall height
        ···#····                           ···#····
        ··###···                           ··###···
        ·#####··                           ·#####··
        ·######·                           ·##┃##·
        ··####··                           ·#┃┃┃#·
        ···##···                           ·#┃┃┃#·
        ····#···                           ··┃┃┃··
                                           ··┃┃┃··
                                           ···#···
```

**Wall shading:** Left face = medium, Right face = light, Top face = lightest.
This creates consistent lighting from top-right.

## Coordinate System

```
Screen coordinates:
  screen_x = (tile_x - tile_y) * (tile_width / 2) + offset_x
  screen_y = (tile_x + tile_y) * (tile_height / 2) + offset_y

World to screen:
  tile_x =  (screen_x / (tile_width/2) + screen_y / (tile_height/2)) / 2
  tile_y = -(screen_x / (tile_width/2) - screen_y / (tile_height/2)) / 2
```

## Depth Sorting (Painter's Algorithm)

Draw tiles back-to-front:
1. Sort by `tile_y` ascending (back rows first)
2. Within same `tile_y`, sort by `tile_x` ascending (left first)
3. Within same tile position, sort by `tile_z` ascending (ground first, then objects on top)

```
Draw order:     (0,0) → (1,0) → (2,0)
                (0,1) → (1,1) → (2,1)
                (0,2) → (1,2) → (2,2)
```

## Stacking Tiles

For multi-level structures (buildings, terrain elevation):
- Each Z-level shifts the sprite UP by the wall height in pixels
- Tile at (x, y, z=1) draws at `screen_y - wall_height`
- Objects on elevated tiles must also be shifted

## Character Placement

Characters in isometric views should:
- Stand at the CENTER of the diamond, not the corner
- Cast shadows toward bottom-right (consistent with tile shading)
- Be approximately 1.5–2× the tile height for human-scale characters
- Use 8 directions: N, NE, E, SE, S, SW, W, NW

## Common Mistakes

1. **Wrong angle:** Using 1:1 (45°) instead of 2:1 — looks diamond but not isometric
2. **Inconsistent lighting:** Left wall dark + right wall dark. Pick ONE light source.
3. **Flat top faces:** Top surface of cubes must show the diamond grid pattern
4. **Character scale:** Characters too small or too large relative to tiles
5. **Z-fighting:** Overlapping sprites at same depth. Fix draw order.
