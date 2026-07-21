#!/usr/bin/env python3
"""PixelForge Studio - Asset Post-Processor

Executes post-processing operations on 2D pixel art PNGs: palette quantization, orphan pixel cleanup, and index color conversion.

Usage:
    python post_processor.py <project_path> [--quantize] [--clean] [--index]
    python post_processor.py <project_path> --all
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Tuple

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class AssetPostProcessor:
    """Post-processing engine for quantization, cleaning, and palette indexing."""

    def __init__(self, workspace_path: Path) -> None:
        self.workspace_path = workspace_path
        self.assets_dir = workspace_path / "assets"
        self.spec_lock_path = workspace_path / "spec_lock.md"

    def quantize_assets(self) -> None:
        """Quantize all workspace PNG assets to nearest declared palette colors."""
        if not HAS_PIL:
            print("[ERROR] Pillow library required for quantization: pip install Pillow")
            sys.exit(1)

        palette = self._load_declared_palette()
        if not palette:
            print(f"[ERROR] No palette definitions found in {self.spec_lock_path.name}")
            sys.exit(1)

        print(f"Quantizing asset palette colors to {len(palette)} target shade(s)...")
        if not self.assets_dir.exists():
            print("[WARN] Assets folder does not exist.")
            return

        processed_count = 0
        for png_path in sorted(self.assets_dir.rglob("*.png")):
            img = Image.open(png_path).convert("RGBA")
            pixels = list(img.getdata())
            new_pixels = []

            for r, g, b, a in pixels:
                if a < 128:
                    new_pixels.append((0, 0, 0, 0))
                else:
                    nearest = self._find_nearest_rgb(r, g, b, palette)
                    new_pixels.append((*nearest, 255))

            quantized_img = Image.new("RGBA", img.size)
            quantized_img.putdata(new_pixels)
            quantized_img.save(png_path, "PNG")
            processed_count += 1

        print(f"[OK] Successfully quantized {processed_count} asset file(s).")

    def clean_stray_pixels(self) -> None:
        """Remove isolated stray orphan pixels across PNG assets."""
        if not HAS_PIL:
            print("[ERROR] Pillow library required for pixel cleanup.")
            sys.exit(1)

        if not self.assets_dir.exists():
            return

        cleaned_count = 0
        for png_path in sorted(self.assets_dir.rglob("*.png")):
            img = Image.open(png_path).convert("RGBA")
            pixels = list(img.getdata())
            width, height = img.size
            modified = False
            new_pixels = list(pixels)

            for y in range(height):
                for x in range(width):
                    idx = y * width + x
                    r, g, b, a = pixels[idx]

                    if a < 128:
                        continue

                    # Check 4-directional neighborhood
                    neighbors = []
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            nidx = ny * width + nx
                            _, _, _, na = pixels[nidx]
                            if na >= 128:
                                neighbors.append(nidx)

                    # If fully isolated pixel, clear to transparent
                    if not neighbors:
                        new_pixels[idx] = (0, 0, 0, 0)
                        modified = True

            if modified:
                clean_img = Image.new("RGBA", img.size)
                clean_img.putdata(new_pixels)
                clean_img.save(png_path, "PNG")
                cleaned_count += 1

        print(f"[OK] Cleaned isolated stray pixels in {cleaned_count} asset file(s).")

    def convert_to_indexed_png(self) -> None:
        """Convert RGBA PNG files into palette-indexed 8-bit PNG images."""
        if not HAS_PIL:
            print("[ERROR] Pillow library required for indexed PNG conversion.")
            sys.exit(1)

        palette = self._load_declared_palette()
        if not self.assets_dir.exists():
            return

        pal_rgb_list: List[Tuple[int, int, int]] = []
        for hex_code in palette:
            code = hex_code.lstrip("#")
            r, g, b = int(code[0:2], 16), int(code[2:4], 16), int(code[4:6], 16)
            pal_rgb_list.append((r, g, b))

        converted_count = 0
        for png_path in sorted(self.assets_dir.rglob("*.png")):
            img = Image.open(png_path).convert("RGBA")
            pixels = list(img.getdata())

            pal_img = Image.new("P", img.size)
            indexed_data: List[int] = []

            for r, g, b, a in pixels:
                if a < 128:
                    indexed_data.append(0)  # Index 0 reserved for transparency
                else:
                    nearest_index = self._find_nearest_index(r, g, b, pal_rgb_list)
                    indexed_data.append(nearest_index + 1)  # Shift by 1 due to transparent index 0

            pal_img.putdata(indexed_data)

            # Build 768-byte palette buffer
            raw_palette_buffer: List[int] = [0, 0, 0]  # Color 0
            for r, g, b in pal_rgb_list:
                raw_palette_buffer.extend([r, g, b])
            while len(raw_palette_buffer) < 768:
                raw_palette_buffer.extend([0, 0, 0])

            pal_img.putpalette(raw_palette_buffer)
            pal_img.info["transparency"] = 0
            pal_img.save(png_path, "PNG")
            converted_count += 1

        print(f"[OK] Converted {converted_count} asset file(s) into indexed PNG format.")

    def run_all_processors(self) -> None:
        """Run complete post-processing pipeline in sequence."""
        self.quantize_assets()
        self.clean_stray_pixels()
        self.convert_to_indexed_png()

    def _load_declared_palette(self) -> List[str]:
        if not self.spec_lock_path.exists():
            return []
        content = self.spec_lock_path.read_text(encoding="utf-8")
        palette: List[str] = []
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
                palette.append(stripped[2:].strip())

        return palette

    @staticmethod
    def _find_nearest_rgb(
        r: int, g: int, b: int, palette_hex: List[str]
    ) -> Tuple[int, int, int]:
        best_dist = float("inf")
        best_rgb = (r, g, b)

        for hex_code in palette_hex:
            code = hex_code.lstrip("#")
            pr, pg, pb = int(code[0:2], 16), int(code[2:4], 16), int(code[4:6], 16)
            dist = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
            if dist < best_dist:
                best_dist = dist
                best_rgb = (pr, pg, pb)

        return best_rgb

    @staticmethod
    def _find_nearest_index(
        r: int, g: int, b: int, palette_rgb: List[Tuple[int, int, int]]
    ) -> int:
        best_dist = float("inf")
        best_idx = 0

        for idx, (pr, pg, pb) in enumerate(palette_rgb):
            dist = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
            if dist < best_dist:
                best_dist = dist
                best_idx = idx

        return best_idx


def main() -> None:
    parser = argparse.ArgumentParser(description="PixelForge Studio - Asset Post-Processor")
    parser.add_argument("project_path", help="Path to workspace directory")
    parser.add_argument("--quantize", action="store_true", help="Quantize assets to palette")
    parser.add_argument("--clean", action="store_true", help="Clean stray orphan pixels")
    parser.add_argument("--index", action="store_true", help="Convert RGBA PNGs to indexed color")
    parser.add_argument("--all", action="store_true", help="Run all post-processing operations")

    args = parser.parse_args()
    processor = AssetPostProcessor(Path(args.project_path))

    if args.all:
        processor.run_all_processors()
    else:
        if args.quantize:
            processor.quantize_assets()
        if args.clean:
            processor.clean_stray_pixels()
        if args.index:
            processor.convert_to_indexed_png()

        if not (args.quantize or args.clean or args.index):
            parser.print_help()


if __name__ == "__main__":
    main()
