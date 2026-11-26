#!/usr/bin/env python3
"""Deterministic cleanup pipeline for AI-generated or messy pixel art PNGs.

Recovers true pixel grid (auto-detect or modal block downscale), strips baked checkerboards,
hardens semi-transparent alpha, removes orphan speckles, merges near-duplicate colors,
dehalos edge contamination, and snaps cleanly to a locked game palette.

Usage:
    python scripts/sprite_clean.py --input messy.png --output clean.png --strip-checker --palette endesga-32 --json
    python scripts/sprite_clean.py --input ai_sprite.png --output clean.png --max-colors 16 --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.canvas import SpriteDocument
from engine.qa import audit_image


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean messy/AI-generated PNGs into strict palette-locked pixel art.")
    parser.add_argument("--input", type=str, required=True, help="Input messy PNG path")
    parser.add_argument("--output", type=str, required=True, help="Output cleaned PNG path")
    parser.add_argument("--scale", type=str, default="auto", help="Source pixel block scale: 'auto' or number (e.g. 4, 8)")
    parser.add_argument("--strip-checker", action="store_true", help="Remove baked-in gray checkerboard background")
    parser.add_argument("--palette", type=str, default="", help="Lock output to named palette or JSON file")
    parser.add_argument("--max-colors", type=int, default=0, help="Adaptive color cap if --palette is not set")
    parser.add_argument("--despeckle", type=int, default=2, help="Minimum connected pixel cluster size (default: 2)")
    parser.add_argument("--dedupe-tol", type=int, default=10, help="Merge near-duplicate colors within channel tol (default: 10)")
    parser.add_argument("--dither", action="store_true", help="Apply ordered Bayer dither when snapping to palette")
    parser.add_argument("--no-dehalo", action="store_true", help="Skip edge dehalo pass")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    try:
        sc: str | float = args.scale if args.scale == "auto" else float(args.scale)
        doc = SpriteDocument.from_png(args.input, scale=sc, strip_bg=args.strip_checker)
        before_colors = len(doc.used_colors())
        pal = args.palette or None
        max_c = args.max_colors if args.max_colors > 0 else None

        doc.clean(
            palette=pal,
            max_colors=max_c,
            dither=args.dither,
            harden=True,
            despeckle_min=args.despeckle,
            dedupe_tol=args.dedupe_tol,
            dehalo=not args.no_dehalo,
        )

        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        cleaned = doc.composite(1)
        cleaned.save(out)
        qa = audit_image(cleaned, grid_size=1, palette=pal)

        res = {
            "status": "ok",
            "input": str(args.input),
            "output": str(out),
            "detected_scale": doc.metadata.get("detected_scale", 1),
            "import_method": doc.metadata.get("import_method", "nearest"),
            "cleaned_size": [doc.width, doc.height],
            "colors_before": before_colors,
            "colors_after": qa["palette"]["unique_colors"],
            "qa_status": qa["status"],
        }
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Cleaned {Path(args.input).name} -> {out} ({doc.width}x{doc.height}, {before_colors}->{res['colors_after']} colors, QA={qa['status']})")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
