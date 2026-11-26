#!/usr/bin/env python3
"""Audit a pixel art PNG for anti-aliasing, orphan pixels, palette compliance, jaggies, clipping, and seamlessness.

Usage:
    python scripts/quality_audit.py --image sprite.png --json
    python scripts/quality_audit.py --image sprite.png --grid 16 --max-colors 16 --palette pico-8 --json
    python scripts/quality_audit.py --image tile.png --check-seamless --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine.qa import audit_image


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit a pixel art PNG for AA, orphans, palette conformance, jaggies, clipping, and seamless tiling."
    )
    parser.add_argument("--image", type=str, required=True, help="Path to the PNG image to audit")
    parser.add_argument("--grid", type=int, default=1, help="Base grid multiple check (default: 1 = any size e.g. 9x9, 12x12)")
    parser.add_argument("--max-colors", type=int, default=256, help="Maximum allowed unique colors (default: 256)")
    parser.add_argument("--palette", type=str, default="", help="Optional strict palette name or JSON path")
    parser.add_argument("--ignore-orphans", action="store_true", help="Allow isolated 1px sparkles/particles")
    parser.add_argument("--check-seamless", action="store_true", help="Also verify 4-edge seamless tile wrap")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    path = Path(args.image)
    if not path.exists():
        msg = f"File not found: {args.image}"
        print(json.dumps({"status": "error", "message": msg}) if args.json else f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    try:
        img = Image.open(path).convert("RGBA")
        report = audit_image(
            img,
            grid_size=args.grid,
            max_colors=args.max_colors,
            palette=args.palette or None,
            ignore_orphans=args.ignore_orphans,
            check_seamless=args.check_seamless,
        )
        report["file"] = str(path)
        passed = report["status"] == "pass"

        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"Audit: {'PASS' if passed else 'FAIL'} — {path.name}")
            if not report["antialiasing"]["clean"]:
                print(f"  ! {report['antialiasing']['semi_transparent_pixels']} semi-transparent pixels")
            if not args.ignore_orphans and not report["orphan_pixels"]["clean"]:
                print(f"  ! {report['orphan_pixels']['orphan_pixels']} orphan pixels")
            if not report["palette"]["clean"]:
                print(f"  ! {report['palette']['unique_colors']} colors (max {args.max_colors}), off-palette={len(report['palette']['off_palette_colors'])}")
            if not report["grid_alignment"]["aligned"]:
                g = report["grid_alignment"]
                print(f"  ! {g['width']}x{g['height']} not aligned to {g['grid_size']}px grid")
            if "seamless" in report and not report["seamless"]["seamless"]:
                print(f"  ! Seamless check failed: {report['seamless']}")
        sys.exit(0 if passed else 1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
