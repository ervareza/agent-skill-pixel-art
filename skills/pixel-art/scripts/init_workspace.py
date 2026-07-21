#!/usr/bin/env python3
"""
Initialize a pixel art workspace with standard directories and an asset manifest.

Usage:
    python scripts/init_workspace.py --dir ./my-project --json
    python scripts/init_workspace.py --help
"""

import sys
import json
import argparse
from pathlib import Path


WORKSPACE_DIRS = [
    "sprites",
    "tilesets",
    "frames",
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
        "asset": asset_name,
        "workspace": str(root),
        "directories": {d: str(root / d) for d in WORKSPACE_DIRS},
    }

    manifest_path = root / f"{asset_name}.manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return {
        "status": "ok",
        "workspace": str(root),
        "created_directories": created,
        "manifest": str(manifest_path),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a pixel art workspace with standard directories and an asset manifest."
    )
    parser.add_argument("--dir", type=str, default=".", help="Root directory for the workspace (default: current directory)")
    parser.add_argument("--name", type=str, default="untitled", help="Asset name for the manifest (default: untitled)")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    try:
        result = init_workspace(Path(args.dir), args.name)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Workspace initialized at: {result['workspace']}")
            print(f"Manifest written to: {result['manifest']}")
        sys.exit(0)
    except Exception as e:
        if args.json:
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
