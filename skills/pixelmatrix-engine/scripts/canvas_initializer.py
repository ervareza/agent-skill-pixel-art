#!/usr/bin/env python3
"""
PixelMatrix Engine — MatrixCanvasInitializer
Autonomous Workspace Initialization and Canvas Specification Validator.

Author: PixelMatrix Engine Core Team
License: MIT
Version: 2.0.0
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List

class MatrixCanvasInitializer:
    """
    Manages workspace folder hierarchy initialization, asset directory setup,
    and specification manifest creation for PixelMatrix Engine assets.
    """

    DEFAULT_FOLDERS = [
        "source_rasters",
        "compiled_atlases",
        "lut_palettes",
        "spec_manifests",
        "exports/indexed_png"
    ]

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()

    def initialize_structure(self) -> List[str]:
        """Creates the standardized workspace directory structure."""
        created_paths = []
        for folder in self.DEFAULT_FOLDERS:
            target = self.workspace_root / folder
            target.mkdir(parents=True, exist_ok=True)
            created_paths.append(str(target))
        return created_paths

    def generate_contract_manifest(
        self,
        asset_name: str,
        preset_key: str,
        palette_key: str,
        sprite_matrix_key: str
    ) -> Dict[str, Any]:
        """Generates a structured asset contract manifest for AI agent pipelines."""
        manifest = {
            "engine": "PixelMatrix Engine",
            "version": "2.0.0",
            "asset_name": asset_name,
            "specification": {
                "grid_preset": preset_key,
                "palette_lut": palette_key,
                "sprite_matrix": sprite_matrix_key
            },
            "output_paths": {
                "source": f"source_rasters/{asset_name}_raw.png",
                "processed": f"exports/indexed_png/{asset_name}_indexed.png",
                "atlas": f"compiled_atlases/{asset_name}_atlas.png",
                "atlas_meta": f"compiled_atlases/{asset_name}_atlas.json"
            },
            "status": "INITIALIZED"
        }

        manifest_path = self.workspace_root / "spec_manifests" / f"{asset_name}_contract.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return manifest


def main():
    parser = argparse.ArgumentParser(description="PixelMatrix Canvas Initializer CLI")
    parser.add_argument("--workspace", type=str, default=".", help="Target workspace root path")
    parser.add_argument("--asset-name", type=str, default="hero_sprite", help="Asset identifier name")
    parser.add_argument("--preset", type=str, default="standard_sprite_32", help="Grid preset key")
    parser.add_argument("--palette", type=str, default="pico8_fantasy_16", help="Palette LUT key")
    parser.add_argument("--matrix", type=str, default="character_4way_matrix", help="Sprite matrix key")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")

    args = parser.parse_args()

    initializer = MatrixCanvasInitializer(Path(args.workspace))
    created_dirs = initializer.initialize_structure()
    manifest = initializer.generate_contract_manifest(
        args.asset_name, args.preset, args.palette, args.matrix
    )

    result = {
        "status": "SUCCESS",
        "created_directories": created_dirs,
        "contract_manifest": manifest
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"[PixelMatrix Engine] Workspace initialized at: {initializer.workspace_root}")
        print(f"[PixelMatrix Engine] Contract manifest created for: {args.asset_name}")

if __name__ == "__main__":
    main()
