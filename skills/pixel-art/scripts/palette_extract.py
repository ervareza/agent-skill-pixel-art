#!/usr/bin/env python3
"""
Extract the color palette from an existing image.

Usage:
    python scripts/palette_extract.py --image reference.png --json
    python scripts/palette_extract.py --image reference.png --max-colors 16 --output extracted.json --json
    python scripts/palette_extract.py --help
"""

import sys
import json
import argparse
from pathlib import Path
from PIL import Image


def extract_palette(input_path: Path, max_colors: int = 256) -> dict:
    img = Image.open(input_path).convert("RGBA")
    w, h = img.size
    px = img.load()

    colors = {}
    total_opaque = 0
    for x in range(w):
        for y in range(h):
            r, g, b, a = px[x, y]
            if a > 0:
                total_opaque += 1
                hex_c = f"#{r:02X}{g:02X}{b:02X}"
                colors[hex_c] = colors.get(hex_c, 0) + 1

    sorted_colors = sorted(colors.items(), key=lambda x: -x[1])
    top_colors = [c for c, _ in sorted_colors[:max_colors]]

    palette = {
        "name": input_path.stem,
        "max_colors": len(top_colors),
        "colors": top_colors,
    }

    return {
        "status": "ok",
        "source": str(input_path),
        "total_unique_colors": len(colors),
        "extracted_colors": len(top_colors),
        "palette": palette,
        "color_frequency": [{"color": c, "pixels": n, "percent": round(n / max(total_opaque, 1) * 100, 1)} for c, n in sorted_colors[:max_colors]],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract the color palette from an existing PNG image."
    )
    parser.add_argument("--image", type=str, required=True, help="Source image path")
    parser.add_argument("--max-colors", type=int, default=256, help="Maximum colors to extract (default: 256)")
    parser.add_argument("--output", type=str, default="", help="Save palette as JSON file (optional)")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    input_path = Path(args.image)
    if not input_path.exists():
        msg = f"File not found: {args.image}"
        print(json.dumps({"status": "error", "message": msg}) if args.json else f"Error: {msg}")
        sys.exit(1)

    try:
        result = extract_palette(input_path, args.max_colors)

        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w") as f:
                json.dump(result["palette"], f, indent=2)
            result["saved_to"] = str(out_path)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Extracted {result['extracted_colors']} colors from {input_path.name}")
            for cf in result["color_frequency"][:10]:
                print(f"  {cf['color']} — {cf['percent']}% ({cf['pixels']}px)")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
