#!/usr/bin/env python3
"""
PixelMatrix Engine — RasterSpecInspector
Quality Inspection Engine for Grid Alignment, Palette Limits & Anti-Aliasing Artifacts.

Author: PixelMatrix Engine Core Team
License: MIT
Version: 2.0.0
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image

class RasterSpecInspector:
    """
    Validates pixel art raster images against canvas preset specifications,
    detects anti-aliasing artifacts, checks color limits, and flags orphan pixels.
    """

    def __init__(self, target_image_path: Path):
        self.image_path = target_image_path.resolve()
        if not self.image_path.exists():
            raise FileNotFoundError(f"Image file not found: {target_image_path}")
        self.img = Image.open(self.image_path).convert("RGBA")

    def inspect_dimensions(self, expected_w: int = 32, expected_h: int = 32) -> Dict[str, Any]:
        """Verifies image dimensions and grid alignment."""
        actual_w, actual_h = self.img.size
        is_exact = (actual_w == expected_w) and (actual_h == expected_h)
        is_multiple = (actual_w % expected_w == 0) and (actual_h % expected_h == 0)

        return {
            "actual_dimensions": [actual_w, actual_h],
            "expected_dimensions": [expected_w, expected_h],
            "is_exact_match": is_exact,
            "is_grid_aligned": is_multiple
        }

    def detect_antialiasing_artifacts(self) -> Dict[str, Any]:
        """Detects semi-transparent alpha values indicative of blur/anti-aliasing artifacts."""
        pixels = self.img.getdata()
        semi_transparent_count = 0
        total_pixels = len(pixels)

        for r, g, b, a in pixels:
            if 0 < a < 255:  # Semi-transparent pixel
                semi_transparent_count += 1

        percentage = round((semi_transparent_count / max(total_pixels, 1)) * 100, 2)
        has_artifacts = semi_transparent_count > 0

        return {
            "semi_transparent_pixels": semi_transparent_count,
            "total_pixels": total_pixels,
            "artifact_percentage": percentage,
            "has_antialiasing_artifacts": has_artifacts
        }

    def inspect_color_palette(self, max_allowed_colors: int = 16) -> Dict[str, Any]:
        """Extracts color count and checks against max allowed palette constraint."""
        pixels = self.img.getdata()
        unique_colors = set()
        for r, g, b, a in pixels:
            if a > 0:
                unique_colors.add((r, g, b))

        count = len(unique_colors)
        exceeds_limit = count > max_allowed_colors

        return {
            "unique_color_count": count,
            "max_allowed_colors": max_allowed_colors,
            "exceeds_palette_limit": exceeds_limit
        }

    def detect_orphan_pixels(self) -> Dict[str, Any]:
        """Detects single isolated pixels (no 8-way neighbors of similar color)."""
        w, h = self.img.size
        pixels = self.img.load()
        orphan_count = 0

        for x in range(1, w - 1):
            for y in range(1, h - 1):
                cur_color = pixels[x, y]
                if cur_color[3] == 0:  # Skip transparent
                    continue

                # Check 8 neighbors
                has_neighbor = False
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        neighbor = pixels[x + dx, y + dy]
                        if neighbor[3] > 0:  # Opaque neighbor
                            has_neighbor = True
                            break
                    if has_neighbor:
                        break

                if not has_neighbor:
                    orphan_count += 1

        return {
            "orphan_pixel_count": orphan_count,
            "has_isolated_orphans": orphan_count > 0
        }

    def run_full_inspection(self, expected_w: int = 32, expected_h: int = 32, max_colors: int = 16) -> Dict[str, Any]:
        """Runs complete inspection suite."""
        dimensions = self.inspect_dimensions(expected_w, expected_h)
        aa_info = self.detect_antialiasing_artifacts()
        palette_info = self.inspect_color_palette(max_colors)
        orphan_info = self.detect_orphan_pixels()

        passed = (
            dimensions["is_grid_aligned"] and
            not aa_info["has_antialiasing_artifacts"] and
            not palette_info["exceeds_palette_limit"]
        )

        return {
            "engine": "PixelMatrix Engine",
            "inspector": "RasterSpecInspector",
            "file": str(self.image_path),
            "passed_spec": passed,
            "dimensions": dimensions,
            "antialiasing": aa_info,
            "palette": palette_info,
            "orphans": orphan_info
        }


def main():
    parser = argparse.ArgumentParser(description="PixelMatrix Raster Spec Inspector CLI")
    parser.add_argument("--image", type=str, required=True, help="Path to image file")
    parser.add_argument("--width", type=int, default=32, help="Expected grid width")
    parser.add_argument("--height", type=int, default=32, help="Expected grid height")
    parser.add_argument("--max-colors", type=int, default=16, help="Maximum allowed colors")
    parser.add_argument("--json", action="store_true", help="Output JSON result")

    args = parser.parse_args()

    try:
        inspector = RasterSpecInspector(Path(args.image))
        report = inspector.run_full_inspection(args.width, args.height, args.max_colors)
        print(json.dumps(report, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
