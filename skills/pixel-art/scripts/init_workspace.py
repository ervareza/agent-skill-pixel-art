#!/usr/bin/env python3
"""Initialize a PixelForge v1.0.0 pixel art workspace with standard game-asset directories & manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WORKSPACE_DIRS = [
    "characters",
    "layers",
    "tilesets",
    "vfx",
    "items",
    "ui",
    "stacks",
    "aseprite",
    "sheets",
    "exports",
]


def init_workspace(root: Path, asset_name: str) -> dict:
    root = root.resolve()
    created = []
    for d in WORKSPACE_DIRS:
        target = root / d
        target.mkdir(parents=True, exist_ok=True)
        created.append(str(target))

    manifest = {
        "engine": "PixelForge",
        "version": "1.0.0",
        "asset": asset_name,
        "workspace": str(root),
        "directories": {d: str(root / d) for d in WORKSPACE_DIRS},
    }
    manifest_path = root / f"{asset_name}.manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"status": "ok", "workspace": str(root), "created_directories": created, "manifest": str(manifest_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize a PixelForge pixel art game asset workspace.")
    parser.add_argument("--dir", type=str, default=".", help="Workspace root directory")
    parser.add_argument("--name", type=str, default="pixel-game", help="Project name for manifest")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    try:
        res = init_workspace(Path(args.dir), args.name)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Initialized PixelForge workspace at {res['workspace']} ({len(WORKSPACE_DIRS)} dirs)")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
