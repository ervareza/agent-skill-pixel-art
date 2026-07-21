#!/usr/bin/env python3
"""
Mirror a sprite horizontally or vertically.

Usage:
    python scripts/sprite_mirror.py --input sprite_east.png --output sprite_west.png --axis horizontal --json
    python scripts/sprite_mirror.py --input sprite.png --output sprite_flip.png --axis vertical --json
    python scripts/sprite_mirror.py --input-dir ./east_frames/ --output-dir ./west_frames/ --axis horizontal --json
    python scripts/sprite_mirror.py --help
"""

import sys
import json
import argparse
from pathlib import Path
from PIL import Image


def mirror_image(img: Image.Image, axis: str) -> Image.Image:
    if axis == "horizontal":
        return img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    elif axis == "vertical":
        return img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    else:
        raise ValueError(f"Invalid axis: {axis}. Use 'horizontal' or 'vertical'.")


def main():
    parser = argparse.ArgumentParser(
        description="Mirror a sprite or batch of sprites horizontally or vertically."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", type=str, help="Single PNG file path")
    group.add_argument("--input-dir", type=str, help="Directory of PNGs to mirror")
    parser.add_argument("--output", type=str, default="", help="Output file path (for single input)")
    parser.add_argument("--output-dir", type=str, default="", help="Output directory (for batch)")
    parser.add_argument("--axis", type=str, required=True, choices=["horizontal", "vertical"], help="Mirror axis")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    try:
        if args.input:
            path = Path(args.input)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {args.input}")
            out_path = Path(args.output) if args.output else path.with_stem(path.stem + f"_mirror_{args.axis}")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            img = Image.open(path).convert("RGBA")
            mirrored = mirror_image(img, args.axis)
            mirrored.save(out_path)
            result = {"status": "ok", "input": str(path), "output": str(out_path), "axis": args.axis}
        else:
            in_dir = Path(args.input_dir)
            out_dir = Path(args.output_dir) if args.output_dir else in_dir.parent / f"{in_dir.name}_mirrored"
            out_dir.mkdir(parents=True, exist_ok=True)
            files = sorted([f for f in in_dir.iterdir() if f.suffix.lower() == ".png"])
            mirrored_files = []
            for f in files:
                img = Image.open(f).convert("RGBA")
                m = mirror_image(img, args.axis)
                out = out_dir / f.name
                m.save(out)
                mirrored_files.append(str(out))
            result = {"status": "ok", "input_dir": str(in_dir), "output_dir": str(out_dir), "axis": args.axis, "files_mirrored": len(mirrored_files)}

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Mirrored ({args.axis}): {result.get('output', result.get('output_dir'))}")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
