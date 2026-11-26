#!/usr/bin/env python3
"""Convert an RGBA PNG to an indexed 8-bit PNG while PRESERVING alpha transparency."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine.exporters import export_indexed_png


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert an RGBA PNG to an indexed 8-bit PNG with preserved transparency.")
    parser.add_argument("--input", type=str, required=True, help="Source RGBA PNG path")
    parser.add_argument("--output", type=str, required=True, help="Output indexed PNG path")
    parser.add_argument("--max-colors", type=int, default=256, help="Maximum colors in indexed palette (default: 256)")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        msg = f"File not found: {args.input}"
        print(json.dumps({"status": "error", "message": msg}) if args.json else f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    try:
        img = Image.open(input_path).convert("RGBA")
        result = export_indexed_png(img, Path(args.output), max_colors=args.max_colors)
        result["input"] = str(input_path)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Exported {input_path.name} -> {Path(args.output).name} ({result['indexed_colors']} colors, transparent={result['transparent']})")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
