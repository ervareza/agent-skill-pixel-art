#!/usr/bin/env python3
"""PixelForge Studio - Sprite Atlas Packer

Packs individual PNG pixel art frames into sprite sheet atlases with JSON metadata manifests.

Usage:
    python atlas_packer.py <project_path> [--by-category]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class SpriteAtlasPacker:
    """Packer utility for assembling sprite atlases and manifests."""

    def __init__(self, workspace_path: Path) -> None:
        self.workspace_path = workspace_path
        self.assets_dir = workspace_path / "assets"
        self.sheets_dir = workspace_path / "sheets"

    def pack_atlases(self, by_category: bool = True) -> bool:
        """Pack individual PNG assets into organized sprite sheet atlases."""
        if not self.assets_dir.exists():
            print(f"[ERROR] Assets directory does not exist: {self.assets_dir}")
            return False

        if not HAS_PIL:
            print("[ERROR] Pillow library is required for sprite packing: pip install Pillow")
            sys.exit(1)

        self.sheets_dir.mkdir(parents=True, exist_ok=True)
        manifest: Dict[str, Any] = {"engine": "PixelForge Studio", "sheets": []}

        categories = sorted(d.name for d in self.assets_dir.iterdir() if d.is_dir())

        for cat in categories:
            cat_dir = self.assets_dir / cat
            png_files = sorted(cat_dir.glob("*.png"))
            if not png_files:
                continue

            # Group files by pixel resolution
            dimension_groups: Dict[str, List[Path]] = {}
            for png in png_files:
                img = Image.open(png)
                res_key = f"{img.width}x{img.height}"
                dimension_groups.setdefault(res_key, []).append(png)

            # Build sheets per dimension group
            for res_key, files in dimension_groups.items():
                width, height = map(int, res_key.split("x"))

                if by_category:
                    anim_groups = self._group_by_animation(files)
                    for anim_name, anim_files in anim_groups.items():
                        sheet_name = f"{cat}_{anim_name}_{res_key}.png"
                        self._create_sheet_file(
                            self.sheets_dir / sheet_name,
                            anim_files,
                            width,
                            height,
                            manifest,
                            cat,
                            anim_name,
                        )
                else:
                    sheet_name = f"{cat}_{res_key}.png"
                    self._create_sheet_file(
                        self.sheets_dir / sheet_name, files, width, height, manifest, cat, "all"
                    )

        # Write manifest JSON
        manifest_path = self.sheets_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[OK] Generated {len(manifest['sheets'])} sprite atlas sheet(s). Manifest saved: {manifest_path.name}")
        return True

    @staticmethod
    def _group_by_animation(files: List[Path]) -> Dict[str, List[Path]]:
        groups: Dict[str, List[Path]] = {}
        for file in files:
            stem = file.stem
            parts = stem.rsplit("_", 1)
            if len(parts) == 2 and parts[1].isdigit():
                anim_name = parts[0]
            else:
                anim_name = stem
            groups.setdefault(anim_name, []).append(file)
        return groups

    @staticmethod
    def _create_sheet_file(
        sheet_path: Path,
        files: List[Path],
        tile_w: int,
        tile_h: int,
        manifest: Dict[str, Any],
        category: str,
        anim_name: str,
    ) -> None:
        total_frames = len(files)
        cols = min(total_frames, 16)
        rows = (total_frames + cols - 1) // cols

        sheet_img = Image.new("RGBA", (cols * tile_w, rows * tile_h), (0, 0, 0, 0))

        for idx, file in enumerate(files):
            img = Image.open(file).convert("RGBA")
            col = idx % cols
            row = idx // cols
            sheet_img.paste(img, (col * tile_w, row * tile_h))

        sheet_img.save(sheet_path, "PNG")

        manifest["sheets"].append(
            {
                "file": sheet_path.name,
                "category": category,
                "animation": anim_name,
                "tile_size": {"width": tile_w, "height": tile_h},
                "columns": cols,
                "rows": rows,
                "frame_count": total_frames,
                "frames": [f.stem for f in files],
            }
        )
        print(f"  Packed atlas: {sheet_path.name} ({total_frames} frame(s), {cols}x{rows} grid)")


def main() -> None:
    parser = argparse.ArgumentParser(description="PixelForge Studio - Sprite Atlas Packer")
    parser.add_argument("project_path", help="Path to workspace project directory")
    parser.add_argument(
        "--by-category",
        action="store_true",
        default=True,
        help="Pack sprite sheets grouped by category and animation",
    )
    args = parser.parse_args()

    packer = SpriteAtlasPacker(Path(args.project_path))
    success = packer.pack_atlases(by_category=args.by_category)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
