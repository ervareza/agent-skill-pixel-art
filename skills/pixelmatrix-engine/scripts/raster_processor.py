#!/usr/bin/env python3
"""
PixelMatrix Engine — PixelRasterPostProcessor
Color Quantization, Isolated Orphan Pixel Cleaning & Indexed 8-bit PNG Export.

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

class PixelRasterPostProcessor:
    """
    Cleans raw pixel assets by stripping anti-aliasing artifacts, quantizing colors
    to target LUT count, purging isolated orphan pixels, and exporting clean 8-bit PNGs.
    """

    def __init__(self, input_image_path: Path):
        self.input_path = input_image_path.resolve()
        if not self.input_path.exists():
            raise FileNotFoundError(f"Image not found: {input_image_path}")
        self.img = Image.open(self.input_path).convert("RGBA")

    def clean_transparency_threshold(self, alpha_threshold: int = 128) -> int:
        """Forces semi-transparent pixels to 0 or 255 alpha to eliminate anti-aliasing."""
        pixels = self.img.load()
        w, h = self.img.size
        modified_count = 0

        for x in range(w):
            for y in range(h):
                r, g, b, a = pixels[x, y]
                if 0 < a < 255:
                    new_a = 255 if a >= alpha_threshold else 0
                    pixels[x, y] = (r, g, b, new_a)
                    modified_count += 1

        return modified_count

    def clean_orphan_pixels(self) -> int:
        """Cleans isolated pixels with no opaque 8-way neighbors."""
        pixels = self.img.load()
        w, h = self.img.size
        cleaned = 0

        for x in range(1, w - 1):
            for y in range(1, h - 1):
                r, g, b, a = pixels[x, y]
                if a == 0:
                    continue

                has_neighbor = False
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        if pixels[x + dx, y + dy][3] > 0:
                            has_neighbor = True
                            break
                    if has_neighbor:
                        break

                if not has_neighbor:
                    pixels[x, y] = (0, 0, 0, 0)
                    cleaned += 1

        return cleaned

    def quantize_and_export(self, output_path: Path, max_colors: int = 16) -> Dict[str, Any]:
        """Quantizes image colors and exports as an indexed PNG."""
        # Process in memory
        aa_cleaned = self.clean_transparency_threshold()
        orphans_cleaned = self.clean_orphan_pixels()

        # Convert to P mode (indexed) with defined color limit
        quantized = self.img.quantize(colors=max_colors, dither=Image.Dither.NONE)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        quantized.save(output_path, "PNG")

        return {
            "engine": "PixelMatrix Engine",
            "processor": "PixelRasterPostProcessor",
            "input": str(self.input_path),
            "output": str(output_path),
            "aa_pixels_cleaned": aa_cleaned,
            "orphan_pixels_cleaned": orphans_cleaned,
            "quantized_color_limit": max_colors,
            "export_format": "PNG_INDEXED_P_MODE"
        }


def main():
    parser = argparse.ArgumentParser(description="PixelMatrix Pixel Raster PostProcessor CLI")
    parser.add_argument("--input", type=str, required=True, help="Input PNG path")
    parser.add_argument("--output", type=str, required=True, help="Output PNG path")
    parser.add_argument("--max-colors", type=int, default=16, help="Target max colors")
    parser.add_argument("--json", action="store_true", help="Output JSON result")

    args = parser.parse_args()

    try:
        processor = PixelRasterPostProcessor(Path(args.input))
        report = processor.quantize_and_export(Path(args.output), args.max_colors)
        print(json.dumps(report, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
