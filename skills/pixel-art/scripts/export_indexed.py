#!/usr/bin/env python3
"""
Convert an RGBA PNG to an indexed 8-bit PNG with optional color reduction.

Usage:
    python scripts/export_indexed.py --input sprite.png --output sprite_indexed.png --json
    python scripts/export_indexed.py --input sprite.png --output out.png --max-colors 16 --json
    python scripts/export_indexed.py --help
"""

import sys
import json
import argparse
from pathlib import Path
from PIL import Image


def export_indexed(input_path: Path, output_path: Path, max_colors: int = 256) -> dict:
    img = Image.open(input_path).convert("RGBA")
    original_w, original_h = img.size

    # Count unique opaque colors
    pixels = img.getdata()
    unique = set()
    for r, g, b, a in pixels:
        if a > 0:
            unique.add((r, g, b))
    original_color_count = len(unique)

    # Quantize to indexed palette
    quantized = img.quantize(colors=min(max_colors, 256), method=Image.Quantize.MEDIANCUT)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    quantized.save(output_path)

    return {
        "status": "ok",
        "input": str(input_path),
        "output": str(output_path),
        "original_colors": original_color_count,
        "indexed_colors": min(max_colors, original_color_count),
        "dimensions": [original_w, original_h],
        "file_size_bytes": output_path.stat().st_size,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Convert an RGBA PNG to an indexed 8-bit PNG with optional color reduction."
    )
    parser.add_argument("--input", type=str, required=True, help="Source RGBA PNG path")
    parser.add_argument("--output", type=str, required=True, help="Output indexed PNG path")
    parser.add_argument("--max-colors", type=int, default=256, help="Maximum colors in indexed palette (default: 256)")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        msg = f"File not found: {args.input}"
        print(json.dumps({"status": "error", "message": msg}) if args.json else f"Error: {msg}")
        sys.exit(1)

    try:
        result = export_indexed(input_path, Path(args.output), args.max_colors)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Exported {input_path.name} → {Path(args.output).name} ({result['indexed_colors']} colors)")
        sys.exit(0)
    except Exception as e:
        msg = str(e)
        print(json.dumps({"status": "error", "message": msg}) if args.json else f"Error: {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
