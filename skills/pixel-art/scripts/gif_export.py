#!/usr/bin/env python3
"""Convert a sprite sheet or directory of frames into a crisp transparent animated GIF (1..60 FPS)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine.exporters import export_gif


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a sprite sheet or directory of frames into a clean transparent animated GIF.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sheet", type=str, help="Sprite sheet PNG path")
    group.add_argument("--frames-dir", type=str, help="Directory containing frame PNGs")
    parser.add_argument("--frame-width", type=int, default=0, help="Frame width (required with --sheet)")
    parser.add_argument("--frame-height", type=int, default=0, help="Frame height (required with --sheet)")
    parser.add_argument("--cols", type=int, default=0, help="Columns in sheet (0 = auto-detect)")
    parser.add_argument("--fps", type=int, default=10, help="Frames per second (1..60, default: 10)")
    parser.add_argument("--scale", type=int, default=1, help="Integer nearest-neighbor upscale factor (default: 1)")
    parser.add_argument("--bg", type=str, default="", help="Optional solid hex background color")
    parser.add_argument("--output", type=str, required=True, help="Output GIF path")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    try:
        frames: list[Image.Image] = []
        if args.sheet:
            if args.frame_width <= 0 or args.frame_height <= 0:
                raise ValueError("--frame-width and --frame-height are required with --sheet")
            img = Image.open(args.sheet).convert("RGBA")
            fw, fh = args.frame_width, args.frame_height
            cols = args.cols if args.cols > 0 else max(1, img.width // fw)
            rows = max(1, img.height // fh)
            for r in range(rows):
                for c in range(cols):
                    x, y = c * fw, r * fh
                    if x + fw <= img.width and y + fh <= img.height:
                        frames.append(img.crop((x, y, x + fw, y + fh)))
        else:
            files = sorted([f for f in Path(args.frames_dir).iterdir() if f.suffix.lower() == ".png"], key=lambda f: f.stem)
            if not files:
                raise ValueError(f"No PNG files found in {args.frames_dir}")
            frames = [Image.open(f).convert("RGBA") for f in files]

        dur_ms = max(16, round(1000.0 / max(1, args.fps)))
        res = export_gif(frames, Path(args.output), durations_ms=dur_ms, scale=args.scale, bg=args.bg or None)
        res["fps"] = args.fps
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Exported {res['frame_count']} frames -> {args.output} ({args.fps} FPS @ {args.scale}x)")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
