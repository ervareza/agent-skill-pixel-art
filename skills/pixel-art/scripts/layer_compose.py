#!/usr/bin/env python3
"""Compose, inspect, toggle, and export multi-layer pixel art projects (.pxproj.json / PNG layers -> .aseprite / sheet).

Usage:
    python scripts/layer_compose.py --layers shadow:shadow.png,body:body.png,weapon:sword.png --output composite.png --aseprite hero.aseprite --json
    python scripts/layer_compose.py --project hero.pxproj.json --hide cape_back,weapon --output hero_nocape.png --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.canvas import SpriteDocument
from engine.exporters import export_aseprite, export_per_layer_sheets, export_spritesheet


def main() -> None:
    parser = argparse.ArgumentParser(description="Compose and manipulate multi-layer pixel art rigs and .aseprite files.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--project", type=str, help="Existing .pxproj.json project file")
    group.add_argument("--layers", type=str, help="Comma-separated bottom-to-top name:path pairs (e.g. shadow:s.png,body:b.png)")
    parser.add_argument("--hide", type=str, default="", help="Comma-separated layer names to hide")
    parser.add_argument("--show-only", type=str, default="", help="Comma-separated layer names to show exclusively")
    parser.add_argument("--opacity", type=str, default="", help="Comma-separated layer:0-255 opacity overrides")
    parser.add_argument("--blend", type=str, default="", help="Comma-separated layer:mode blend overrides (normal|multiply|screen|add|overlay)")
    parser.add_argument("--output", type=str, default="", help="Output composited PNG (or spritesheet if multi-frame)")
    parser.add_argument("--aseprite", type=str, default="", help="Export layered native .aseprite path")
    parser.add_argument("--save-project", type=str, default="", help="Save updated .pxproj.json")
    parser.add_argument("--split-dir", type=str, default="", help="Export every layer as its own PNG sheet")
    parser.add_argument("--cols", type=int, default=0, help="Sheet columns for multi-frame output")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    try:
        if args.project:
            doc = SpriteDocument.load_project(args.project)
        else:
            pairs = [p.strip() for p in args.layers.split(",") if p.strip()]
            loaded = []
            for p in pairs:
                if ":" in p:
                    name, fpath = p.split(":", 1)
                else:
                    fpath = p
                    name = Path(p).stem
                im = Image.open(fpath).convert("RGBA")
                loaded.append((name.strip(), im))
            if not loaded:
                raise ValueError("No layers provided")
            w, h = loaded[0][1].size
            doc = SpriteDocument(w, h, snap=False)
            doc.ensure_rig_layers([n for n, _ in loaded])
            for name, im in loaded:
                doc.frames[0].cels[name] = im if im.size == (w, h) else im.resize((w, h), Image.Resampling.NEAREST)

        if args.show_only:
            keep = {n.strip() for n in args.show_only.split(",") if n.strip()}
            for l in doc.layers:
                l.visible = l.name in keep
        if args.hide:
            for n in args.hide.split(","):
                n = n.strip()
                if n and n in doc.layer_names:
                    doc.set_layer_visibility(n, False)
        if args.opacity:
            for item in args.opacity.split(","):
                if ":" in item:
                    ln, val = item.split(":", 1)
                    doc.layer(ln.strip(), opacity=int(val))
        if args.blend:
            for item in args.blend.split(","):
                if ":" in item:
                    ln, bm = item.split(":", 1)
                    doc.layer(ln.strip(), blend_mode=bm.strip())

        res: dict = {
            "status": "ok",
            "size": [doc.width, doc.height],
            "frames": doc.n_frames,
            "layers": [l.to_dict() for l in doc.layers],
        }

        if args.output:
            out = Path(args.output)
            out.parent.mkdir(parents=True, exist_ok=True)
            if doc.n_frames == 1:
                doc.composite(1).save(out)
                res["output"] = str(out)
            else:
                res["sheet"] = export_spritesheet(doc, out, cols=args.cols)

        if args.aseprite:
            res["aseprite"] = export_aseprite(doc, args.aseprite)

        if args.save_project:
            res["project"] = str(doc.save_project(args.save_project))

        if args.split_dir:
            res["split"] = export_per_layer_sheets(doc, args.split_dir, cols=args.cols)

        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Composed {len(doc.layers)} layers ({doc.width}x{doc.height}, {doc.n_frames}f)")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
