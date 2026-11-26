#!/usr/bin/env python3
"""Remap image colors to a target palette using perceptual redmean distance (with optional Bayer dither)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine.canvas import SpriteDocument
from engine.color import load_palette


def main() -> None:
    parser = argparse.ArgumentParser(description="Remap image colors to a target palette (by name or JSON file).")
    parser.add_argument("--image", type=str, required=True, help="Source PNG path")
    parser.add_argument("--palette", type=str, required=True, help="Built-in palette name (e.g. pico-8) or palette JSON path")
    parser.add_argument("--output", type=str, required=True, help="Output PNG path")
    parser.add_argument("--dither", action="store_true", help="Apply subtle 4x4 Bayer dithering during remap")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        msg = f"Image not found: {args.image}"
        print(json.dumps({"status": "error", "message": msg}) if args.json else f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    try:
        pal_name, pal_rgbas = load_palette(args.palette)
        im = Image.open(image_path).convert("RGBA")
        doc = SpriteDocument(im.width, im.height, snap=False)
        doc.frames[0].cels["main"] = im
        doc.remap_to_palette(pal_rgbas, dither=args.dither)
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        doc.composite(1).save(out)
        res = {
            "status": "ok",
            "input": str(image_path),
            "output": str(out),
            "palette": pal_name,
            "palette_colors": len(pal_rgbas),
            "dither": args.dither,
        }
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Remapped {image_path.name} -> {out.name} ({pal_name}, {len(pal_rgbas)} colors)")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
