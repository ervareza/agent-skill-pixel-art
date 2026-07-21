#!/usr/bin/env python3
"""
Convert a sprite sheet into an animated GIF.

Usage:
    python scripts/gif_export.py --sheet walk.png --frame-width 16 --frame-height 16 --fps 8 --output walk.gif --json
    python scripts/gif_export.py --frames-dir ./frames/ --fps 10 --output anim.gif --json
    python scripts/gif_export.py --help
"""

import sys
import json
import argparse
from pathlib import Path
from PIL import Image


def sheet_to_gif(sheet_path: Path, fw: int, fh: int, fps: int, output: Path, cols: int = 0) -> dict:
    img = Image.open(sheet_path).convert("RGBA")
    sw, sh = img.size
    if cols <= 0:
        cols = sw // fw
    rows = sh // fh
    frames = []
    for r in range(rows):
        for c in range(cols):
            x, y = c * fw, r * fh
            if x + fw <= sw and y + fh <= sh:
                frame = img.crop((x, y, x + fw, y + fh))
                bg = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
                bg.paste(frame, (0, 0))
                frames.append(bg)

    if not frames:
        raise ValueError("No frames extracted from sheet")

    output.parent.mkdir(parents=True, exist_ok=True)
    duration = max(1, 1000 // fps)
    frames[0].save(output, save_all=True, append_images=frames[1:], duration=duration, loop=0, disposal=2)

    return {
        "status": "ok",
        "output": str(output),
        "frame_count": len(frames),
        "frame_size": [fw, fh],
        "fps": fps,
        "duration_ms": duration,
        "file_size_bytes": output.stat().st_size,
    }


def frames_to_gif(frames_dir: Path, fps: int, output: Path) -> dict:
    files = sorted([f for f in frames_dir.iterdir() if f.suffix.lower() == ".png"], key=lambda f: f.stem)
    if not files:
        raise ValueError(f"No PNG files found in {frames_dir}")

    frames = [Image.open(f).convert("RGBA") for f in files]
    fw, fh = frames[0].size
    output.parent.mkdir(parents=True, exist_ok=True)
    duration = max(1, 1000 // fps)
    frames[0].save(output, save_all=True, append_images=frames[1:], duration=duration, loop=0, disposal=2)

    return {
        "status": "ok",
        "output": str(output),
        "frame_count": len(frames),
        "frame_size": [fw, fh],
        "fps": fps,
        "duration_ms": duration,
        "file_size_bytes": output.stat().st_size,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Convert a sprite sheet or directory of frames into an animated GIF."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sheet", type=str, help="Sprite sheet PNG path")
    group.add_argument("--frames-dir", type=str, help="Directory containing frame PNGs")
    parser.add_argument("--frame-width", type=int, default=0, help="Frame width (required with --sheet)")
    parser.add_argument("--frame-height", type=int, default=0, help="Frame height (required with --sheet)")
    parser.add_argument("--cols", type=int, default=0, help="Columns in sheet (auto-detect if 0)")
    parser.add_argument("--fps", type=int, default=8, help="Frames per second (default: 8)")
    parser.add_argument("--output", type=str, required=True, help="Output GIF path")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    try:
        if args.sheet:
            if args.frame_width <= 0 or args.frame_height <= 0:
                raise ValueError("--frame-width and --frame-height required with --sheet")
            result = sheet_to_gif(Path(args.sheet), args.frame_width, args.frame_height, args.fps, Path(args.output), args.cols)
        else:
            result = frames_to_gif(Path(args.frames_dir), args.fps, Path(args.output))

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Exported {result['frame_count']} frames → {args.output} ({args.fps} FPS)")
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}) if args.json else f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
