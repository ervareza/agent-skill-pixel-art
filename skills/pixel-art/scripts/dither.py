#!/usr/bin/env python3
"""
Apply ordered dithering (Bayer matrix) between two colors.

Usage:
    python scripts/dither.py --width 64 --height 64 --color1 "#1D2B53" --color2 "#7E2553" --output gradient.png --json
    python scripts/dither.py --width 128 --height 32 --color1 "#000000" --color2 "#FFFFFF" --matrix 4 --output dither4.png --json
    python scripts/dither.py --help
"""

import sys
import json
import argparse
from pathlib import Path
from PIL import Image


BAYER_2X2 = [
    [0, 2],
    [3, 1],
]

BAYER_4X4 = [
    [0,  8,  2, 10],
    [12, 4, 14,  6],
    [3, 11,  1,  9],
    [15, 7, 13,  5],
]


def hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def generate_dither(width: int, height: int, c1: tuple, c2: tuple, matrix_size: int = 4) -> Image.Image:
    bayer = BAYER_4X4 if matrix_size == 4 else BAYER_2X2
    n = len(bayer)
    levels = n * n

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    px = img.load()

    for x in range(width):
        t = x / max(width - 1, 1)  # gradient from left to right
        for y in range(height):
            threshold = bayer[y % n][x % n] / levels
            if t > threshold:
                px[x, y] = (c2[0], c2[1], c2[2], 255)
            else:
                px[x, y] = (c1[0], c1[1], c1[2], 255)

    return img


def main():
    parser = argparse.ArgumentParser(
        description="Generate an ordered dithered gradient between two colors using a Bayer matrix."
    )
    parser.add_argument("--width", type=int, required=True, help="Output width in pixels")
    parser.add_argument("--height", type=int, required=True, help="Output height in pixels")
    parser.add_argument("--color1", type=str, required=True, help="Start color (hex)")
    parser.add_argument("--color2", type=str, required=True, help="End color (hex)")
    parser.add_argument("--matrix", type=int, default=4, choices=[2, 4], help="Bayer matrix size: 2 or 4 (default: 4)")
    parser.add_argument("--output", type=str, required=True, help="Output PNG path")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    try:
        c1 = hex_to_rgb(args.color1)
        c2 = hex_to_rgb(args.color2)
        img = generate_dither(args.width, args.height, c1, c2, args.matrix)
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out)

        result = {
            "status": "ok",
            "output": str(out),
            "size": [args.width, args.height],
            "color1": args.color1,
            "color2": args.color2,
            "matrix": f"{args.matrix}x{args.matrix}",
            "file_size_bytes": out.stat().st_size,
        }
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Dithered {args.width}×{args.height} → {out}")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
