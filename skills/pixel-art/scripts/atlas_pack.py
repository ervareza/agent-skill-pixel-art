#!/usr/bin/env python3
"""
Pack multiple sprite frames into a single sprite sheet PNG with JSON metadata.

Usage:
    python scripts/atlas_pack.py --frames-dir ./frames --output sheet.png --json
    python scripts/atlas_pack.py --frames-dir ./frames --output sheet.png --cols 4 --json
    python scripts/atlas_pack.py --help
"""

import sys
import json
import argparse
from pathlib import Path
from PIL import Image


def pack_atlas(frames_dir: Path, output_path: Path, cols: int = 0, padding: int = 0) -> dict:
    frames_dir = frames_dir.resolve()
    frame_files = sorted(
        [f for f in frames_dir.iterdir() if f.suffix.lower() == ".png"],
        key=lambda f: f.stem
    )

    if not frame_files:
        raise ValueError(f"No PNG files found in {frames_dir}")

    frames = [Image.open(f).convert("RGBA") for f in frame_files]
    fw, fh = frames[0].size
    count = len(frames)

    if cols <= 0:
        cols = count
    rows = (count + cols - 1) // cols

    sheet_w = cols * (fw + padding) - padding
    sheet_h = rows * (fh + padding) - padding
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))

    frame_data = []
    for i, frame in enumerate(frames):
        col = i % cols
        row = i // cols
        x = col * (fw + padding)
        y = row * (fh + padding)
        sheet.paste(frame, (x, y))
        frame_data.append({
            "index": i,
            "filename": frame_files[i].name,
            "x": x,
            "y": y,
            "w": fw,
            "h": fh,
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path)

    meta_path = output_path.with_suffix(".json")
    meta = {
        "image": output_path.name,
        "frame_width": fw,
        "frame_height": fh,
        "columns": cols,
        "rows": rows,
        "frame_count": count,
        "padding": padding,
        "frames": frame_data,
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    return {
        "status": "ok",
        "sheet": str(output_path),
        "metadata": str(meta_path),
        "frame_count": count,
        "sheet_size": [sheet_w, sheet_h],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Pack sprite frames into a single sprite sheet with JSON metadata."
    )
    parser.add_argument("--frames-dir", type=str, required=True, help="Directory containing frame PNGs")
    parser.add_argument("--output", type=str, required=True, help="Output sprite sheet PNG path")
    parser.add_argument("--cols", type=int, default=0, help="Columns per row (default: all frames in one row)")
    parser.add_argument("--padding", type=int, default=0, help="Padding between frames in pixels (default: 0)")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    try:
        result = pack_atlas(Path(args.frames_dir), Path(args.output), args.cols, args.padding)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Packed {result['frame_count']} frames → {result['sheet']}")
            print(f"Metadata → {result['metadata']}")
        sys.exit(0)
    except Exception as e:
        msg = str(e)
        print(json.dumps({"status": "error", "message": msg}) if args.json else f"Error: {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
