#!/usr/bin/env python3
"""
PixelMatrix Engine — PaletteLUTSynthesizer
Color Palette Look-Up Table (LUT) Extractor, Remapper & Distance Analyzer.

Author: PixelMatrix Engine Core Team
License: MIT
Version: 2.0.0
"""

import sys
import json
import math
import argparse
from pathlib import Path
from typing import List, Tuple, Dict, Any
from PIL import Image

class PaletteLUTSynthesizer:
    """
    Extracts color palettes from raw raster images, maps colors against defined
    hardware/aesthetic LUTs, and calculates perceptual color distances.
    """

    @staticmethod
    def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
        """Converts HEX string to RGB tuple."""
        hex_clean = hex_str.lstrip("#")
        return tuple(int(hex_clean[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        """Converts RGB tuple to HEX string."""
        return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"

    @staticmethod
    def euclidean_distance(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
        """Calculates Euclidean color distance in 3D RGB space."""
        return math.sqrt(
            (color1[0] - color2[0]) ** 2 +
            (color1[1] - color2[1]) ** 2 +
            (color1[2] - color2[2]) ** 2
        )

    def extract_palette(self, image_path: Path, max_colors: int = 256) -> List[str]:
        """Extracts unique colors from an image file, excluding fully transparent pixels."""
        img = Image.open(image_path).convert("RGBA")
        pixels = img.getdata()
        
        unique_rgbs = set()
        for r, g, b, a in pixels:
            if a > 10:  # Ignore transparent pixels
                unique_rgbs.add((r, g, b))
                
        sorted_rgbs = sorted(list(unique_rgbs))[:max_colors]
        return [self.rgb_to_hex(rgb) for rgb in sorted_rgbs]

    def remap_to_lut(
        self,
        source_colors: List[str],
        lut_colors: List[str]
    ) -> Dict[str, Any]:
        """Maps each source color to the nearest color in the target LUT."""
        source_rgbs = [self.hex_to_rgb(c) for c in source_colors]
        lut_rgbs = [self.hex_to_rgb(c) for c in lut_colors]

        mapping = {}
        total_distance = 0.0

        for src_hex, src_rgb in zip(source_colors, source_rgbs):
            best_match = None
            min_dist = float("inf")

            for lut_hex, lut_rgb in zip(lut_colors, lut_rgbs):
                dist = self.euclidean_distance(src_rgb, lut_rgb)
                if dist < min_dist:
                    min_dist = dist
                    best_match = lut_hex

            mapping[src_hex] = {
                "matched_color": best_match,
                "distance": round(min_dist, 2)
            }
            total_distance += min_dist

        avg_distance = round(total_distance / max(len(source_colors), 1), 2)
        return {
            "source_color_count": len(source_colors),
            "target_lut_count": len(lut_colors),
            "average_color_distance": avg_distance,
            "remap_matrix": mapping
        }


def main():
    parser = argparse.ArgumentParser(description="PixelMatrix Palette LUT Synthesizer CLI")
    parser.add_argument("--image", type=str, required=False, help="Source image path")
    parser.add_argument("--lut", type=str, required=False, help="JSON file or LUT palette key")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")

    args = parser.parse_args()

    synthesizer = PaletteLUTSynthesizer()

    if not args.image:
        demo_palette = ["#1A1A1A", "#FF0055", "#00FF66", "#FFFFFF"]
        lut_demo = ["#000000", "#FF004D", "#00E436", "#FFF1E8"]
        result = synthesizer.remap_to_lut(demo_palette, lut_demo)
    else:
        image_path = Path(args.image)
        if not image_path.exists():
            print(json.dumps({"error": f"Image file not found: {args.image}"}))
            sys.exit(1)
        extracted = synthesizer.extract_palette(image_path)
        result = {"extracted_colors": extracted, "count": len(extracted)}

    if args.json or True:  # Default clean JSON CLI output
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
