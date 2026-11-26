#!/usr/bin/env python3
"""Generate seeded procedural pixel art VFX sprite sheets, GIFs, and .aseprite files.

Usage:
    python scripts/vfx_gen.py --type explosion --size 32 --frames 12 --fps 16 --output explosion.png --gif --json
    python scripts/vfx_gen.py --type fire --size 24x32 --frames 8 --fps 12 --palette pico-8 --output fire.png --gif --aseprite --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.exporters import export_aseprite, export_gif, export_spritesheet
from engine.vfx import VFX_TYPES, generate_vfx


def parse_size(raw: str) -> tuple[int, int]:
    s = raw.lower().strip()
    if "x" in s:
        a, b = s.split("x", 1)
        return int(a), int(b)
    v = int(s)
    return v, v


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate procedural pixel art VFX animations (color + quantized glow).")
    parser.add_argument("--type", type=str, default="explosion", choices=VFX_TYPES, help="Effect type")
    parser.add_argument("--size", type=str, default="32", help="Canvas size: N or WxH")
    parser.add_argument("--frames", type=int, default=12, help="Frame count (2..60)")
    parser.add_argument("--fps", type=int, default=16, help="Playback FPS (1..60)")
    parser.add_argument("--palette", type=str, default="none", help="Optional target palette to snap colors to")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic seed")
    parser.add_argument("--cols", type=int, default=0, help="Sheet columns (0 = single row)")
    parser.add_argument("--scale", type=int, default=1, help="Sheet integer scale")
    parser.add_argument("--gif", action="store_true", help="Also export animated GIF")
    parser.add_argument("--gif-scale", type=int, default=4, help="GIF scale factor")
    parser.add_argument("--aseprite", action="store_true", help="Also export .aseprite")
    parser.add_argument("--output", type=str, required=True, help="Output spritesheet PNG path")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    try:
        w, h = parse_size(args.size)
        pal = None if args.palette.lower() == "none" else args.palette
        doc = generate_vfx(vfx_type=args.type, width=w, height=h, frames=args.frames, fps=args.fps, palette=pal, seed=args.seed)
        out = Path(args.output)
        sheet_res = export_spritesheet(doc, out, cols=args.cols, scale=args.scale)
        res: dict = {"status": "ok", "vfx": args.type, "size": [w, h], "frames": args.frames, "fps": args.fps, "sheet": sheet_res}

        if args.gif:
            imgs = [doc.composite(i + 1) for i in range(doc.n_frames)]
            durs = [f.duration_ms for f in doc.frames]
            res["gif"] = export_gif(imgs, out.with_suffix(".gif"), durations_ms=durs, scale=args.gif_scale)
        if args.aseprite:
            res["aseprite"] = export_aseprite(doc, out.with_suffix(".aseprite"))

        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Generated VFX '{args.type}' ({w}x{h}, {args.frames}f @ {args.fps}fps) -> {out}")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
