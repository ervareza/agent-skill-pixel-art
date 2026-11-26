"""Comprehensive Pixel Art Quality Auditor & Animation/Tile Verification.

Inspired by MalloyTheDev/aseprite-mcp, with-pebbly/aseprite-ai-artist, and Gamezxz/pixel-art-studio:
- Semi-transparent pixel (anti-aliasing) detection
- Orphan / stray pixel detection (4-way and 8-way)
- Palette compliance & near-duplicate color detector
- Grid alignment (flexible: supports arbitrary 8x8, 9x9, 12x12, WxH!)
- Edge jaggies & doubled-pixel corner detection
- Silhouette fill ratio, centering, and edge clipping check
- Animation checks: loop continuity, empty/duplicate frames, foot-baseline drift
- Tile seamlessness check (left<->right and top<->bottom edge continuity)
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Sequence

from PIL import Image

from .color import load_palette, perceptual_dist2, rgba_to_hex


def audit_antialiasing(img: Image.Image) -> dict:
    w, h = img.size
    px = img.load()
    bad = 0
    for y in range(h):
        for x in range(w):
            a = px[x, y][3]
            if 0 < a < 255:
                bad += 1
    return {"semi_transparent_pixels": bad, "total_pixels": w * h, "clean": bad == 0}


def audit_orphans(img: Image.Image, connectivity: int = 8) -> dict:
    w, h = img.size
    px = img.load()
    nb = (
        [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if connectivity == 4
        else [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]
    )
    orphans: list[tuple[int, int]] = []
    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0:
                continue
            if not any(0 <= x + dx < w and 0 <= y + dy < h and px[x + dx, y + dy][3] > 0 for dx, dy in nb):
                orphans.append((x, y))
    return {"orphan_pixels": len(orphans), "positions": orphans[:20], "clean": len(orphans) == 0}


def audit_palette(
    img: Image.Image,
    max_colors: int = 256,
    palette: str | Path | Sequence[str] | None = None,
    dup_tol: int = 8,
) -> dict:
    w, h = img.size
    px = img.load()
    cnt: Counter = Counter()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 0:
                cnt[(r, g, b)] += 1
    colors = list(cnt.keys())
    off_palette: list[str] = []
    if palette is not None:
        _, pal_rgbas = load_palette(palette)
        pal_set = {p[:3] for p in pal_rgbas}
        off_palette = [rgba_to_hex(c) for c in colors if c not in pal_set]

    near_dups: list[tuple[str, str]] = []
    if len(colors) <= 64:
        for i in range(len(colors)):
            for j in range(i + 1, len(colors)):
                if max(abs(colors[i][k] - colors[j][k]) for k in range(3)) <= dup_tol:
                    near_dups.append((rgba_to_hex(colors[i]), rgba_to_hex(colors[j])))

    clean = len(colors) <= max_colors and len(off_palette) == 0
    return {
        "unique_colors": len(colors),
        "max_allowed": max_colors,
        "off_palette_colors": off_palette[:20],
        "near_duplicate_pairs": near_dups[:10],
        "clean": clean,
    }


def audit_grid(img: Image.Image, grid_size: int = 1) -> dict:
    w, h = img.size
    aligned = (w % grid_size == 0) and (h % grid_size == 0) if grid_size > 0 else True
    return {"width": w, "height": h, "grid_size": grid_size, "aligned": aligned}


def audit_silhouette_and_edges(img: Image.Image) -> dict:
    """Measure silhouette fill, bounding box, border clipping, and doubled-pixel corners."""
    w, h = img.size
    px = img.load()
    opaque = 0
    min_x, min_y, max_x, max_y = w, h, -1, -1
    for y in range(h):
        for x in range(w):
            if px[x, y][3] > 0:
                opaque += 1
                if x < min_x:
                    min_x = x
                if y < min_y:
                    min_y = y
                if x > max_x:
                    max_x = x
                if y > max_y:
                    max_y = y

    if opaque == 0:
        return {
            "empty": True,
            "fill_ratio": 0.0,
            "bbox": None,
            "touches_edges": [],
            "double_corners": 0,
        }

    touches = []
    if min_x == 0:
        touches.append("left")
    if max_x == w - 1:
        touches.append("right")
    if min_y == 0:
        touches.append("top")
    if max_y == h - 1:
        touches.append("bottom")

    # Count 1px outline L-shaped double corners on outer silhouette
    outline_mask = [[False] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if px[x, y][3] > 0:
                if any(not (0 <= x + dx < w and 0 <= y + dy < h) or px[x + dx, y + dy][3] == 0 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    outline_mask[y][x] = True

    doubles = 0
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if not outline_mask[y][x]:
                continue
            # Check for 3-pixel L-triad on a diagonal where center sits in corner
            for (dx1, dy1, dx2, dy2) in ((1, 0, 0, 1), (-1, 0, 0, 1), (1, 0, 0, -1), (-1, 0, 0, -1)):
                if outline_mask[y + dy1][x + dx1] and outline_mask[y + dy2][x + dx2]:
                    # Only flag if opposite diagonal is transparent (outer corner lump)
                    if px[x - dx1, y - dy2][3] == 0 and px[x + dx1, y + dy2][3] > 0:
                        doubles += 1
                        break

    return {
        "empty": False,
        "opaque_pixels": opaque,
        "fill_ratio": round(opaque / max(1, w * h), 3),
        "bbox": [min_x, min_y, max_x, max_y],
        "touches_edges": touches,
        "double_corners": doubles,
    }


def audit_seamless(img: Image.Image, threshold: float = 55.0) -> dict:
    """Measure 4-edge wrap continuity for seamless terrain tiles."""
    w, h = img.size
    px = img.load()
    lr_diffs = []
    for y in range(h):
        c1 = px[0, y]
        c2 = px[w - 1, y]
        lr_diffs.append((perceptual_dist2(c1, c2) ** 0.5) / 3.0)
    tb_diffs = []
    for x in range(w):
        c1 = px[x, 0]
        c2 = px[x, h - 1]
        tb_diffs.append((perceptual_dist2(c1, c2) ** 0.5) / 3.0)
    lr_avg = sum(lr_diffs) / max(1, len(lr_diffs))
    tb_avg = sum(tb_diffs) / max(1, len(tb_diffs))
    return {
        "horizontal_edge_delta": round(lr_avg, 2),
        "vertical_edge_delta": round(tb_avg, 2),
        "seamless": lr_avg <= threshold and tb_avg <= threshold,
    }


def audit_animation(frames: Sequence[Image.Image]) -> dict:
    """Verify animation hygiene: non-empty frames, non-static motion, foot-baseline stability, loop seam."""
    if not frames:
        return {"status": "fail", "issues": ["zero frames"]}
    w, h = frames[0].size
    empty_frames = []
    baselines = []
    pixel_counts = []
    identical_adjacent = 0

    for i, fr in enumerate(frames):
        im = fr.convert("RGBA")
        bbox = im.getbbox()
        if bbox is None:
            empty_frames.append(i + 1)
            continue
        baselines.append(bbox[3])
        px = im.load()
        cnt = sum(1 for y in range(h) for x in range(w) if px[x, y][3] > 0)
        pixel_counts.append(cnt)
        if i > 0 and im.tobytes() == frames[i - 1].convert("RGBA").tobytes():
            identical_adjacent += 1

    # Loop seam diff (last vs first frame)
    if len(frames) > 1:
        f0 = frames[0].convert("RGBA").load()
        fn = frames[-1].convert("RGBA").load()
        changed = sum(1 for y in range(h) for x in range(w) if f0[x, y] != fn[x, y])
        seam_diff_ratio = round(changed / max(1, w * h), 4)
    else:
        seam_diff_ratio = 0.0

    baseline_drift = (max(baselines) - min(baselines)) if baselines else 0
    volume_min = min(pixel_counts) if pixel_counts else 0
    volume_max = max(pixel_counts) if pixel_counts else 0

    issues = []
    if empty_frames:
        issues.append(f"empty frames: {empty_frames}")
    if len(frames) > 1 and identical_adjacent == len(frames) - 1:
        issues.append("all frames are identical (no motion)")

    return {
        "frame_count": len(frames),
        "empty_frames": empty_frames,
        "identical_adjacent_pairs": identical_adjacent,
        "foot_baseline_range_px": baseline_drift,
        "volume_px_range": [volume_min, volume_max],
        "loop_seam_diff_ratio": seam_diff_ratio,
        "clean": len(issues) == 0,
        "issues": issues,
    }


def audit_image(
    img: Image.Image,
    grid_size: int = 1,
    max_colors: int = 256,
    palette: str | Path | Sequence[str] | None = None,
    ignore_orphans: bool = False,
    check_seamless: bool = False,
) -> dict:
    """Run full pixel art quality audit on an image."""
    rgba = img.convert("RGBA")
    aa = audit_antialiasing(rgba)
    orphans = audit_orphans(rgba)
    pal = audit_palette(rgba, max_colors=max_colors, palette=palette)
    grid = audit_grid(rgba, grid_size=grid_size)
    sil = audit_silhouette_and_edges(rgba)

    passed = (
        aa["clean"]
        and (ignore_orphans or orphans["clean"])
        and pal["clean"]
        and grid["aligned"]
        and not sil["empty"]
    )
    report = {
        "status": "pass" if passed else "fail",
        "antialiasing": aa,
        "orphan_pixels": orphans,
        "palette": pal,
        "grid_alignment": grid,
        "silhouette": sil,
    }
    if check_seamless:
        seam = audit_seamless(rgba)
        report["seamless"] = seam
        if not seam["seamless"]:
            report["status"] = "fail"
    return report
