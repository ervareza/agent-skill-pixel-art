#!/usr/bin/env python3
"""Add a 1px solid, inset, or selective (selout) outline + optional rim light around a sprite.

Usage:
    python scripts/outline_generator.py --input sprite.png --output outlined.png --color "#1A1A2E" --json
    python scripts/outline_generator.py --input sprite.png --output selout.png --mode selout --rim-light --json
    python scripts/outline_generator.py --input sprite.png --output inset.png --inset --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine.canvas import SpriteDocument


def main() -> None:
    parser = argparse.ArgumentParser(description="Add a crisp 1px outside, inset, or selective hue-shifted outline (+ optional rim light).")
    parser.add_argument("--input", type=str, required=True, help="Source PNG path")
    parser.add_argument("--output", type=str, required=True, help="Output PNG path")
    parser.add_argument("--color", type=str, default="#1E182B", help="Outline color hex (default: #1E182B)")
    parser.add_argument("--mode", type=str, default="outside", choices=["outside", "inset", "selout"], help="Outline mode (default: outside)")
    parser.add_argument("--inset", action="store_true", help="Alias for --mode inset (draw inside sprite bounds, no size increase)")
    parser.add_argument("--diagonals", action="store_true", help="Include 8-way diagonal corner pixels")
    parser.add_argument("--rim-light", action="store_true", help="Add directional top-left rim highlight before outlining")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        msg = f"File not found: {args.input}"
        print(json.dumps({"status": "error", "message": msg}) if args.json else f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    try:
        src = Image.open(input_path).convert("RGBA")
        sw, sh = src.size
        mode = "inset" if args.inset else args.mode

        if mode == "inset":
            doc = SpriteDocument(sw, sh, snap=False)
            doc.frames[0].cels["main"] = src
            if args.rim_light:
                doc.rim_light()
            doc.outline(args.color, where="inside", diagonals=args.diagonals)
        else:
            doc = SpriteDocument(sw + 2, sh + 2, snap=False)
            doc.paste_image(src, 1, 1)
            if args.rim_light:
                doc.rim_light()
            if mode == "selout":
                doc.selout(dark_color=args.color, diagonals=args.diagonals)
            else:
                doc.outline(args.color, where="outside", diagonals=args.diagonals)

        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_img = doc.composite(1)
        out_img.save(out_path)

        res = {
            "status": "ok",
            "input": str(input_path),
            "output": str(out_path),
            "mode": mode,
            "rim_light": args.rim_light,
            "original_size": [sw, sh],
            "outlined_size": [out_img.width, out_img.height],
            "outline_color": args.color,
        }
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Outlined ({mode}) {input_path.name} -> {out_img.width}x{out_img.height}")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
