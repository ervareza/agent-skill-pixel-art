#!/usr/bin/env python3
"""Pack sprite frames into a sprite sheet with universal engine metadata (Aseprite JSON, Phaser, Unity, Godot 4 .tres, simple)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine.canvas import SpriteDocument
from engine.exporters import export_aseprite, export_godot_spriteframes, export_spritesheet


def main() -> None:
    parser = argparse.ArgumentParser(description="Pack sprite frames into a sprite sheet with engine metadata.")
    parser.add_argument("--frames-dir", type=str, required=True, help="Directory containing frame PNGs")
    parser.add_argument("--output", type=str, required=True, help="Output sprite sheet PNG path")
    parser.add_argument("--cols", type=int, default=0, help="Columns per row (default: all frames in one row)")
    parser.add_argument("--padding", type=int, default=0, help="Padding between frames in pixels (default: 0)")
    parser.add_argument("--fps", type=int, default=10, help="Animation FPS stored in metadata (default: 10)")
    parser.add_argument("--tag", type=str, default="default", help="Animation tag name (default: default)")
    parser.add_argument("--format", type=str, default="aseprite", choices=["aseprite", "phaser", "unity", "simple"], help="JSON metadata format")
    parser.add_argument("--godot", action="store_true", help="Also emit Godot 4 .tres SpriteFrames")
    parser.add_argument("--aseprite", action="store_true", help="Also emit native .aseprite file")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    try:
        frames_dir = Path(args.frames_dir).resolve()
        files = sorted([f for f in frames_dir.iterdir() if f.suffix.lower() == ".png"], key=lambda f: f.stem)
        if not files:
            raise ValueError(f"No PNG files found in {frames_dir}")

        imgs = [Image.open(f).convert("RGBA") for f in files]
        fw, fh = imgs[0].size
        doc = SpriteDocument(fw, fh, snap=False, default_fps=args.fps)
        doc.frames[0].cels["main"] = imgs[0]
        for im in imgs[1:]:
            doc.add_frame(copy=False)
            doc.frames[-1].cels["main"] = im
        doc.tag(args.tag, 1, len(imgs))

        out = Path(args.output)
        res = export_spritesheet(doc, out, cols=args.cols, padding=args.padding, json_format=args.format)
        if args.godot:
            res["godot"] = export_godot_spriteframes(out, out.with_suffix(".json"), out.with_suffix(".tres"))
        if args.aseprite:
            res["aseprite"] = export_aseprite(doc, out.with_suffix(".aseprite"))

        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Packed {res['frame_count']} frames -> {res['sheet']} (+ {res['metadata']})")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
