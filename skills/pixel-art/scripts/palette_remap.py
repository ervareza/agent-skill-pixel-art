#!/usr/bin/env python3
"""
Remap image colors to the nearest color in a target palette using Euclidean RGB distance.

Usage:
    python scripts/palette_remap.py --image input.png --palette palettes/pico-8.json --output remapped.png --json
    python scripts/palette_remap.py --help
"""

import sys
import json
import math
import argparse
from pathlib import Path
from PIL import Image


def hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def nearest_color(pixel_rgb: tuple, palette_rgbs: list) -> tuple:
    best = palette_rgbs[0]
    best_dist = float("inf")
    for p in palette_rgbs:
        dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(pixel_rgb, p)))
        if dist < best_dist:
            best_dist = dist
            best = p
    return best


def remap_image(img: Image.Image, palette_rgbs: list) -> Image.Image:
    out = img.copy()
    px = out.load()
    w, h = out.size
    for x in range(w):
        for y in range(h):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            nr, ng, nb = nearest_color((r, g, b), palette_rgbs)
            px[x, y] = (nr, ng, nb, a)
    return out


def main():
    parser = argparse.ArgumentParser(
        description="Remap image colors to the nearest color in a target palette."
    )
    parser.add_argument("--image", type=str, required=True, help="Source PNG image path")
    parser.add_argument("--palette", type=str, required=True, help="Palette JSON file path")
    parser.add_argument("--output", type=str, required=True, help="Output PNG image path")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    image_path = Path(args.image)
    palette_path = Path(args.palette)

    if not image_path.exists():
        msg = f"Image not found: {args.image}"
        print(json.dumps({"status": "error", "message": msg}) if args.json else f"Error: {msg}")
        sys.exit(1)

    if not palette_path.exists():
        msg = f"Palette not found: {args.palette}"
        print(json.dumps({"status": "error", "message": msg}) if args.json else f"Error: {msg}")
        sys.exit(1)

    try:
        with open(palette_path, "r") as f:
            palette_data = json.load(f)
        palette_rgbs = [hex_to_rgb(c) for c in palette_data["colors"]]

        img = Image.open(image_path).convert("RGBA")
        remapped = remap_image(img, palette_rgbs)

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        remapped.save(output_path)

        result = {
            "status": "ok",
            "input": str(image_path),
            "output": str(output_path),
            "palette": palette_data["name"],
            "palette_colors": len(palette_data["colors"]),
        }

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Remapped {image_path.name} → {output_path.name} using {palette_data['name']} palette")

        sys.exit(0)

    except Exception as e:
        msg = str(e)
        print(json.dumps({"status": "error", "message": msg}) if args.json else f"Error: {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
