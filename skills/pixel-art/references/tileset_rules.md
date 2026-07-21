# Tileset Rules

Rules and conventions for creating pixel art tilesets compatible with game engines (Godot, Unity, Defold, Tiled).

## Grid Sizes

| Grid | Use Case |
|---|---|
| 8×8 | Micro environments, Game Boy style |
| 16×16 | Most common for 2D platformers and top-down RPGs |
| 32×32 | Detailed environments, larger tile features |
| 48×48 | Isometric tiles (diamond ratio 2:1, 48 wide × 24 tall) |

## Basic Tileset Layout

A minimal tileset for terrain should include:

```
┌────┬────┬────┐
│ TL │ TM │ TR │   Top-left, Top-middle, Top-right
├────┼────┼────┤
│ ML │ MM │ MR │   Mid-left, Center fill, Mid-right
├────┼────┼────┤
│ BL │ BM │ BR │   Bottom-left, Bottom-middle, Bottom-right
└────┴────┴────┘
```

The center tile (MM) must tile seamlessly in all directions.

## Wang Autotile Bitmask (47-tile blob)

For automatic terrain transitions, use a 47-tile blob tileset. Each tile is identified by a bitmask of its 8 neighbors:

```
NW  N  NE       Bit positions:
 W  ·  E        NW=1  N=2   NE=4
SW  S  SE       W=8         E=16
                SW=32 S=64  SE=128
```

Corner bits (NW, NE, SW, SE) only matter when both adjacent edge neighbors are filled. For example, NW only matters when both N and W are filled.

This reduces the theoretical 256 combinations to 47 unique visual tiles.

## Terrain Transitions

When two terrain types meet (e.g., grass → dirt), create transition tiles:
- 4 edges (N, S, E, W)
- 4 outer corners (NW, NE, SW, SE)
- 4 inner corners
- 1 center fill per terrain type

Total: 13 tiles minimum per terrain pair.

## Isometric Tiles

For isometric projection at 30°:
- Diamond shape: width = 2× height
- Standard: 64×32 or 48×24
- Tiles overlap: draw back-to-front (painter's algorithm)
- Coordinate transform: `screen_x = (tile_x - tile_y) * (tile_w / 2)`, `screen_y = (tile_x + tile_y) * (tile_h / 2)`

## Animated Tiles

For water, lava, or other animated terrain:
- Use 3–4 frames
- Place frames side-by-side in the tileset
- Frame duration: 200–400ms for water, 100–200ms for fire/lava
