#!/usr/bin/env python3
"""Generate ordered Bayer (2x2 / 4x4 / 8x8) or band-edge dithered pixel art gradients."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine.canvas import SpriteDocument
from engine.color import hue_ramp


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an ordered Bayer or band-edge dithered gradient.")
    parser.add_argument("--width", type=int, required=True, help="Output width in pixels")
    parser.add_argument("--height", type=int, required=True, help="Output height in pixels")
    parser.add_argument("--color1", type=str, required=True, help="Start color (hex)")
    parser.add_argument("--color2", type=str, required=True, help="End color (hex)")
    parser.add_argument("--matrix", type=int, default=4, choices=[2, 4, 8], help="Bayer matrix size: 2, 4, or 8 (default: 4)")
    parser.add_argument("--axis", type=str, default="h", choices=["h", "v"], help="Gradient direction: h (horizontal) or v (vertical)")
    parser.add_argument("--strip", type=float, default=1.0, help="Dither transition band width (0.25 = Codixel band-edge, 1.0 = full gradient)")
    parser.add_argument("--output", type=str, required=True, help="Output PNG path")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    try:
        doc = SpriteDocument(args.width, args.height, snap=False)
        pattern = f"bayer{args.matrix}"
        doc.band_dither(0, 0, args.width - 1, args.height - 1, [args.color1, args.color2], axis=args.axis, strip=args.strip, pattern=pattern)
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        doc.composite(1).save(out)
        res = {
            "status": "ok",
            "output": str(out),
            "size": [args.width, args.height],
            "color1": args.color1,
            "color2": args.color2,
            "matrix": f"{args.matrix}x{args.matrix}",
            "axis": args.axis,
            "strip": args.strip,
            "file_size_bytes": out.stat().st_size,
        }
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Dithered {args.width}x{args.height} ({pattern}) -> {out}")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
