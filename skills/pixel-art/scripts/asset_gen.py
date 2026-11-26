#!/usr/bin/env python3
"""Generate game items, weapons, ZzSprite procedural creatures, and 9-slice UI components.

Usage:
    python scripts/asset_gen.py --category item --type sword --size 16 --output sword.png --json
    python scripts/asset_gen.py --category zzsprite --size 16 --seed 107 --palette pico-8 --output alien.png --json
    python scripts/asset_gen.py --category ui --type panel_9slice --size 48x48 --style fantasy --output panel.png --json
    python scripts/asset_gen.py --category ui --type button_3state --size 48x20 --output button.png --gif --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.assets import ITEM_TYPES, UI_TYPES, generate_item, generate_ui_asset, generate_zzsprite
from engine.exporters import export_gif, export_spritesheet


def parse_size(raw: str) -> tuple[int, int]:
    s = raw.lower().strip()
    if "x" in s:
        a, b = s.split("x", 1)
        return int(a), int(b)
    v = int(s)
    return v, v


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate pixel art game items, ZzSprite creatures, and 9-slice UI assets.")
    parser.add_argument("--category", type=str, required=True, choices=["item", "zzsprite", "ui"], help="Asset category")
    parser.add_argument("--type", type=str, default="sword", help=f"Item ({','.join(ITEM_TYPES)}) or UI ({','.join(UI_TYPES)})")
    parser.add_argument("--size", type=str, default="16", help="Canvas size: N or WxH")
    parser.add_argument("--style", type=str, default="fantasy", choices=["fantasy", "scifi", "minimal"], help="UI visual style")
    parser.add_argument("--palette", type=str, default="endesga-32", help="Palette name/JSON or 'none'")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic seed")
    parser.add_argument("--scale", type=int, default=1, help="Integer upscale factor")
    parser.add_argument("--gif", action="store_true", help="Export animated GIF for multi-frame UI assets")
    parser.add_argument("--output", type=str, required=True, help="Output PNG path")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    try:
        w, h = parse_size(args.size)
        pal = None if args.palette.lower() == "none" else args.palette
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)

        if args.category == "item":
            doc = generate_item(item_type=args.type, size=max(w, h), palette=pal, seed=args.seed)
            im = doc.composite(1)
            if args.scale > 1:
                im = im.resize((im.width * args.scale, im.height * args.scale), im.Resampling.NEAREST if hasattr(im, "Resampling") else 0)
            im.save(out)
            res = {"status": "ok", "category": "item", "type": args.type, "size": list(im.size), "output": str(out)}

        elif args.category == "zzsprite":
            doc = generate_zzsprite(size=max(w, h), seed=args.seed, palette=pal)
            im = doc.composite(1)
            if args.scale > 1:
                from PIL import Image
                im = im.resize((im.width * args.scale, im.height * args.scale), Image.Resampling.NEAREST)
            im.save(out)
            res = {"status": "ok", "category": "zzsprite", "seed": args.seed, "size": list(im.size), "output": str(out)}

        else:  # ui
            doc, ui_meta = generate_ui_asset(ui_type=args.type, width=w, height=h, style=args.style, palette=pal)
            if doc.n_frames == 1:
                im = doc.composite(1)
                if args.scale > 1:
                    from PIL import Image
                    im = im.resize((im.width * args.scale, im.height * args.scale), Image.Resampling.NEAREST)
                im.save(out)
                meta_p = out.with_suffix(".json")
                meta_p.write_text(json.dumps(ui_meta, indent=2), encoding="utf-8")
                res = {"status": "ok", "category": "ui", "meta": ui_meta, "output": str(out), "metadata": str(meta_p)}
            else:
                sheet_res = export_spritesheet(doc, out, cols=doc.n_frames, scale=args.scale)
                res = {"status": "ok", "category": "ui", "meta": ui_meta, "sheet": sheet_res}
                if args.gif:
                    imgs = [doc.composite(i + 1) for i in range(doc.n_frames)]
                    durs = [f.duration_ms for f in doc.frames]
                    res["gif"] = export_gif(imgs, out.with_suffix(".gif"), durations_ms=durs, scale=max(2, args.scale))

        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Generated {args.category}/{args.type} -> {out}")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
