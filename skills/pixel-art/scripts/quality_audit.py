#!/usr/bin/env python3
"""
Audit a pixel art PNG for common quality issues:
  - Semi-transparent pixels (anti-aliasing artifacts)
  - Orphan pixels (isolated with no opaque neighbors)
  - Palette violations (too many unique colors)
  - Grid alignment (dimensions not multiples of base grid)

Usage:
    python scripts/quality_audit.py --image sprite.png --json
    python scripts/quality_audit.py --image sprite.png --grid 16 --max-colors 16 --json
    python scripts/quality_audit.py --help
"""

import sys
import json
import argparse
from pathlib import Path
from PIL import Image


def audit_antialiasing(img):
    """Check for semi-transparent pixels (0 < alpha < 255)."""
    pixels = img.getdata()
    bad = sum(1 for r, g, b, a in pixels if 0 < a < 255)
    return {
        "semi_transparent_pixels": bad,
        "total_pixels": len(pixels),
        "clean": bad == 0,
    }


def audit_orphan_pixels(img):
    """Check for isolated pixels with zero opaque 8-way neighbors."""
    w, h = img.size
    px = img.load()
    orphans = 0

    for x in range(w):
        for y in range(h):
            if px[x, y][3] == 0:
                continue
            has_neighbor = False
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] > 0:
                        has_neighbor = True
                        break
                if has_neighbor:
                    break
            if not has_neighbor:
                orphans += 1

    return {"orphan_pixels": orphans, "clean": orphans == 0}


def audit_palette(img, max_colors):
    """Check unique opaque color count against limit."""
    pixels = img.getdata()
    colors = set()
    for r, g, b, a in pixels:
        if a > 0:
            colors.add((r, g, b))
    count = len(colors)
    return {
        "unique_colors": count,
        "max_allowed": max_colors,
        "clean": count <= max_colors,
    }


def audit_grid(img, grid_size):
    """Check if dimensions are exact multiples of grid_size."""
    w, h = img.size
    aligned = (w % grid_size == 0) and (h % grid_size == 0)
    return {
        "width": w,
        "height": h,
        "grid_size": grid_size,
        "aligned": aligned,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Audit a pixel art PNG for anti-aliasing, orphan pixels, palette violations, and grid alignment."
    )
    parser.add_argument("--image", type=str, required=True, help="Path to the PNG image to audit")
    parser.add_argument("--grid", type=int, default=8, help="Base grid size for alignment check (default: 8)")
    parser.add_argument("--max-colors", type=int, default=256, help="Maximum allowed unique colors (default: 256)")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    path = Path(args.image)
    if not path.exists():
        msg = f"File not found: {args.image}"
        if args.json:
            print(json.dumps({"status": "error", "message": msg}))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    try:
        img = Image.open(path).convert("RGBA")
    except Exception as e:
        msg = f"Cannot open image: {e}"
        if args.json:
            print(json.dumps({"status": "error", "message": msg}))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    aa = audit_antialiasing(img)
    orphans = audit_orphan_pixels(img)
    palette = audit_palette(img, args.max_colors)
    grid = audit_grid(img, args.grid)

    passed = aa["clean"] and orphans["clean"] and palette["clean"] and grid["aligned"]

    report = {
        "status": "pass" if passed else "fail",
        "file": str(path),
        "antialiasing": aa,
        "orphan_pixels": orphans,
        "palette": palette,
        "grid_alignment": grid,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Audit: {'PASS' if passed else 'FAIL'} — {path.name}")
        if not aa["clean"]:
            print(f"  ⚠ {aa['semi_transparent_pixels']} semi-transparent pixels found")
        if not orphans["clean"]:
            print(f"  ⚠ {orphans['orphan_pixels']} orphan pixels found")
        if not palette["clean"]:
            print(f"  ⚠ {palette['unique_colors']} colors found (max {palette['max_allowed']})")
        if not grid["aligned"]:
            print(f"  ⚠ {grid['width']}x{grid['height']} not aligned to {grid['grid_size']}px grid")

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
