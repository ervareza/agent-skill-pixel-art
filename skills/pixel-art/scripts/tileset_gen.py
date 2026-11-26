#!/usr/bin/env python3
"""Generate seamless terrain tiles, 16-tile Wang / 47-tile Blob autotiles, animated tiles, and 2:1 isometric blocks.

Usage:
    python scripts/tileset_gen.py --terrain grass --size 16 --mode wang16 --palette endesga-32 --output grass_autotile.png --json
    python scripts/tileset_gen.py --terrain stone --size 32 --mode blob47 --output stone_47.png --json
    python scripts/tileset_gen.py --terrain water --size 16 --mode animated --frames 6 --fps 6 --output water_loop.png --gif --json
    python scripts/tileset_gen.py --terrain grass --size 64 --mode isometric --output iso_grass.png --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.exporters import export_gif, export_spritesheet
from engine.qa import audit_image
from engine.tileset import (
    TERRAIN_PRESETS,
    generate_animated_tile,
    generate_autotile_sheet,
    generate_isometric_block,
    generate_seamless_tile,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate seamless pixel art tiles, Wang/Blob autotiles, animated tiles, and isometric blocks.")
    parser.add_argument("--terrain", type=str, default="grass", choices=sorted(TERRAIN_PRESETS.keys()), help="Terrain preset")
    parser.add_argument("--size", type=int, default=16, help="Tile size in pixels (default: 16; use 32/64 for isometric)")
    parser.add_argument("--mode", type=str, default="single", choices=["single", "wang16", "blob47", "animated", "isometric"], help="Generation mode")
    parser.add_argument("--frames", type=int, default=6, help="Frame count for animated tiles (default: 6)")
    parser.add_argument("--fps", type=int, default=6, help="FPS for animated tiles (default: 6)")
    parser.add_argument("--wall-height", type=int, default=0, help="Wall height in px for isometric mode (0 = auto)")
    parser.add_argument("--palette", type=str, default="endesga-32", help="Palette name/JSON or 'none'")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic seed")
    parser.add_argument("--gif", action="store_true", help="Also export animated GIF (for animated mode)")
    parser.add_argument("--gif-scale", type=int, default=4, help="GIF upscale factor")
    parser.add_argument("--output", type=str, required=True, help="Output PNG path")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    try:
        pal = None if args.palette.lower() == "none" else args.palette
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        res: dict = {"status": "ok", "terrain": args.terrain, "mode": args.mode, "output": str(out)}

        if args.mode == "single":
            tile = generate_seamless_tile(size=args.size, terrain=args.terrain, palette=pal, seed=args.seed)
            tile.save(out)
            res["size"] = [tile.width, tile.height]
            res["qa"] = audit_image(tile, grid_size=1, palette=pal, check_seamless=True)

        elif args.mode in ("wang16", "blob47"):
            sheet, meta = generate_autotile_sheet(tile_size=args.size, terrain=args.terrain, mode=args.mode, palette=pal, seed=args.seed)
            sheet.save(out)
            meta_path = out.with_suffix(".json")
            meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
            res["sheet_size"] = [sheet.width, sheet.height]
            res["tile_count"] = meta["tile_count"]
            res["metadata"] = str(meta_path)

        elif args.mode == "animated":
            doc = generate_animated_tile(size=args.size, terrain=args.terrain, frames=args.frames, fps=args.fps, palette=pal, seed=args.seed)
            res["sheet"] = export_spritesheet(doc, out, cols=args.frames)
            if args.gif:
                gif_path = out.with_suffix(".gif")
                imgs = [doc.composite(i + 1) for i in range(doc.n_frames)]
                durs = [f.duration_ms for f in doc.frames]
                res["gif"] = export_gif(imgs, gif_path, durations_ms=durs, scale=args.gif_scale)

        elif args.mode == "isometric":
            wh = args.wall_height if args.wall_height > 0 else None
            iso = generate_isometric_block(width=args.size, terrain=args.terrain, wall_height=wh, palette=pal, seed=args.seed)
            iso.save(out)
            res["size"] = [iso.width, iso.height]
            res["qa"] = audit_image(iso, grid_size=1, palette=pal)

        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Generated {args.terrain} ({args.mode}) -> {out}")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
