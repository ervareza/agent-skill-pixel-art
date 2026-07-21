#!/usr/bin/env python3
"""PixelForge Studio - Chroma Palette Analyzer

Analyzes, extracts, and validates color palettes from reference assets and project specifications.

Usage:
    python chroma_analyzer.py extract <image_path> [--count 16]
    python chroma_analyzer.py validate <project_path>
    python chroma_analyzer.py distance <color1> <color2>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Set, Tuple

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class ChromaPaletteAnalyzer:
    """Chroma palette extraction and color space analyzer."""

    def __init__(self) -> None:
        if not HAS_PIL:
            print("[WARN] Pillow library is not installed. Image-based extraction will be restricted.")

    def extract_palette_from_image(self, image_path: Path, max_colors: int = 16) -> List[str]:
        """Extract dominant pixel art palette from reference image."""
        if not HAS_PIL:
            print("[ERROR] Pillow is required for palette extraction: pip install Pillow")
            sys.exit(1)

        if not image_path.exists():
            print(f"[ERROR] Source image not found: {image_path}")
            sys.exit(1)

        img = Image.open(image_path).convert("RGBA")
        pixels = list(img.getdata())

        # Filter out fully transparent or low-alpha pixels
        opaque = [(r, g, b) for r, g, b, a in pixels if a > 128]
        if not opaque:
            print(f"[WARN] No opaque pixels detected in {image_path}")
            return []

        # Quantize colors to frequency buckets
        color_histogram = {}
        for r, g, b in opaque:
            qr = (r >> 4) << 4
            qg = (g >> 4) << 4
            qb = (b >> 4) << 4
            bucket = (qr, qg, qb)
            color_histogram[bucket] = color_histogram.get(bucket, 0) + 1

        sorted_buckets = sorted(color_histogram.items(), key=lambda item: -item[1])

        # Cluster and extract hex strings
        palette: List[str] = []
        for (r, g, b), _ in sorted_buckets:
            hex_code = f"#{r:02X}{g:02X}{b:02X}"
            
            # Check Euclidean color distance threshold
            too_similar = False
            for existing_hex in palette:
                if self.calculate_color_distance(hex_code, existing_hex) < 30.0:
                    too_similar = True
                    break

            if not too_similar:
                palette.append(hex_code)

            if len(palette) >= max_colors:
                break

        return palette

    def validate_project_palette(self, project_path: Path) -> bool:
        """Validate whether workspace assets comply with declared palette."""
        spec_lock = project_path / "spec_lock.md"
        if not spec_lock.exists():
            print(f"[ERROR] spec_lock.md not found in {project_path}")
            return False

        content = spec_lock.read_text(encoding="utf-8")
        palette_colors: Set[str] = set()
        in_palette_block = False

        for line in content.splitlines():
            stripped = line.strip()
            if stripped.lower().startswith("## palette"):
                in_palette_block = True
                continue
            if stripped.startswith("## ") and in_palette_block:
                in_palette_block = False
                continue
            if in_palette_block and stripped.startswith("- #"):
                palette_colors.add(stripped[2:].strip().upper())

        if not palette_colors:
            print("[WARN] No palette color specifications found in spec_lock.md")
            return False

        print(f"Declared palette contract: {len(palette_colors)} distinct color(s)")

        assets_dir = project_path / "assets"
        if not assets_dir.exists():
            print("[WARN] Assets directory does not exist yet.")
            return True

        if not HAS_PIL:
            print("[WARN] Pillow library missing; skipping pixel-level color validation.")
            return True

        non_compliant_assets: List[str] = []
        for png in assets_dir.rglob("*.png"):
            img = Image.open(png).convert("RGBA")
            for r, g, b, a in img.getdata():
                if a < 128:
                    continue
                hex_c = f"#{r:02X}{g:02X}{b:02X}".upper()
                if hex_c not in palette_colors:
                    non_compliant_assets.append(f"{png.relative_to(project_path)}: Color {hex_c} outside palette")
                    break

        if non_compliant_assets:
            print(f"[WARN] Found {len(non_compliant_assets)} non-compliant asset file(s):")
            for issue in non_compliant_assets[:20]:
                print(f"  - {issue}")
            return False

        print("[OK] All verified assets conform strictly to the declared palette contract.")
        return True

    @staticmethod
    def calculate_color_distance(color1: str, color2: str) -> float:
        """Calculate RGB Euclidean distance between two hex color codes."""
        c1 = color1.lstrip("#")
        c2 = color2.lstrip("#")
        r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
        r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
        return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5


def main() -> None:
    parser = argparse.ArgumentParser(description="PixelForge Studio - Chroma Palette Analyzer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: extract
    p_extract = subparsers.add_parser("extract", help="Extract palette from image")
    p_extract.add_argument("image_path", help="Path to reference image")
    p_extract.add_argument("--count", type=int, default=16, help="Maximum color count to extract")

    # Subcommand: validate
    p_val = subparsers.add_parser("validate", help="Validate workspace assets against declared palette")
    p_val.add_argument("project_path", help="Path to workspace directory")

    # Subcommand: distance
    p_dist = subparsers.add_parser("distance", help="Calculate Euclidean distance between hex colors")
    p_dist.add_argument("color1", help="First hex color code (e.g. #FF0000)")
    p_dist.add_argument("color2", help="Second hex color code (e.g. #00FF00)")

    args = parser.parse_args()
    analyzer = ChromaPaletteAnalyzer()

    if args.command == "extract":
        colors = analyzer.extract_palette_from_image(Path(args.image_path), max_colors=args.count)
        print(f"Extracted {len(colors)} palette color(s):")
        for c in colors:
            print(f"  {c}")
    elif args.command == "validate":
        valid = analyzer.validate_project_palette(Path(args.project_path))
        sys.exit(0 if valid else 1)
    elif args.command == "distance":
        dist = ChromaPaletteAnalyzer.calculate_color_distance(args.color1, args.color2)
        print(f"Euclidean distance: {dist:.2f} (max value = 441.67)")


if __name__ == "__main__":
    main()
