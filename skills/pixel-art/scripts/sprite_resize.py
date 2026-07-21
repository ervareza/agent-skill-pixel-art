#!/usr/bin/env python3
"""
Resize pixel art using nearest-neighbor interpolation ONLY.

Usage:
    python scripts/sprite_resize.py --input sprite.png --output sprite_2x.png --scale 2 --json
    python scripts/sprite_resize.py --input sprite.png --output sprite_4x.png --scale 4 --json
    python scripts/sprite_resize.py --help
"""

import sys
import json
import argparse
from pathlib import Path
from PIL import Image


def resize_sprite(input_path: Path, output_path: Path, scale: int) -> dict:
    img = Image.open(input_path).convert("RGBA")
    ow, oh = img.size
    nw, nh = ow * scale, oh * scale
    resized = img.resize((nw, nh), Image.Resampling.NEAREST)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    resized.save(output_path)
    return {
        "status": "ok",
        "input": str(input_path),
        "output": str(output_path),
        "original_size": [ow, oh],
        "new_size": [nw, nh],
        "scale": scale,
        "file_size_bytes": output_path.stat().st_size,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Resize pixel art using nearest-neighbor interpolation (no blurring)."
    )
    parser.add_argument("--input", type=str, required=True, help="Source PNG path")
    parser.add_argument("--output", type=str, required=True, help="Output PNG path")
    parser.add_argument("--scale", type=int, required=True, help="Scale factor (2, 3, 4, 8, etc.)")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    if args.scale < 1:
        msg = "Scale must be >= 1"
        print(json.dumps({"status": "error", "message": msg}) if args.json else f"Error: {msg}")
        sys.exit(1)

    input_path = Path(args.input)
    if not input_path.exists():
        msg = f"File not found: {args.input}"
        print(json.dumps({"status": "error", "message": msg}) if args.json else f"Error: {msg}")
        sys.exit(1)

    try:
        result = resize_sprite(input_path, Path(args.output), args.scale)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Resized {input_path.name} → {result['new_size'][0]}×{result['new_size'][1]} ({args.scale}×)")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
