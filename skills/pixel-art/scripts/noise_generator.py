#!/usr/bin/env python3
"""
Generate procedural noise textures for pixel art terrain.

Usage:
    python scripts/noise_generator.py --width 64 --height 64 --type perlin --scale 8 --output noise.png --json
    python scripts/noise_generator.py --width 128 --height 128 --type value --palette palettes/pico-8.json --output terrain.png --json
    python scripts/noise_generator.py --help
"""

import sys
import json
import math
import random
import argparse
from pathlib import Path
from PIL import Image


def lerp(a: float, b: float, t: float) -> float:
    return a + t * (b - a)


def fade(t: float) -> float:
    return t * t * t * (t * (t * 6 - 15) + 10)


class ValueNoise:
    """Simple value noise implementation (no external deps)."""

    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.perm = list(range(256))
        random.shuffle(self.perm)
        self.perm += self.perm
        self.values = [random.random() for _ in range(512)]

    def noise2d(self, x: float, y: float) -> float:
        xi, yi = int(math.floor(x)) & 255, int(math.floor(y)) & 255
        xf, yf = x - math.floor(x), y - math.floor(y)
        u, v = fade(xf), fade(yf)

        aa = self.values[self.perm[xi] + yi]
        ab = self.values[self.perm[xi] + yi + 1]
        ba = self.values[self.perm[xi + 1] + yi]
        bb = self.values[self.perm[xi + 1] + yi + 1]

        x1 = lerp(aa, ba, u)
        x2 = lerp(ab, bb, u)
        return lerp(x1, x2, v)

    def fbm(self, x: float, y: float, octaves: int = 4) -> float:
        value = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_val = 0.0
        for _ in range(octaves):
            value += self.noise2d(x * frequency, y * frequency) * amplitude
            max_val += amplitude
            amplitude *= 0.5
            frequency *= 2.0
        return value / max_val


def generate_noise(width: int, height: int, scale: float, seed: int, octaves: int, palette_colors: list = None) -> Image.Image:
    noise = ValueNoise(seed)
    img = Image.new("RGBA", (width, height))
    px = img.load()

    for x in range(width):
        for y in range(height):
            nx = x / scale
            ny = y / scale
            val = noise.fbm(nx, ny, octaves)
            val = max(0.0, min(1.0, val))

            if palette_colors:
                idx = int(val * (len(palette_colors) - 1))
                idx = max(0, min(len(palette_colors) - 1, idx))
                c = palette_colors[idx]
                px[x, y] = (c[0], c[1], c[2], 255)
            else:
                g = int(val * 255)
                px[x, y] = (g, g, g, 255)

    return img


def hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def main():
    parser = argparse.ArgumentParser(
        description="Generate procedural noise textures for pixel art terrain."
    )
    parser.add_argument("--width", type=int, required=True, help="Output width")
    parser.add_argument("--height", type=int, required=True, help="Output height")
    parser.add_argument("--scale", type=float, default=16.0, help="Noise scale (default: 16)")
    parser.add_argument("--octaves", type=int, default=4, help="FBM octaves (default: 4)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--palette", type=str, default="", help="Palette JSON to colorize noise (optional)")
    parser.add_argument("--output", type=str, required=True, help="Output PNG path")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    palette_colors = None
    if args.palette:
        pal_path = Path(args.palette)
        if not pal_path.exists():
            msg = f"Palette not found: {args.palette}"
            print(json.dumps({"status": "error", "message": msg}) if args.json else f"Error: {msg}")
            sys.exit(1)
        with open(pal_path) as f:
            pdata = json.load(f)
        palette_colors = [hex_to_rgb(c) for c in pdata["colors"]]

    try:
        img = generate_noise(args.width, args.height, args.scale, args.seed, args.octaves, palette_colors)
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out)

        result = {
            "status": "ok",
            "output": str(out),
            "size": [args.width, args.height],
            "scale": args.scale,
            "octaves": args.octaves,
            "seed": args.seed,
            "palette": args.palette or "grayscale",
            "file_size_bytes": out.stat().st_size,
        }
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Noise {args.width}×{args.height} → {out}")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
