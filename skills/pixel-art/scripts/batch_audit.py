#!/usr/bin/env python3
"""
Batch audit all PNG files in a directory for pixel art quality issues.

Usage:
    python scripts/batch_audit.py --dir ./sprites/ --json
    python scripts/batch_audit.py --dir ./sprites/ --grid 16 --max-colors 16 --json
    python scripts/batch_audit.py --help
"""

import sys
import json
import argparse
from pathlib import Path
from PIL import Image


def audit_single(img_path: Path, grid: int, max_colors: int) -> dict:
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    px = img.load()

    aa_count = 0
    orphans = 0
    colors = set()

    for x in range(w):
        for y in range(h):
            r, g, b, a = px[x, y]
            if 0 < a < 255:
                aa_count += 1
            if a > 0:
                colors.add((r, g, b))
                # orphan check
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

    aligned = (w % grid == 0) and (h % grid == 0)
    color_ok = len(colors) <= max_colors
    issues = []
    if aa_count > 0:
        issues.append(f"{aa_count} semi-transparent pixels")
    if orphans > 0:
        issues.append(f"{orphans} orphan pixels")
    if not color_ok:
        issues.append(f"{len(colors)} colors (max {max_colors})")
    if not aligned:
        issues.append(f"{w}×{h} not aligned to {grid}px grid")

    return {
        "file": img_path.name,
        "size": [w, h],
        "status": "pass" if not issues else "fail",
        "issues": issues,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Batch audit all PNG files in a directory for pixel art quality issues."
    )
    parser.add_argument("--dir", type=str, required=True, help="Directory containing PNG files")
    parser.add_argument("--grid", type=int, default=8, help="Base grid size (default: 8)")
    parser.add_argument("--max-colors", type=int, default=256, help="Max allowed colors (default: 256)")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    target = Path(args.dir)
    if not target.is_dir():
        msg = f"Not a directory: {args.dir}"
        print(json.dumps({"status": "error", "message": msg}) if args.json else f"Error: {msg}")
        sys.exit(1)

    pngs = sorted([f for f in target.rglob("*.png")], key=lambda f: f.name)
    if not pngs:
        msg = f"No PNG files found in {args.dir}"
        print(json.dumps({"status": "error", "message": msg}) if args.json else f"Error: {msg}")
        sys.exit(1)

    results = []
    passed = 0
    failed = 0
    for p in pngs:
        try:
            r = audit_single(p, args.grid, args.max_colors)
            results.append(r)
            if r["status"] == "pass":
                passed += 1
            else:
                failed += 1
        except Exception as e:
            results.append({"file": p.name, "status": "error", "issues": [str(e)]})
            failed += 1

    report = {
        "status": "pass" if failed == 0 else "fail",
        "total_files": len(pngs),
        "passed": passed,
        "failed": failed,
        "results": results,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Batch audit: {passed}/{len(pngs)} passed")
        for r in results:
            icon = "✅" if r["status"] == "pass" else "❌"
            print(f"  {icon} {r['file']}", end="")
            if r["issues"]:
                print(f" — {', '.join(r['issues'])}")
            else:
                print()

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
