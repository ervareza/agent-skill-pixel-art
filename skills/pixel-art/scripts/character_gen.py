#!/usr/bin/env python3
"""Generate layered, multi-directional animated pixel art characters.

Supports ANY pixel resolution (8x8, 9x9, 12x12, 16x16, 24x24, 32x32, 48x48, 64x64, WxH),
ANY frame count (1, 2, 3, 4, 5, 6, 8, 12, 24, 60), ANY FPS (1..60),
1/2/4/8 directions, 8 actions, 9 archetypes, paper-doll equipment swaps,
and exports to PNG spritesheet + JSON, per-layer paper-doll sheets, native .aseprite,
Godot 4 .tres SpriteFrames, RPG Maker 3x4, animated GIF, and labeled contact preview!

Usage:
    python scripts/character_gen.py --archetype hero --size 32 --dirs 4 --actions idle,walk,run,attack --frames 8 --fps 10 --output-dir ./out/hero --aseprite --gif --godot --rpgmaker --export-layers --json
    python scripts/character_gen.py --archetype mage --size 16x24 --dirs 8 --actions walk,cast --frames 12 --fps 16 --output-dir ./out/mage --gif --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.character import (
    ACTIONS,
    ARCHETYPES,
    DIR_SETS,
    CharacterSpec,
    build_character_pack,
    preset_spec,
)
from engine.exporters import (
    export_aseprite,
    export_gif,
    export_godot_spriteframes,
    export_per_layer_sheets,
    export_rpgmaker_sheet,
    export_spritesheet,
)
from engine.qa import audit_animation, audit_image


def parse_size(raw: str) -> tuple[int, int]:
    s = raw.lower().strip()
    if "x" in s:
        a, b = s.split("x", 1)
        return int(a), int(b)
    v = int(s)
    return v, v


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate layered multi-directional animated pixel art characters at any size & frame count."
    )
    parser.add_argument("--archetype", type=str, default="hero", choices=ARCHETYPES, help="Character preset archetype")
    parser.add_argument("--size", type=str, default="32", help="Canvas size: N (e.g. 8, 9, 12, 16, 24, 32, 48, 64) or WxH (e.g. 16x24)")
    parser.add_argument("--dirs", type=str, default="4", help="Direction set: 1, 2, 4, 8, or comma list (down,left,right,up,se,sw,ne,nw)")
    parser.add_argument("--actions", type=str, default="idle,walk", help=f"Comma-separated actions from: {','.join(ACTIONS)}")
    parser.add_argument("--frames", type=int, default=8, help="Frames per action clip (e.g. 2, 3, 4, 5, 6, 8, 12, 24, 60)")
    parser.add_argument("--fps", type=int, default=10, help="Base playback FPS (1..60)")
    parser.add_argument("--palette", type=str, default="endesga-32", help="Palette name or JSON path (or 'none' for unconstrained ramps)")
    parser.add_argument("--weapon", type=str, default="", help="Override weapon: none, sword, staff, bow, dagger, axe")
    parser.add_argument("--headgear", type=str, default="", help="Override headgear: none, helmet, wizard_hat, hood, crown, headband")
    parser.add_argument("--shield", type=str, default="", help="Override shield: none, kite, round")
    parser.add_argument("--hair-style", type=str, default="", help="Override hair: short, long, spiky, bob, bald")
    parser.add_argument("--no-cape", action="store_true", help="Disable cape layer")
    parser.add_argument("--output-dir", type=str, required=True, help="Output directory")
    parser.add_argument("--name", type=str, default="", help="Asset filename prefix (default: archetype)")
    parser.add_argument("--format", type=str, default="aseprite", choices=["aseprite", "phaser", "unity", "simple"], help="Spritesheet JSON metadata format")
    parser.add_argument("--scale", type=int, default=1, help="Integer export scale for spritesheet (default: 1)")
    parser.add_argument("--gif-scale", type=int, default=4, help="Integer scale for animated GIF previews (default: 4)")
    parser.add_argument("--gif", action="store_true", help="Export animated GIFs per (action, direction)")
    parser.add_argument("--aseprite", action="store_true", help="Export native layered .aseprite file")
    parser.add_argument("--export-layers", action="store_true", help="Export separate aligned paper-doll PNG sheets per layer")
    parser.add_argument("--godot", action="store_true", help="Export Godot 4 .tres SpriteFrames resource")
    parser.add_argument("--rpgmaker", action="store_true", help="Export RPG Maker MV/MZ 3x4 walk sheet (requires 4-dir walk)")
    parser.add_argument("--project", action="store_true", help="Save editable .pxproj.json project file")
    parser.add_argument("--preview", action="store_true", help="Export labeled upscaled contact sheet preview")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    try:
        w, h = parse_size(args.size)
        actions = [a.strip().lower() for a in args.actions.split(",") if a.strip()]
        spec = preset_spec(args.archetype)
        if args.weapon:
            spec.weapon = args.weapon
        if args.headgear:
            spec.headgear = args.headgear
        if args.shield:
            spec.shield = args.shield
        if args.hair_style:
            spec.hair_style = args.hair_style
        if args.no_cape:
            spec.has_cape = False

        pal = None if args.palette.lower() == "none" else args.palette
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        prefix = args.name or args.archetype

        master, clips = build_character_pack(
            width=w, height=h, actions=actions, directions=args.dirs,
            frames=args.frames, fps=args.fps, archetype=args.archetype,
            palette=pal, spec=spec,
        )

        # Pack master sheet with 1 row per clip (cols = frames)
        sheet_path = out_dir / f"{prefix}_sheet.png"
        sheet_res = export_spritesheet(
            master, sheet_path, cols=args.frames, scale=args.scale, json_format=args.format
        )

        # Run QA on frame 1
        qa_first = audit_image(master.composite(1), grid_size=1, max_colors=256, palette=pal)

        result: dict = {
            "status": "ok",
            "archetype": spec.archetype,
            "size": [w, h],
            "frames_per_clip": args.frames,
            "total_frames": master.n_frames,
            "fps": args.fps,
            "layers": master.layer_names,
            "tags": list(master.tags.keys()),
            "sheet": sheet_res,
            "qa_frame1": qa_first["status"],
        }

        if args.aseprite:
            result["aseprite"] = export_aseprite(master, out_dir / f"{prefix}.aseprite")

        if args.project:
            result["project"] = str(master.save_project(out_dir / f"{prefix}.pxproj.json"))

        if args.export_layers:
            result["layer_sheets"] = export_per_layer_sheets(master, out_dir / "layers", cols=args.frames, scale=args.scale)

        if args.godot:
            result["godot"] = export_godot_spriteframes(
                sheet_path, sheet_path.with_suffix(".json"), out_dir / f"{prefix}_spriteframes.tres"
            )

        if args.gif:
            gif_dir = out_dir / "gifs"
            gif_dir.mkdir(parents=True, exist_ok=True)
            gifs = []
            for (act, d), clip in clips.items():
                idx = clip.tag_frame_indices(f"{act}_{d}")
                fr_imgs = [clip.composite(i + 1) for i in idx]
                durs = [clip.frames[i].duration_ms for i in idx]
                gpath = gif_dir / f"{prefix}_{act}_{d}.gif"
                export_gif(fr_imgs, gpath, durations_ms=durs, scale=args.gif_scale)
                gifs.append(str(gpath))
            result["gifs"] = gifs

        if args.rpgmaker:
            walk_dirs = {d: [clip.composite(i + 1) for i in range(clip.n_frames)] for (act, d), clip in clips.items() if act == "walk"}
            if not walk_dirs:
                first_act = actions[0]
                walk_dirs = {d: [clip.composite(i + 1) for i in range(clip.n_frames)] for (act, d), clip in clips.items() if act == first_act}
            result["rpgmaker"] = export_rpgmaker_sheet(walk_dirs, out_dir / f"{prefix}_rpgmaker_3x4.png")

        if args.preview:
            prev_scale = max(2, min(8, 128 // max(w, h)))
            prev_path = out_dir / f"{prefix}_preview.png"
            master.preview_image(scale=prev_scale, cols=args.frames, labels=True).save(prev_path)
            result["preview"] = str(prev_path)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Generated {spec.archetype} ({w}x{h}, {master.n_frames} frames, {len(master.layers)} layers) -> {sheet_path}")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
