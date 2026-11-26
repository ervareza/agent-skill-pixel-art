#!/usr/bin/env python3
"""Fake-3D Sprite Stacking CLI: build horizontal slice strips and render crisp 360-degree turntables.

Usage:
    python scripts/sprite_stack.py --preset car --slices 12 --frames 16 --output-dir ./out/car --gif --json
    python scripts/sprite_stack.py --strip my_slices.png --slices 16 --frames 24 --output-dir ./out/turntable --gif --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.assets import STACK_PRESETS, build_stack_preset, render_stack_turntable
from engine.exporters import export_gif, export_spritesheet


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate fake-3D stacked sprite slice strips and rotatable 360-degree turntables.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preset", type=str, choices=STACK_PRESETS, help="Procedural 3D voxel stack preset")
    group.add_argument("--strip", type=str, help="Existing horizontal slice strip PNG to render as a turntable")
    parser.add_argument("--slice-width", type=int, default=16, help="Slice width for preset mode (default: 16)")
    parser.add_argument("--slice-height", type=int, default=24, help="Slice height for preset mode (default: 24)")
    parser.add_argument("--slices", type=int, default=12, help="Number of stacked slices (default: 12)")
    parser.add_argument("--frames", type=int, default=16, help="Turntable rotation frames (default: 16)")
    parser.add_argument("--fps", type=int, default=12, help="Turntable playback FPS (default: 12)")
    parser.add_argument("--squash", type=float, default=0.75, help="Camera pitch vertical squash (default: 0.75)")
    parser.add_argument("--spacing", type=float, default=1.0, help="Vertical lift px per slice (default: 1.0)")
    parser.add_argument("--palette", type=str, default="endesga-32", help="Palette name/JSON")
    parser.add_argument("--outline", type=str, default="#181425", help="Unified post-stack outline hex (or 'none')")
    parser.add_argument("--gif", action="store_true", help="Export rotating 360-degree turntable GIF")
    parser.add_argument("--gif-scale", type=int, default=4, help="GIF scale factor")
    parser.add_argument("--output-dir", type=str, required=True, help="Output directory")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    try:
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        pal = None if args.palette.lower() == "none" else args.palette
        outline = None if args.outline.lower() == "none" else args.outline

        if args.preset:
            strip, meta = build_stack_preset(args.preset, args.slice_width, args.slice_height, args.slices, palette=pal)
            name = args.preset
            strip_path = out_dir / f"{name}_slices.png"
            strip.save(strip_path)
        else:
            strip_path = Path(args.strip)
            strip = Image.open(strip_path).convert("RGBA")
            if strip.width % args.slices != 0:
                raise ValueError(f"Strip width {strip.width} is not divisible by --slices {args.slices}")
            name = strip_path.stem
            meta = {"slice_count": args.slices, "slice_width": strip.width // args.slices, "slice_height": strip.height}

        tt_doc = render_stack_turntable(
            strip, args.slices, frames=args.frames, fps=args.fps,
            squash=args.squash, spacing=args.spacing, outline_color=outline,
        )
        sheet_res = export_spritesheet(tt_doc, out_dir / f"{name}_turntable.png", cols=min(8, args.frames))

        res: dict = {
            "status": "ok",
            "strip": str(strip_path),
            "meta": meta,
            "turntable_sheet": sheet_res,
        }
        if args.gif:
            imgs = [tt_doc.composite(i + 1) for i in range(tt_doc.n_frames)]
            durs = [f.duration_ms for f in tt_doc.frames]
            res["gif"] = export_gif(imgs, out_dir / f"{name}_turntable.gif", durations_ms=durs, scale=args.gif_scale)

        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Sprite stack '{name}' ({args.slices} slices, {args.frames} turntable frames) -> {out_dir}")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
