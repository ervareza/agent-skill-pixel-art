#!/usr/bin/env python3
"""
Add a 1px outline around opaque pixels in a sprite.

Usage:
    python scripts/outline_generator.py --input sprite.png --output outlined.png --json
    python scripts/outline_generator.py --input sprite.png --output outlined.png --color "#1A1A2E" --json
    python scripts/outline_generator.py --help
"""

import sys
import json
import argparse
from pathlib import Path
from PIL import Image


def hex_to_rgba(h: str) -> tuple:
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r, g, b, 255)


def add_outline(input_path: Path, output_path: Path, color: tuple) -> dict:
    src = Image.open(input_path).convert("RGBA")
    sw, sh = src.size
    spx = src.load()

    # Create output with 2px extra on each side for the outline
    out = Image.new("RGBA", (sw + 2, sh + 2), (0, 0, 0, 0))
    opx = out.load()

    # Pass 1: draw outline pixels
    for x in range(sw):
        for y in range(sh):
            if spx[x, y][3] > 0:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        ox, oy = x + 1 + dx, y + 1 + dy
                        if opx[ox, oy][3] == 0:
                            opx[ox, oy] = color

    # Pass 2: paste original sprite on top (offset by 1)
    for x in range(sw):
        for y in range(sh):
            if spx[x, y][3] > 0:
                opx[x + 1, y + 1] = spx[x, y]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.save(output_path)

    return {
        "status": "ok",
        "input": str(input_path),
        "output": str(output_path),
        "original_size": [sw, sh],
        "outlined_size": [sw + 2, sh + 2],
        "outline_color": f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Add a 1px outline around opaque pixels in a sprite."
    )
    parser.add_argument("--input", type=str, required=True, help="Source PNG path")
    parser.add_argument("--output", type=str, required=True, help="Output PNG path")
    parser.add_argument("--color", type=str, default="#1A1A2E", help="Outline color as hex (default: #1A1A2E dark blue)")
    parser.add_argument("--inset", action="store_true", help="Draw outline inside the sprite bounds (no size increase)")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        msg = f"File not found: {args.input}"
        print(json.dumps({"status": "error", "message": msg}) if args.json else f"Error: {msg}")
        sys.exit(1)

    try:
        color = hex_to_rgba(args.color)
        result = add_outline(input_path, Path(args.output), color)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Outlined {input_path.name} → {result['outlined_size'][0]}×{result['outlined_size'][1]}")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
