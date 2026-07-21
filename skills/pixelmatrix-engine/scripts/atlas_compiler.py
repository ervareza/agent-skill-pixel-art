#!/usr/bin/env python3
"""
PixelMatrix Engine — SpriteAtlasCompiler
Automated Sprite Sheet and Texture Atlas Compiler with JSON Metadata Generation.

Author: PixelMatrix Engine Core Team
License: MIT
Version: 2.0.0
"""

import sys
import json
import math
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
from PIL import Image

class SpriteAtlasCompiler:
    """
    Packs individual sprite frames or grid rasters into a unified sprite sheet atlas,
    generating frame coordinates, uv metrics, and metadata JSON manifests.
    """

    def __init__(self, frame_size: Tuple[int, int] = (32, 32)):
        self.frame_w, self.frame_h = frame_size

    def pack_frames(
        self,
        frame_paths: List[Path],
        output_atlas_path: Path,
        padding: int = 0
    ) -> Dict[str, Any]:
        """Packs a list of image paths into a grid texture atlas."""
        if not frame_paths:
            raise ValueError("No frame paths provided for packing.")

        images = [Image.open(p).convert("RGBA") for p in frame_paths]
        count = len(images)

        # Calculate optimal grid columns and rows
        cols = math.ceil(math.sqrt(count))
        rows = math.ceil(count / cols)

        atlas_w = cols * (self.frame_w + padding) - padding
        atlas_h = rows * (self.frame_h + padding) - padding

        atlas_img = Image.new("RGBA", (atlas_w, atlas_h), (0, 0, 0, 0))
        frames_meta = {}

        for idx, (path, img) in enumerate(zip(frame_paths, images)):
            col = idx % cols
            row = idx // cols
            x = col * (self.frame_w + padding)
            y = row * (self.frame_h + padding)

            # Resize or paste
            if img.size != (self.frame_w, self.frame_h):
                img = img.resize((self.frame_w, self.frame_h), Image.Resampling.NEAREST)

            atlas_img.paste(img, (x, y))

            frame_id = path.stem
            frames_meta[frame_id] = {
                "frame": {"x": x, "y": y, "w": self.frame_w, "h": self.frame_h},
                "uv": {
                    "u_min": round(x / atlas_w, 4),
                    "v_min": round(y / atlas_h, 4),
                    "u_max": round((x + self.frame_w) / atlas_w, 4),
                    "v_max": round((y + self.frame_h) / atlas_h, 4)
                },
                "grid_index": {"col": col, "row": row}
            }

        output_atlas_path.parent.mkdir(parents=True, exist_ok=True)
        atlas_img.save(output_atlas_path, "PNG")

        meta = {
            "engine": "PixelMatrix Engine",
            "compiler": "SpriteAtlasCompiler",
            "atlas_image": str(output_atlas_path.name),
            "dimensions": {"width": atlas_w, "height": atlas_h},
            "columns": cols,
            "rows": rows,
            "total_frames": count,
            "frame_dimensions": {"width": self.frame_w, "height": self.frame_h},
            "frames": frames_meta
        }

        meta_path = output_atlas_path.with_suffix(".json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        return meta


def main():
    parser = argparse.ArgumentParser(description="PixelMatrix Sprite Atlas Compiler CLI")
    parser.add_argument("--frames-dir", type=str, required=True, help="Directory containing frame PNGs")
    parser.add_argument("--output", type=str, required=True, help="Output atlas PNG path")
    parser.add_argument("--width", type=int, default=32, help="Frame width")
    parser.add_argument("--height", type=int, default=32, help="Frame height")
    parser.add_argument("--json", action="store_true", help="Output JSON metadata")

    args = parser.parse_args()

    frames_dir = Path(args.frames_dir)
    if not frames_dir.exists():
        print(json.dumps({"error": f"Frames directory not found: {args.frames_dir}"}))
        sys.exit(1)

    frame_files = sorted(list(frames_dir.glob("*.png")))
    if not frame_files:
        print(json.dumps({"error": f"No PNG frames found in {args.frames_dir}"}))
        sys.exit(1)

    compiler = SpriteAtlasCompiler((args.width, args.height))
    try:
        meta = compiler.pack_frames(frame_files, Path(args.output))
        print(json.dumps(meta, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
