#!/usr/bin/env python3
"""PixelForge Studio v1.0.0 — Unified Master CLI dispatcher.

Usage:
    python scripts/pixel_studio.py palettes [--json]
    python scripts/pixel_studio.py info [--json]
    python scripts/pixel_studio.py character --archetype hero --size 32 --dirs 4 --frames 8 --output-dir ./hero --gif
    python scripts/pixel_studio.py tileset --terrain grass --mode wang16 --size 16 --output grass.png
    python scripts/pixel_studio.py vfx --type explosion --size 32 --frames 12 --output boom.png --gif
    python scripts/pixel_studio.py asset --category item --type sword --size 16 --output sword.png
    python scripts/pixel_studio.py stack --preset car --slices 12 --frames 16 --output-dir ./car --gif
    python scripts/pixel_studio.py clean --input raw.png --output clean.png --palette endesga-32
    python scripts/pixel_studio.py audit --image sprite.png --json
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR.parent))

from engine import __version__
from engine.assets import ITEM_TYPES, STACK_PRESETS, UI_TYPES
from engine.character import ACTIONS, ARCHETYPES
from engine.color import list_palettes, load_palette
from engine.tileset import TERRAIN_PRESETS
from engine.vfx import VFX_TYPES

SUBCOMMANDS = {
    "character": "character_gen.py",
    "layers": "layer_compose.py",
    "tileset": "tileset_gen.py",
    "vfx": "vfx_gen.py",
    "asset": "asset_gen.py",
    "stack": "sprite_stack.py",
    "clean": "sprite_clean.py",
    "audit": "quality_audit.py",
    "batch-audit": "batch_audit.py",
    "pack": "atlas_pack.py",
    "gif": "gif_export.py",
    "remap": "palette_remap.py",
    "extract": "palette_extract.py",
    "indexed": "export_indexed.py",
    "resize": "sprite_resize.py",
    "mirror": "sprite_mirror.py",
    "outline": "outline_generator.py",
    "dither": "dither.py",
    "noise": "noise_generator.py",
    "init": "init_workspace.py",
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(f"PixelForge Studio CLI v{__version__}")
        print("\nCommands:")
        print("  info          Show engine capabilities, presets, and palettes")
        print("  palettes      List all available color palettes")
        for k, v in SUBCOMMANDS.items():
            print(f"  {k:<13} Dispatch to scripts/{v}")
        sys.exit(0)

    cmd = sys.argv[1]
    rest = sys.argv[2:]
    want_json = "--json" in rest

    if cmd == "palettes":
        pals = []
        for name in list_palettes():
            _, cols = load_palette(name)
            pals.append({"name": name, "colors": len(cols)})
        if want_json:
            print(json.dumps({"status": "ok", "count": len(pals), "palettes": pals}, indent=2))
        else:
            for p in pals:
                print(f"  {p['name']:<16} ({p['colors']} colors)")
        sys.exit(0)

    if cmd == "info":
        info = {
            "engine": "PixelForge",
            "version": __version__,
            "palettes": list_palettes(),
            "character_archetypes": list(ARCHETYPES),
            "character_actions": list(ACTIONS),
            "terrain_presets": sorted(TERRAIN_PRESETS.keys()),
            "vfx_types": list(VFX_TYPES),
            "item_types": list(ITEM_TYPES),
            "ui_types": list(UI_TYPES),
            "sprite_stack_presets": list(STACK_PRESETS),
            "subcommands": sorted(SUBCOMMANDS.keys()),
        }
        if want_json:
            print(json.dumps(info, indent=2))
        else:
            print(f"PixelForge Engine v{__version__}")
            print(f"  Palettes ({len(info['palettes'])}): {', '.join(info['palettes'])}")
            print(f"  Characters ({len(info['character_archetypes'])}): {', '.join(info['character_archetypes'])}")
            print(f"  Actions ({len(info['character_actions'])}): {', '.join(info['character_actions'])}")
            print(f"  Terrains ({len(info['terrain_presets'])}): {', '.join(info['terrain_presets'])}")
            print(f"  VFX ({len(info['vfx_types'])}): {', '.join(info['vfx_types'])}")
            print(f"  Items ({len(info['item_types'])}): {', '.join(info['item_types'])}")
            print(f"  UI ({len(info['ui_types'])}): {', '.join(info['ui_types'])}")
            print(f"  3D Stacks ({len(info['sprite_stack_presets'])}): {', '.join(info['sprite_stack_presets'])}")
        sys.exit(0)

    if cmd not in SUBCOMMANDS:
        msg = f"Unknown subcommand {cmd!r}. Run with --help to see all commands."
        print(json.dumps({"status": "error", "message": msg}) if want_json else f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    script_path = SCRIPTS_DIR / SUBCOMMANDS[cmd]
    proc = subprocess.run([sys.executable, str(script_path), *rest])
    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
