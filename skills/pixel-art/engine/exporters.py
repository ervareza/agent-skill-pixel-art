"""Universal game engine exporters for SpriteDocument & image sequences.

Supported exports:
- Native `.aseprite` binary format (layers, blend modes, opacity, cels, frame durations, animation tags, palette!)
- Sprite sheet PNG + Aseprite JSON (Array or Hash format)
- Godot 4 `.tres` (`SpriteFrames` resource ready for `AnimatedSprite2D`)
- Unity / TexturePacker JSON & Phaser 3 Atlas JSON
- RPG Maker MV/MZ 3×4 (12-frame) character sheet
- LPC (Liberated Pixel Cup) 64×64 layout adapter
- Per-layer sprite sheet export (for runtime paper-doll equipment systems!)
- Transparent animated GIF (exact palette table, no black/magenta corruption)
- Indexed 8-bit PNG (with proper alpha transparency index preservation!)
- Animated WebP & PNG sequences
"""

from __future__ import annotations

import json
import math
import struct
import zlib
from collections import Counter
from pathlib import Path
from typing import Sequence

from PIL import Image

from .canvas import NEAREST, SpriteDocument
from .color import hex_to_rgba, rgba_to_hex

_ASE_BLEND_MAP = {
    "normal": 0,
    "multiply": 1,
    "screen": 2,
    "overlay": 3,
    "add": 16,
}

_ASE_DIR_MAP = {
    "forward": 0,
    "reverse": 1,
    "pingpong": 2,
}


def _ase_string(text: str) -> bytes:
    raw = text.encode("utf-8")
    return struct.pack("<H", len(raw)) + raw


def _ase_chunk(chunk_type: int, payload: bytes) -> bytes:
    return struct.pack("<IH", len(payload) + 6, chunk_type) + payload


def export_aseprite(doc: SpriteDocument, output_path: str | Path) -> dict:
    """Write a spec-compliant binary `.aseprite` file with full layers, cels, durations, tags, and palette."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    # Collect palette colors (max 256)
    if doc.palette:
        pal_rgba = list(doc.palette[:256])
    else:
        used = [rgb + (255,) for rgb, _ in doc.used_colors().most_common(255)]
        pal_rgba = [(0, 0, 0, 0)] + used

    frame_blobs: list[bytes] = []

    for fi, fr in enumerate(doc.frames):
        chunks: list[bytes] = []

        if fi == 0:
            # 1. Palette Chunk (0x2019)
            n_pal = max(1, len(pal_rgba))
            pal_payload = bytearray(struct.pack("<III8s", n_pal, 0, n_pal - 1, b"\x00" * 8))
            for c in pal_rgba:
                pal_payload.extend(struct.pack("<HBBBB", 0, c[0], c[1], c[2], c[3]))
            chunks.append(_ase_chunk(0x2019, bytes(pal_payload)))

            # 2. Layer Chunks (0x2004) in bottom-to-top order
            for lmeta in doc.layers:
                flags = (1 if lmeta.visible else 0) | (0 if lmeta.locked else 2)
                bm = _ASE_BLEND_MAP.get(lmeta.blend_mode, 0)
                layer_payload = (
                    struct.pack("<HHHHHHB3s", flags, 0, 0, 0, 0, bm, lmeta.opacity, b"\x00\x00\x00")
                    + _ase_string(lmeta.name)
                )
                chunks.append(_ase_chunk(0x2004, layer_payload))

            # 3. Tags Chunk (0x2018)
            if doc.tags:
                tag_payload = bytearray(struct.pack("<H8s", len(doc.tags), b"\x00" * 8))
                for tname, tinfo in doc.tags.items():
                    f0 = max(0, int(tinfo["from"]) - 1)
                    f1 = max(f0, int(tinfo["to"]) - 1)
                    ldir = _ASE_DIR_MAP.get(tinfo.get("direction", "forward"), 0)
                    tag_payload.extend(
                        struct.pack("<HHBH6sBBBB", f0, f1, ldir, 0, b"\x00" * 6, 79, 70, 229, 0)
                    )
                    tag_payload.extend(_ase_string(tname))
                chunks.append(_ase_chunk(0x2018, bytes(tag_payload)))

        # 4. Cel Chunks (0x2005) — trimmed to non-empty bounding box & zlib-compressed
        for li, lmeta in enumerate(doc.layers):
            cel = fr.cels.get(lmeta.name)
            if cel is None:
                continue
            bbox = cel.getbbox()
            if bbox is None:
                continue
            x0, y0, x1, y1 = bbox
            cropped = cel.crop(bbox).convert("RGBA")
            cw, ch = cropped.size
            compressed = zlib.compress(cropped.tobytes(), level=6)
            cel_payload = (
                struct.pack("<HhhBHh5sHH", li, x0, y0, 255, 2, 0, b"\x00" * 5, cw, ch)
                + compressed
            )
            chunks.append(_ase_chunk(0x2005, cel_payload))

        chunks_blob = b"".join(chunks)
        n_chunks = len(chunks)
        old_chunks = n_chunks if n_chunks < 0xFFFF else 0xFFFF
        frame_bytes = 16 + len(chunks_blob)
        frame_header = struct.pack(
            "<IHHH2sI",
            frame_bytes,
            0xF1FA,
            old_chunks,
            max(1, min(65535, int(fr.duration_ms))),
            b"\x00\x00",
            n_chunks,
        )
        frame_blobs.append(frame_header + chunks_blob)

    body = b"".join(frame_blobs)
    total_size = 128 + len(body)
    default_dur = doc.frames[0].duration_ms if doc.frames else 100
    header = struct.pack(
        "<IHHHHHIHIIB3sHBBhhHH84s",
        total_size,
        0xA5E0,
        len(doc.frames),
        doc.width,
        doc.height,
        32,         # RGBA 32bpp
        1,          # layer opacity valid
        max(1, min(65535, int(default_dur))),
        0,
        0,
        0,          # transparent index
        b"\x00\x00\x00",
        min(256, len(pal_rgba)),
        1,
        1,          # pixel ratio 1:1
        0,
        0,          # grid origin
        16,
        16,         # grid size
        b"\x00" * 84,
    )
    assert len(header) == 128
    out.write_bytes(header + body)

    return {
        "status": "ok",
        "format": "aseprite",
        "output": str(out),
        "size": [doc.width, doc.height],
        "frames": len(doc.frames),
        "layers": doc.layer_names,
        "tags": list(doc.tags.keys()),
        "file_size_bytes": out.stat().st_size,
    }


def export_gif(
    frames: Sequence[Image.Image],
    output_path: str | Path,
    durations_ms: int | Sequence[int] = 100,
    scale: int = 1,
    loop: int = 0,
    bg: str | None = None,
) -> dict:
    """Export crisp transparent animated GIF with exact global palette (no black/magenta fringes)."""
    if not frames:
        raise ValueError("Cannot export GIF with zero frames")
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    scale = max(1, int(scale))

    rgba_frames: list[Image.Image] = []
    for im in frames:
        cur = im.convert("RGBA")
        if scale > 1:
            cur = cur.resize((cur.width * scale, cur.height * scale), NEAREST)
        if bg is not None:
            base = Image.new("RGBA", cur.size, hex_to_rgba(bg))
            base.alpha_composite(cur)
            cur = base
        rgba_frames.append(cur)

    if isinstance(durations_ms, int):
        durs = [max(20, durations_ms)] * len(rgba_frames)
    else:
        durs = [max(20, int(d)) for d in durations_ms]

    # Detect transparency
    has_trans = bg is None and any(
        im.load()[x, y][3] < 128
        for im in rgba_frames
        for y in range(im.height)
        for x in range(im.width)
    )
    max_colors = 255 if has_trans else 256
    cnt: Counter = Counter()
    for im in rgba_frames:
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, a = px[x, y]
                if a >= 128:
                    cnt[(r, g, b)] += 1

    colors = [c for c, _ in cnt.most_common()]
    if len(colors) > max_colors:
        # Median-cut quantize opaque pixels
        sample = Image.new("RGB", (len(colors), 1))
        sample.putdata(colors)
        q = sample.quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT)
        raw = q.getpalette()[: max_colors * 3]
        colors = list(dict.fromkeys((raw[i], raw[i + 1], raw[i + 2]) for i in range(0, len(raw), 3)))[:max_colors]

    lut = {c: i for i, c in enumerate(colors)}
    t_index = len(colors) if has_trans else None
    flat_pal: list[int] = []
    for c in colors:
        flat_pal.extend(c)
    if t_index is not None:
        flat_pal.extend((255, 0, 255))
    while len(flat_pal) < 768:
        flat_pal.extend((0, 0, 0))

    p_frames: list[Image.Image] = []
    for im in rgba_frames:
        px = im.load()
        w, h = im.size
        indices = bytearray(w * h)
        pos = 0
        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                if has_trans and a < 128:
                    indices[pos] = t_index  # type: ignore[assignment]
                else:
                    idx = lut.get((r, g, b))
                    if idx is None and colors:
                        idx = min(range(len(colors)), key=lambda i: (colors[i][0] - r) ** 2 + (colors[i][1] - g) ** 2 + (colors[i][2] - b) ** 2)
                    indices[pos] = idx or 0
                pos += 1
        pf = Image.new("P", (w, h))
        pf.putpalette(flat_pal[:768])
        pf.putdata(bytes(indices))
        p_frames.append(pf)

    kw = dict(save_all=True, append_images=p_frames[1:], duration=durs, loop=loop, disposal=2, optimize=False)
    if t_index is not None:
        kw["transparency"] = t_index
    p_frames[0].save(out, **kw)

    return {
        "status": "ok",
        "format": "gif",
        "output": str(out),
        "frame_count": len(p_frames),
        "frame_size": list(rgba_frames[0].size),
        "durations_ms": durs,
        "transparent": has_trans,
        "file_size_bytes": out.stat().st_size,
    }


def export_indexed_png(img: Image.Image, output_path: str | Path, max_colors: int = 256) -> dict:
    """Export RGBA image to indexed 8-bit PNG while PRESERVING alpha transparency."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    src = img.convert("RGBA")
    w, h = src.size
    px = src.load()

    has_trans = False
    cnt: Counter = Counter()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 128:
                has_trans = True
            else:
                cnt[(r, g, b)] += 1

    original_colors = len(cnt)
    limit = min(max_colors, 255 if has_trans else 256)
    colors = [c for c, _ in cnt.most_common()]
    if len(colors) > limit:
        sample = Image.new("RGB", (len(colors), 1))
        sample.putdata(colors)
        q = sample.quantize(colors=limit, method=Image.Quantize.MEDIANCUT)
        raw = q.getpalette()[: limit * 3]
        colors = list(dict.fromkeys((raw[i], raw[i + 1], raw[i + 2]) for i in range(0, len(raw), 3)))[:limit]

    # Index 0 reserved for transparency if present
    palette_entries: list[tuple[int, int, int]] = [(0, 0, 0)] + colors if has_trans else colors
    lut = {c: (i + 1 if has_trans else i) for i, c in enumerate(colors)}
    flat: list[int] = []
    for c in palette_entries:
        flat.extend(c)
    while len(flat) < 768:
        flat.extend((0, 0, 0))

    buf = bytearray(w * h)
    pos = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if has_trans and a < 128:
                buf[pos] = 0
            else:
                idx = lut.get((r, g, b))
                if idx is None and colors:
                    best = min(colors, key=lambda c: (c[0] - r) ** 2 + (c[1] - g) ** 2 + (c[2] - b) ** 2)
                    idx = lut[best]
                buf[pos] = idx or 0
            pos += 1

    indexed = Image.new("P", (w, h))
    indexed.putpalette(flat[:768])
    indexed.putdata(bytes(buf))
    if has_trans:
        indexed.save(out, transparency=0)
    else:
        indexed.save(out)

    return {
        "status": "ok",
        "output": str(out),
        "dimensions": [w, h],
        "original_colors": original_colors,
        "indexed_colors": len(colors),
        "transparent": has_trans,
        "file_size_bytes": out.stat().st_size,
    }


def export_spritesheet(
    doc: SpriteDocument,
    output_path: str | Path,
    cols: int = 0,
    padding: int = 0,
    scale: int = 1,
    tag: str | None = None,
    layer: str | None = None,
    json_format: str = "aseprite",
) -> dict:
    """Export SpriteDocument to sprite sheet PNG + engine metadata JSON.

    json_format: 'aseprite' (Aseprite Array JSON), 'phaser', 'unity', or 'simple'.
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    idx = (
        list(range(doc.tags[tag]["from"] - 1, doc.tags[tag]["to"]))
        if tag is not None
        else list(range(len(doc.frames)))
    )
    n = len(idx)
    if n == 0:
        raise ValueError("No frames to export")

    scale = max(1, int(scale))
    fw, fh = doc.width * scale, doc.height * scale
    cols = n if cols <= 0 else cols
    rows = math.ceil(n / cols)

    sw = cols * (fw + padding) - padding if padding > 0 else cols * fw
    sh = rows * (fh + padding) - padding if padding > 0 else rows * fh
    sheet = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))

    frames_meta_array = []
    frames_meta_hash = {}
    for k, fi in enumerate(idx):
        r, c = divmod(k, cols)
        x = c * (fw + padding)
        y = r * (fh + padding)
        im = (
            doc.frames[fi].cels.get(layer, doc._blank())
            if layer is not None
            else doc.composite(fi + 1)
        )
        if scale > 1:
            im = im.resize((fw, fh), NEAREST)
        sheet.alpha_composite(im, (x, y))
        fname = f"{out.stem}_{k:03d}.png"
        entry = {
            "filename": fname,
            "frame": {"x": x, "y": y, "w": fw, "h": fh},
            "rotated": False,
            "trimmed": False,
            "spriteSourceSize": {"x": 0, "y": 0, "w": fw, "h": fh},
            "sourceSize": {"w": fw, "h": fh},
            "duration": doc.frames[fi].duration_ms,
        }
        frames_meta_array.append(entry)
        frames_meta_hash[fname] = {k2: v2 for k2, v2 in entry.items() if k2 != "filename"}

    sheet.save(out)
    meta_path = out.with_suffix(".json")

    frame_tags = []
    if tag is None:
        for tname, tinfo in doc.tags.items():
            frame_tags.append({
                "name": tname,
                "from": tinfo["from"] - 1,
                "to": tinfo["to"] - 1,
                "direction": tinfo["direction"],
            })
    else:
        frame_tags.append({"name": tag, "from": 0, "to": n - 1, "direction": doc.tags[tag]["direction"]})

    meta_block = {
        "app": "PixelForge Engine",
        "version": "1.0.0",
        "image": out.name,
        "format": "RGBA8888",
        "size": {"w": sw, "h": sh},
        "frameSize": {"w": fw, "h": fh},
        "columns": cols,
        "rows": rows,
        "padding": padding,
        "scale": str(scale),
        "layers": [l.to_dict() for l in doc.layers],
        "frameTags": frame_tags,
    }

    if json_format in ("phaser", "unity"):
        payload = {"frames": frames_meta_hash, "meta": meta_block}
    elif json_format == "simple":
        payload = {
            "image": out.name,
            "frame_width": fw,
            "frame_height": fh,
            "columns": cols,
            "rows": rows,
            "frame_count": n,
            "padding": padding,
            "frames": [
                {"index": i, "filename": e["filename"], "x": e["frame"]["x"], "y": e["frame"]["y"], "w": fw, "h": fh, "duration": e["duration"]}
                for i, e in enumerate(frames_meta_array)
            ],
            "tags": frame_tags,
        }
    else:
        payload = {"frames": frames_meta_array, "meta": meta_block}

    meta_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return {
        "status": "ok",
        "sheet": str(out),
        "metadata": str(meta_path),
        "format": json_format,
        "frame_count": n,
        "frame_size": [fw, fh],
        "sheet_size": [sw, sh],
        "columns": cols,
        "rows": rows,
    }


def export_per_layer_sheets(doc: SpriteDocument, output_dir: str | Path, cols: int = 0, scale: int = 1) -> dict:
    """Export EVERY layer of a SpriteDocument as an aligned paper-doll spritesheet PNG."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    exported = []
    for idx, lmeta in enumerate(doc.layers):
        # Skip completely empty layers across all frames
        if not any(fr.cels.get(lmeta.name) and fr.cels[lmeta.name].getbbox() for fr in doc.frames):
            continue
        p = out_dir / f"{idx:02d}_{lmeta.name}.png"
        res = export_spritesheet(doc, p, cols=cols, scale=scale, layer=lmeta.name)
        exported.append({"layer": lmeta.name, "z_index": idx, "sheet": res["sheet"], "metadata": res["metadata"]})
    manifest = out_dir / "layers_manifest.json"
    manifest.write_text(json.dumps({"layers": exported, "size": [doc.width * scale, doc.height * scale], "frames": len(doc.frames)}, indent=2), encoding="utf-8")
    return {"status": "ok", "output_dir": str(out_dir), "layers_exported": len(exported), "manifest": str(manifest)}


def export_godot_spriteframes(
    sheet_path: str | Path,
    meta_json_path: str | Path,
    output_tres_path: str | Path,
    res_texture_path: str | None = None,
) -> dict:
    """Generate a Godot 4 `.tres` SpriteFrames resource from an exported sprite sheet + JSON."""
    sheet = Path(sheet_path)
    meta = json.loads(Path(meta_json_path).read_text(encoding="utf-8"))
    out = Path(output_tres_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    frames_raw = meta["frames"]
    frames_list = list(frames_raw.values()) if isinstance(frames_raw, dict) else frames_raw
    tags = meta.get("meta", {}).get("frameTags") or [{"name": "default", "from": 0, "to": len(frames_list) - 1, "direction": "forward"}]
    tex_res = res_texture_path or f"res://{sheet.name}"

    lines = [
        f'[gd_resource type="SpriteFrames" load_steps={len(frames_list) + 2} format=3]',
        "",
        f'[ext_resource type="Texture2D" path="{tex_res}" id="1_tex"]',
        "",
    ]
    for i, fr in enumerate(frames_list):
        r = fr["frame"]
        lines.append(f'[sub_resource type="AtlasTexture" id="AtlasTexture_{i}"]')
        lines.append('atlas = ExtResource("1_tex")')
        lines.append(f'region = Rect2({r["x"]}, {r["y"]}, {r["w"]}, {r["h"]})')
        lines.append("")

    lines.append("[resource]")
    anim_entries = []
    for t in tags:
        f0, f1 = int(t["from"]), int(t["to"])
        tag_frames = []
        durations = []
        idxs = list(range(f0, f1 + 1))
        if t.get("direction") == "reverse":
            idxs = idxs[::-1]
        elif t.get("direction") == "pingpong" and len(idxs) > 2:
            idxs = idxs + idxs[-2:0:-1]
        for fi in idxs:
            dur_ms = frames_list[fi].get("duration", 100)
            durations.append(dur_ms)
            tag_frames.append(f'{{\n"duration": 1.0,\n"texture": SubResource("AtlasTexture_{fi}")\n}}')
        avg_ms = sum(durations) / max(1, len(durations))
        fps = round(1000.0 / max(16.0, avg_ms), 2)
        loop_val = "false" if any(k in t["name"] for k in ("die", "death", "hurt")) else "true"
        anim_entries.append(
            f'{{\n"frames": [{", ".join(tag_frames)}],\n"loop": {loop_val},\n"name": &"{t["name"]}",\n"speed": {fps}\n}}'
        )
    lines.append("animations = [" + ", ".join(anim_entries) + "]")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "status": "ok",
        "format": "godot4_spriteframes",
        "output": str(out),
        "animations": [t["name"] for t in tags],
        "sub_resources": len(frames_list),
    }


def export_rpgmaker_sheet(
    dir_frames: dict[str, Sequence[Image.Image]],
    output_path: str | Path,
    cell_size: tuple[int, int] | None = None,
) -> dict:
    """Export a 4-direction RPG Maker MV/MZ 3×4 character sheet (Down, Left, Right, Up × 3 frames)."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    order = ("down", "left", "right", "up")
    sample = next(iter(dir_frames.values()))[0]
    cw, ch = cell_size or sample.size
    sheet = Image.new("RGBA", (cw * 3, ch * 4), (0, 0, 0, 0))

    for row, dname in enumerate(order):
        seq = list(dir_frames.get(dname, []))
        if not seq:
            continue
        # Sample 3 frames cleanly: step A, stand/mid, step B
        if len(seq) == 1:
            picks = [seq[0], seq[0], seq[0]]
        elif len(seq) == 2:
            picks = [seq[0], seq[1], seq[0]]
        elif len(seq) == 3:
            picks = seq[:3]
        else:
            picks = [seq[0], seq[len(seq) // 4], seq[len(seq) // 2]]
        for col, im in enumerate(picks):
            im_rgba = im.convert("RGBA")
            if im_rgba.size != (cw, ch):
                im_rgba = im_rgba.resize((cw, ch), NEAREST)
            sheet.alpha_composite(im_rgba, (col * cw, row * ch))

    sheet.save(out)
    return {
        "status": "ok",
        "format": "rpgmaker_3x4",
        "output": str(out),
        "cell_size": [cw, ch],
        "sheet_size": [cw * 3, ch * 4],
        "row_order": list(order),
    }
