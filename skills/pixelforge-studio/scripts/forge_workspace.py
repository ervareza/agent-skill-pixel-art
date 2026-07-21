#!/usr/bin/env python3
"""PixelForge Studio - Workspace Manager

Engine for initializing, importing, validating, and managing PixelForge Studio workspaces.

Usage:
    python forge_workspace.py init <project_name> [--size 32x32] [--palette default]
    python forge_workspace.py import-sources <project_path> <files...> [--move]
    python forge_workspace.py validate <project_path>
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Core Workspace Constants
SKILL_DIR: Path = Path(__file__).resolve().parent.parent
DEFAULT_WORKSPACE_ROOT: Path = SKILL_DIR.parent.parent / "projects"

ASSET_CATEGORIES: List[str] = [
    "characters",
    "tiles",
    "items",
    "ui",
    "effects",
    "backgrounds",
]


class ForgeWorkspaceManager:
    """Manager class for PixelForge Studio asset generation workspaces."""

    def __init__(self, root_dir: Optional[Path] = None) -> None:
        self.root_dir = root_dir or DEFAULT_WORKSPACE_ROOT

    def initialize_workspace(
        self, name: str, size: str = "32x32", palette: str = "default"
    ) -> Path:
        """Initialize a new PixelForge project directory structure."""
        try:
            w_str, h_str = size.lower().split("x")
            width, height = int(w_str), int(h_str)
        except ValueError:
            print(f"[ERROR] Invalid dimensions format '{size}'. Expected format 'WxH' (e.g. 32x32)")
            sys.exit(1)

        max_allowed_dim = 2048
        if width > max_allowed_dim or height > max_allowed_dim:
            print(f"[ERROR] Dimensions {size} exceed max resolution limit of {max_allowed_dim}x{max_allowed_dim}")
            sys.exit(1)
        if width < 1 or height < 1:
            print(f"[ERROR] Invalid dimension size {size}. Minimum is 1x1.")
            sys.exit(1)

        date_stamp = datetime.now().strftime("%Y%m%d")
        workspace_folder = f"{name}_{size}_{date_stamp}"
        workspace_path = self.root_dir / workspace_folder

        if workspace_path.exists():
            print(f"[ERROR] Target workspace already exists at: {workspace_path}")
            sys.exit(1)

        # Create Directory Layout
        workspace_path.mkdir(parents=True, exist_ok=True)
        for cat in ASSET_CATEGORIES:
            (workspace_path / "assets" / cat).mkdir(parents=True, exist_ok=True)

        for sub_folder in ["animations", "sheets", "notes", "exports", "images"]:
            (workspace_path / sub_folder).mkdir(parents=True, exist_ok=True)

        # Write core specifications
        self._write_spec_lock(workspace_path, name, size, palette)
        self._write_design_spec(workspace_path, name, size, palette)

        print(f"[OK] PixelForge Workspace initialized: {workspace_path}")
        print(f"     Canvas Base Size: {size}")
        print(f"     Color Palette:    {palette}")
        print(f"     Asset Bundles:    {', '.join(ASSET_CATEGORIES)}")
        return workspace_path

    def import_reference_sources(
        self, workspace_path: Path, source_files: List[str], move: bool = False
    ) -> List[str]:
        """Import visual source materials into project workspace."""
        if not workspace_path.exists():
            print(f"[ERROR] Workspace target path not found: {workspace_path}")
            sys.exit(1)

        target_dir = workspace_path / "images"
        imported_names: List[str] = []

        import shutil
        for src in source_files:
            src_file = Path(src)
            if not src_file.exists():
                print(f"[WARN] Reference file not found: {src}")
                continue

            destination = target_dir / src_file.name
            if move:
                shutil.move(str(src_file), str(destination))
            else:
                shutil.copy2(str(src_file), str(destination))
            imported_names.append(destination.name)
            print(f"  Imported source: {destination.name}")

        print(f"[OK] Successfully imported {len(imported_names)} source asset(s)")
        return imported_names

    def validate_workspace_integrity(self, workspace_path: Path) -> bool:
        """Audit project structure and verify spec contract completeness."""
        if not workspace_path.exists():
            print(f"[ERROR] Workspace directory not found: {workspace_path}")
            sys.exit(1)

        issues: List[str] = []
        required_files = ["design_spec.md", "spec_lock.md"]
        for fname in required_files:
            if not (workspace_path / fname).exists():
                issues.append(f"Missing core contract: {fname}")

        for cat in ASSET_CATEGORIES:
            if not (workspace_path / "assets" / cat).exists():
                issues.append(f"Missing asset bundle folder: assets/{cat}")

        for folder in ["images", "animations", "sheets", "notes", "exports"]:
            if not (workspace_path / folder).exists():
                issues.append(f"Missing subfolder: {folder}")

        spec_contract = workspace_path / "spec_lock.md"
        if spec_contract.exists():
            content = spec_contract.read_text(encoding="utf-8")
            if "palette" not in content.lower():
                issues.append("spec_lock.md lacks declared ## palette section")
            if "canvas" not in content.lower():
                issues.append("spec_lock.md lacks declared ## canvas section")

        if issues:
            print(f"[FAIL] Workspace verification found {len(issues)} defect(s):")
            for item in issues:
                print(f"  - {item}")
            return False

        print(f"[OK] Workspace structure verification clean: {workspace_path.name}")
        return True

    def _write_spec_lock(
        self, path: Path, project_name: str, size: str, palette: str
    ) -> None:
        contract_content = f"""# PixelForge Spec Lock Contract
## metadata
- project_name: {project_name}
- created_at: {datetime.now().isoformat()}
- version: 1.0.0

## canvas
- base_size: {size}
- max_dimension: 2048x2048

## palette
- id: {palette}
- colors:
  - #000000
  - #FFFFFF

## per_sprite_budget
- max_colors: 16
"""
        (path / "spec_lock.md").write_text(contract_content, encoding="utf-8")

    def _write_design_spec(
        self, path: Path, project_name: str, size: str, palette: str
    ) -> None:
        spec_content = f"""# PixelForge Design Spec

## Project Overview
- **Name**: {project_name}
- **Target Resolution**: {size}
- **Color Palette Preset**: {palette}

## Style Guidelines
- **Art Direction**: 2D Pixel Art
- **Edge Rule**: Clean, sharp pixel boundaries. No semi-transparent anti-aliasing.
- **Lighting**: Consistent top-left light key.
"""
        (path / "design_spec.md").write_text(spec_content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PixelForge Studio - Workspace Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: init
    cmd_init = subparsers.add_parser("init", help="Initialize a new project workspace")
    cmd_init.add_argument("project_name", help="Identifier for the new project")
    cmd_init.add_argument("--size", default="32x32", help="Base tile/sprite size (e.g. 32x32, 64x64)")
    cmd_init.add_argument("--palette", default="default", help="Preset color palette identifier")

    # Subcommand: import-sources
    cmd_import = subparsers.add_parser("import-sources", help="Import reference images into workspace")
    cmd_import.add_argument("project_path", help="Path to existing project directory")
    cmd_import.add_argument("files", nargs="+", help="Files to import")
    cmd_import.add_argument("--move", action="store_true", help="Move source files instead of copying")

    # Subcommand: validate
    cmd_val = subparsers.add_parser("validate", help="Verify workspace structure and contracts")
    cmd_val.add_argument("project_path", help="Path to project directory")

    args = parser.parse_args()
    manager = ForgeWorkspaceManager()

    if args.command == "init":
        manager.initialize_workspace(args.project_name, size=args.size, palette=args.palette)
    elif args.command == "import-sources":
        manager.import_reference_sources(Path(args.project_path), args.files, move=args.move)
    elif args.command == "validate":
        valid = manager.validate_workspace_integrity(Path(args.project_path))
        sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
