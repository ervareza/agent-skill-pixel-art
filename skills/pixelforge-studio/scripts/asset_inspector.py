#!/usr/bin/env python3
"""PixelForge Studio - Asset Inspector

Audits and validates generated 2D pixel art assets against workspace spec lock contracts.

Usage:
    python asset_inspector.py <project_path>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class PixelAssetInspector:
    """Quality assurance and specification audit inspector for PixelForge assets."""

    def __init__(self, workspace_path: Path) -> None:
        self.workspace_path = workspace_path
        self.spec_lock_path = workspace_path / "spec_lock.md"
        self.assets_dir = workspace_path / "assets"

    def inspect_workspace(self) -> bool:
        """Run complete quality inspection suite across project assets."""
        if not self.spec_lock_path.exists():
            print(f"[ERROR] spec_lock.md contract missing at: {self.spec_lock_path}")
            return False

        if not self.assets_dir.exists():
            print("[WARN] Assets directory does not exist yet.")
            return True

        palette_colors, base_size, max_color_budget = self._parse_spec_lock()
        print(
            f"Spec Audit Parameters: base_size={base_size}, max_colors={max_color_budget}, palette_size={len(palette_colors)}"
        )

        if not HAS_PIL:
            print("[WARN] Pillow library unavailable; running structure audit only.")
            return self._audit_structure_only()

        errors: List[str] = []
        warnings: List[str] = []
        asset_count = 0

        for png_file in sorted(self.assets_dir.rglob("*.png")):
            asset_count += 1
            img = Image.open(png_file)
            width, height = img.size

            # Check canvas dimensions conformity
            if base_size:
                bw, bh = base_size
                if width % bw != 0 or height % bh != 0:
                    warnings.append(
                        f"{png_file.name}: dimensions {width}x{height} not a multiple of base unit {bw}x{bh}"
                    )

            img_rgba = img.convert("RGBA")
            pixels = list(img_rgba.getdata())
            unique_colors: Set[str] = set()
            out_of_palette: Set[str] = set()
            semi_transparent_count = 0

            for r, g, b, a in pixels:
                if a < 128:
                    if 0 < a < 128:
                        semi_transparent_count += 1
                    continue

                if 128 <= a < 255:
                    semi_transparent_count += 1

                hex_code = f"#{r:02X}{g:02X}{b:02X}".upper()
                unique_colors.add(hex_code)
                if palette_colors and hex_code not in palette_colors:
                    out_of_palette.add(hex_code)

            if len(unique_colors) > max_color_budget:
                errors.append(
                    f"{png_file.name}: color count ({len(unique_colors)}) exceeds budget limit ({max_color_budget})"
                )

            if out_of_palette:
                errors.append(
                    f"{png_file.name}: contains {len(out_of_palette)} color(s) outside declared palette contract"
                )

            if semi_transparent_count > 0:
                warnings.append(
                    f"{png_file.name}: {semi_transparent_count} semi-transparent pixel(s) detected (anti-aliasing flaw)"
                )

        # Output Summary
        print("\n" + "=" * 60)
        print(f"[INSPECTION REPORT] Scanned {asset_count} asset file(s)")
        if errors:
            print(f"  [ERROR] {len(errors)} critical issue(s) detected:")
            for err in errors:
                print(f"    - {err}")
        if warnings:
            print(f"  [WARN] {len(warnings)} warning(s):")
            for wrn in warnings:
                print(f"    - {wrn}")
        if not errors and not warnings:
            print("  [OK] 100% Asset Inspection Passed cleanly!")
        elif not errors:
            print("  [OK] Asset Inspection Passed with non-critical warnings.")

        return len(errors) == 0

    def _parse_spec_lock(self) -> Tuple[Set[str], Optional[Tuple[int, int]], int]:
        content = self.spec_lock_path.read_text(encoding="utf-8")
        palette_colors: Set[str] = set()
        base_size: Optional[Tuple[int, int]] = None
        max_colors = 16

        in_palette = in_canvas = in_budget = False
        for line in content.splitlines():
            line = line.strip()
            if line.lower().startswith("## palette"):
                in_palette = True
                continue
            if line.lower().startswith("## canvas"):
                in_canvas = True
                continue
            if line.lower().startswith("## per_sprite_budget"):
                in_budget = True
                continue
            if line.startswith("## ") and (in_palette or in_canvas or in_budget):
                in_palette = in_canvas = in_budget = False
                continue

            if in_palette and line.startswith("- #"):
                palette_colors.add(line[2:].strip().upper())
            elif in_canvas and "base_size:" in line:
                val = line.split(":", 1)[1].strip()
                try:
                    w, h = val.lower().split("x")
                    base_size = (int(w), int(h))
                except ValueError:
                    pass
            elif in_budget and "max_colors:" in line:
                val = line.split(":", 1)[1].strip()
                try:
                    max_colors = int(val)
                except ValueError:
                    pass

        return palette_colors, base_size, max_colors

    def _audit_structure_only(self) -> bool:
        required_folders = ["assets", "images", "animations", "sheets", "notes", "exports"]
        required_files = ["design_spec.md", "spec_lock.md"]
        issues: List[str] = []

        for folder in required_folders:
            if not (self.workspace_path / folder).exists():
                issues.append(f"Missing folder: {folder}")

        for fname in required_files:
            if not (self.workspace_path / fname).exists():
                issues.append(f"Missing file: {fname}")

        if issues:
            for item in issues:
                print(f"  [WARN] {item}")
            return False
        return True


def main() -> None:
    parser = argparse.ArgumentParser(description="PixelForge Studio - Asset Inspector")
    parser.add_argument("project_path", help="Path to project workspace directory")
    args = parser.parse_args()

    inspector = PixelAssetInspector(Path(args.project_path))
    success = inspector.inspect_workspace()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
