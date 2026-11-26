#!/usr/bin/env python3
"""Batch audit all PNG files in a directory using the PixelForge QA engine."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine.qa import audit_image


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch audit all PNG files in a directory.")
    parser.add_argument("--dir", type=str, required=True, help="Directory containing PNG files")
    parser.add_argument("--grid", type=int, default=1, help="Base grid multiple (default: 1)")
    parser.add_argument("--max-colors", type=int, default=256, help="Max allowed colors (default: 256)")
    parser.add_argument("--palette", type=str, default="", help="Optional strict palette name or JSON path")
    parser.add_argument("--ignore-orphans", action="store_true", help="Ignore isolated 1px sparkles")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    target = Path(args.dir)
    if not target.is_dir():
        msg = f"Not a directory: {args.dir}"
        print(json.dumps({"status": "error", "message": msg}) if args.json else f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    pngs = sorted(target.rglob("*.png"), key=lambda p: str(p))
    if not pngs:
        msg = f"No PNG files found in {args.dir}"
        print(json.dumps({"status": "error", "message": msg}) if args.json else f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    results = []
    passed = 0
    failed = 0
    for p in pngs:
        try:
            img = Image.open(p).convert("RGBA")
            rep = audit_image(img, grid_size=args.grid, max_colors=args.max_colors, palette=args.palette or None, ignore_orphans=args.ignore_orphans)
            issues = []
            if not rep["antialiasing"]["clean"]:
                issues.append(f"{rep['antialiasing']['semi_transparent_pixels']} AA px")
            if not args.ignore_orphans and not rep["orphan_pixels"]["clean"]:
                issues.append(f"{rep['orphan_pixels']['orphan_pixels']} orphans")
            if not rep["palette"]["clean"]:
                issues.append(f"{rep['palette']['unique_colors']} colors (off-pal {len(rep['palette']['off_palette_colors'])})")
            if not rep["grid_alignment"]["aligned"]:
                issues.append(f"grid mismatch ({img.width}x{img.height})")
            status = rep["status"]
            if status == "pass":
                passed += 1
            else:
                failed += 1
            results.append({"file": str(p.relative_to(target)), "size": [img.width, img.height], "status": status, "issues": issues})
        except Exception as e:
            failed += 1
            results.append({"file": p.name, "status": "error", "issues": [str(e)]})

    report = {"status": "pass" if failed == 0 else "fail", "total_files": len(pngs), "passed": passed, "failed": failed, "results": results}
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Batch audit: {passed}/{len(pngs)} passed")
        for r in results:
            tag = "PASS" if r["status"] == "pass" else "FAIL"
            extra = f" — {', '.join(r['issues'])}" if r["issues"] else ""
            print(f"  [{tag}] {r['file']}{extra}")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
