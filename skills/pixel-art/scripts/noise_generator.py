#!/usr/bin/env python3
"""Generate guaranteed 4-edge seamless procedural noise textures (Toroidal FBM Value Noise & Toroidal Voronoi).

Usage:
    python scripts/noise_generator.py --width 64 --height 64 --type value --scale 16 --palette pico-8 --output terrain.png --json
    python scripts/noise_generator.py --width 64 --height 64 --type voronoi --cells 10 --palette endesga-32 --output stone.png --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine.color import load_palette
from engine.tileset import toroidal_value_noise, toroidal_voronoi


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate 4-edge seamless toroidal procedural noise textures for pixel art terrain.")
    parser.add_argument("--width", type=int, required=True, help="Output width")
    parser.add_argument("--height", type=int, required=True, help="Output height")
    parser.add_argument("--type", type=str, default="value", choices=["value", "perlin", "voronoi"], help="Noise algorithm (default: value)")
    parser.add_argument("--scale", type=float, default=16.0, help="Noise cell size in pixels (default: 16)")
    parser.add_argument("--octaves", type=int, default=3, help="FBM octaves (default: 3)")
    parser.add_argument("--cells", type=int, default=9, help="Voronoi cell count (for --type voronoi)")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic seed (default: 42)")
    parser.add_argument("--palette", type=str, default="", help="Palette name or JSON path to colorize noise")
    parser.add_argument("--output", type=str, required=True, help="Output PNG path")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    try:
        pal_rgbas = load_palette(args.palette)[1] if args.palette else None
        w, h = args.width, args.height

        if args.type == "voronoi":
            ed, _ = toroidal_voronoi(w, h, cells=args.cells, seed=args.seed)
            max_d = max(1e-6, max(max(row) for row in ed))
            field = [[min(1.0, ed[y][x] / max_d) for x in range(w)] for y in range(h)]
        else:
            px_per = max(2, round(w / max(2.0, args.scale)))
            py_per = max(2, round(h / max(2.0, args.scale)))
            field = toroidal_value_noise(w, h, period_x=px_per, period_y=py_per, octaves=args.octaves, seed=args.seed)

        img = Image.new("RGBA", (w, h))
        px = img.load()
        for y in range(h):
            for x in range(w):
                v = field[y][x]
                if pal_rgbas:
                    idx = max(0, min(len(pal_rgbas) - 1, int(v * len(pal_rgbas))))
                    c = pal_rgbas[idx]
                    px[x, y] = (c[0], c[1], c[2], 255)
                else:
                    g = int(v * 255)
                    px[x, y] = (g, g, g, 255)

        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out)

        res = {
            "status": "ok",
            "output": str(out),
            "size": [w, h],
            "type": args.type,
            "seamless": True,
            "scale": args.scale,
            "octaves": args.octaves,
            "seed": args.seed,
            "palette": args.palette or "grayscale",
            "file_size_bytes": out.stat().st_size,
        }
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Seamless {args.type} noise {w}x{h} -> {out}")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
