#!/usr/bin/env python3
"""
ChromaMatrix Core — CanvasBootstrapper
Voxel Canvas Initializer and Contract Manifest Orchestrator.

Author: ChromaMatrix Core Team
License: MIT
Version: 3.0.0
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List

class CanvasBootstrapper:
    """
    Manages voxel canvas folder setup, directory initialization,
    and contract manifest creation for ChromaMatrix Core.
    """

    DEFAULT_DIRECTORY_NODES = [
        "source_rasters",
        "compiled_atlases",
        "luma_palettes",
        "contract_manifests",
        "exports/indexed_png"
    ]

    def __init__(self, voxel_canvas_root: Path):
        self.canvas_root = voxel_canvas_root.resolve()

    def bootstrap_environment(self) -> List[str]:
        """Creates standardized directory nodes for the voxel canvas."""
        created = []
        for node in self.DEFAULT_DIRECTORY_NODES:
            target = self.canvas_root / node
            target.mkdir(parents=True, exist_ok=True)
            created.append(str(target))
        return created

    def create_contract_manifest(
        self,
        asset_identifier: str,
        grid_matrix_key: str,
        luma_palette_key: str,
        sprite_core_key: str
    ) -> Dict[str, Any]:
        """Generates structured asset contract manifest for AI agent workflows."""
        manifest = {
            "engine": "ChromaMatrix Core",
            "version": "3.0.0",
            "asset_identifier": asset_identifier,
            "manifest_keys": {
                "grid_matrix": grid_matrix_key,
                "luma_palette": luma_palette_key,
                "sprite_core": sprite_core_key
            },
            "directory_bindings": {
                "raw_raster": f"source_rasters/{asset_identifier}_raw.png",
                "refined_export": f"exports/indexed_png/{asset_identifier}_indexed.png",
                "atlas_image": f"compiled_atlases/{asset_identifier}_atlas.png",
                "atlas_manifest": f"compiled_atlases/{asset_identifier}_atlas.json"
            },
            "status": "BOOTSTRAPPED"
        }

        manifest_file = self.canvas_root / "contract_manifests" / f"{asset_identifier}_contract.json"
        manifest_file.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return manifest


def main():
    parser = argparse.ArgumentParser(description="ChromaMatrix Canvas Bootstrapper CLI")
    parser.add_argument("--canvas", type=str, default=".", help="Target voxel canvas path")
    parser.add_argument("--asset-id", type=str, default="hero_character", help="Asset identifier")
    parser.add_argument("--grid-matrix", type=str, default="standard_sprite_32", help="Grid matrix key")
    parser.add_argument("--palette-lut", type=str, default="pico8_fantasy_16", help="Luma palette key")
    parser.add_argument("--sprite-core", type=str, default="character_4way_matrix", help="Sprite core key")
    parser.add_argument("--json", action="store_true", help="Output JSON result")

    args = parser.parse_args()

    bootstrapper = CanvasBootstrapper(Path(args.canvas))
    directories = bootstrapper.bootstrap_environment()
    manifest = bootstrapper.create_contract_manifest(
        args.asset_id, args.grid_matrix, args.palette_lut, args.sprite_core
    )

    result = {
        "status": "SUCCESS",
        "created_directories": directories,
        "contract_manifest": manifest
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"[ChromaMatrix Core] Voxel Canvas bootstrapped at: {bootstrapper.canvas_root}")
        print(f"[ChromaMatrix Core] Contract created for: {args.asset_id}")

if __name__ == "__main__":
    main()
