"""Comprehensive automated test suite for PixelForge Engine v1.0.0 & all 21 CLI tools."""

from __future__ import annotations

import json
import struct
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_ROOT = REPO_ROOT / "skills" / "pixel-art"
SCRIPTS_DIR = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SKILL_ROOT))

from engine import SpriteDocument, ColorRamp, hue_ramp, list_palettes, load_palette
from engine.assets import (
    ITEM_TYPES,
    STACK_PRESETS,
    UI_TYPES,
    build_stack_preset,
    generate_item,
    generate_ui_asset,
    generate_zzsprite,
    render_stack_turntable,
)
from engine.character import ACTIONS, ARCHETYPES, RIG_LAYERS, build_character_action, build_character_pack
from engine.exporters import (
    export_aseprite,
    export_gif,
    export_godot_spriteframes,
    export_indexed_png,
    export_per_layer_sheets,
    export_rpgmaker_sheet,
    export_spritesheet,
)
from engine.qa import audit_animation, audit_image, audit_seamless
from engine.tileset import (
    TERRAIN_PRESETS,
    generate_animated_tile,
    generate_autotile_sheet,
    generate_isometric_block,
    generate_seamless_tile,
)
from engine.vfx import VFX_TYPES, generate_vfx


# ---------------------------------------------------------------------------
# 1. Color & Palette Tests
# ---------------------------------------------------------------------------

def test_all_16_palettes_load():
    pals = list_palettes()
    assert len(pals) >= 16
    for name in pals:
        pname, cols = load_palette(name)
        assert pname
        assert len(cols) >= 2
        for c in cols:
            assert len(c) == 4 and c[3] == 255


def test_hue_ramp_shifts_hue_and_luminance():
    ramp = hue_ramp("#CC3333", steps=5, hue_shift=20.0)
    assert len(ramp) == 5
    assert ramp[2] == "#CC3333"
    assert len(set(ramp)) == 5


# ---------------------------------------------------------------------------
# 2. Multi-Layer Canvas, Blend Modes, Linked Cels & Cleanup Pipeline
# ---------------------------------------------------------------------------

def test_layers_blend_modes_and_project_roundtrip(tmp_path: Path):
    doc = SpriteDocument(16, 16, palette="pico-8")
    doc.ensure_rig_layers(["bg", "body", "glow"])
    doc.layer("bg").rect(0, 0, 15, 15, "#1D2B53")
    doc.layer("body").circle(8, 8, 4, "#FF004D", fill=True)
    doc.layer("glow", blend_mode="add", opacity=180).circle(8, 8, 2, "#FFEC27", fill=True)
    doc.add_frame(copy=True)
    doc.link_cel(layer="bg", from_frame=1, to_frames=[2])
    doc.tag("pulse", 1, 2, direction="pingpong")

    proj = doc.save_project(tmp_path / "test.pxproj.json")
    loaded = SpriteDocument.load_project(proj)
    assert loaded.width == 16 and loaded.height == 16
    assert loaded.layer_names == ["bg", "body", "glow"]
    assert loaded.n_frames == 2
    assert loaded.tags["pulse"]["direction"] == "pingpong"
    assert loaded.composite(1).size == (16, 16)
    assert "Legend:" in loaded.ascii_view(1)


def test_cleanup_pipeline_removes_aa_and_locks_palette(tmp_path: Path):
    # Create messy image with semi-transparent AA, checkerboard bg, and single orphan pixel
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = im.load()
    for y in range(4, 12):
        for x in range(4, 12):
            px[x, y] = (200, 50, 60, 255)
    px[3, 5] = (200, 50, 60, 120)   # semi-transparent AA
    px[14, 14] = (255, 0, 0, 255)   # orphan pixel
    src = tmp_path / "messy.png"
    im.save(src)

    doc = SpriteDocument.from_png(src, scale=1)
    doc.clean(palette="pico-8", despeckle_min=2, dedupe_tol=10)
    cleaned = doc.composite(1)
    qa = audit_image(cleaned, grid_size=1, palette="pico-8")
    assert qa["status"] == "pass"
    assert qa["antialiasing"]["semi_transparent_pixels"] == 0
    assert qa["orphan_pixels"]["orphan_pixels"] == 0
    assert qa["palette"]["off_palette_colors"] == []


# ---------------------------------------------------------------------------
# 3. Character Engine: Arbitrary Sizes, Frame Counts, Directions, Actions, Archetypes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("w,h", [(8, 8), (9, 9), (12, 12), (16, 16), (16, 24), (24, 24), (32, 32), (48, 48), (64, 64)])
def test_character_arbitrary_resolutions(w: int, h: int):
    doc = build_character_action(w, h, action="walk", direction="down", frames=4, archetype="hero", palette="endesga-32")
    assert (doc.width, doc.height) == (w, h)
    assert doc.n_frames == 4
    assert doc.layer_names == RIG_LAYERS
    qa = audit_image(doc.composite(1), grid_size=1, palette="endesga-32")
    assert qa["status"] == "pass", f"QA failed at {w}x{h}: {qa}"


@pytest.mark.parametrize("n_frames", [2, 3, 4, 5, 6, 8, 12, 24, 60])
def test_character_arbitrary_frame_counts(n_frames: int):
    doc = build_character_action(24, 24, action="walk", direction="right", frames=n_frames, fps=min(60, max(6, n_frames)), archetype="hero")
    assert doc.n_frames == n_frames
    frames = [doc.composite(i + 1) for i in range(n_frames)]
    anim_qa = audit_animation(frames)
    assert anim_qa["clean"], f"Animation failed for {n_frames} frames: {anim_qa}"
    assert anim_qa["foot_baseline_range_px"] <= 1


def test_character_4dir_and_8dir_are_visually_distinct():
    # Prove Down, Left, Right, Up are genuinely distinct facings (NOT identical like old v5.0.0!)
    imgs = {}
    for d in ("down", "left", "right", "up", "se", "sw", "ne", "nw"):
        doc = build_character_action(32, 32, action="walk", direction=d, frames=4, archetype="hero")
        imgs[d] = doc.composite(1).tobytes()
    assert len(set(imgs.values())) == 8, "All 8 directions must produce distinct pixel artwork"


@pytest.mark.parametrize("action", ACTIONS)
def test_character_all_8_actions(action: str):
    doc = build_character_action(32, 32, action=action, direction="right", frames=6, archetype="knight")
    assert doc.n_frames == 6
    assert all(doc.composite(i + 1).getbbox() is not None for i in range(6))


@pytest.mark.parametrize("archetype", ARCHETYPES)
def test_character_all_9_archetypes(archetype: str):
    doc = build_character_action(32, 32, action="walk", direction="down", frames=4, archetype=archetype, palette="endesga-32")
    qa = audit_image(doc.composite(1), grid_size=1, palette="endesga-32")
    assert qa["status"] == "pass", f"{archetype} QA failed: {qa}"


# ---------------------------------------------------------------------------
# 4. Exporters: Native .aseprite Binary, Godot 4 .tres, RPG Maker 3x4, Indexed PNG, GIF
# ---------------------------------------------------------------------------

def test_native_aseprite_binary_format_and_engine_exports(tmp_path: Path):
    master, clips = build_character_pack(
        width=32, height=32, actions=("idle", "walk"), directions="4", frames=4, fps=10, archetype="hero"
    )
    ase_path = tmp_path / "hero.aseprite"
    ase_res = export_aseprite(master, ase_path)
    raw = ase_path.read_bytes()
    # Verify Aseprite 128-byte header magic (0xA5E0), frame count, dimensions, 32bpp RGBA
    fsize, magic, frames, w, h, bpp = struct.unpack_from("<IHHHHH", raw, 0)
    assert fsize == len(raw)
    assert magic == 0xA5E0
    assert frames == master.n_frames == 32
    assert (w, h) == (32, 32)
    assert bpp == 32
    # Verify first frame magic (0xF1FA) at offset 128
    _, fmagic = struct.unpack_from("<IH", raw, 128)
    assert fmagic == 0xF1FA
    assert len(ase_res["layers"]) == len(RIG_LAYERS)

    # Spritesheet + Godot 4 .tres + Per-layer sheets + RPG Maker 3x4 + Indexed PNG + GIF
    sheet_path = tmp_path / "hero_sheet.png"
    export_spritesheet(master, sheet_path, cols=4, json_format="aseprite")
    tres = tmp_path / "hero.tres"
    gres = export_godot_spriteframes(sheet_path, sheet_path.with_suffix(".json"), tres)
    assert tres.exists() and 'type="SpriteFrames"' in tres.read_text(encoding="utf-8")
    assert len(gres["animations"]) == 8

    layer_res = export_per_layer_sheets(master, tmp_path / "layers", cols=4)
    assert layer_res["layers_exported"] >= 8

    walk_dirs = {d: [clips[("walk", d)].composite(i + 1) for i in range(4)] for d in ("down", "left", "right", "up")}
    rpg = export_rpgmaker_sheet(walk_dirs, tmp_path / "rpgmaker.png")
    assert rpg["sheet_size"] == [96, 128]

    idx_path = tmp_path / "indexed.png"
    idx_res = export_indexed_png(master.composite(1), idx_path, max_colors=32)
    assert idx_res["transparent"] is True
    idx_img = Image.open(idx_path)
    assert idx_img.mode == "P" and "transparency" in idx_img.info

    gif_path = tmp_path / "walk.gif"
    gif_res = export_gif(walk_dirs["down"], gif_path, durations_ms=100, scale=2)
    assert gif_res["transparent"] is True and gif_path.stat().st_size > 100


# ---------------------------------------------------------------------------
# 5. Tilesets, Autotiles (Wang 16 & Blob 47), Isometric, VFX, Items, UI, Sprite Stacking
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("terrain", sorted(TERRAIN_PRESETS.keys()))
def test_seamless_tiles_and_autotiles(terrain: str):
    tile = generate_seamless_tile(16, terrain=terrain, palette="endesga-32", seed=42)
    assert tile.size == (16, 16)
    qa = audit_image(tile, grid_size=16, palette="endesga-32")
    assert qa["antialiasing"]["clean"]
    assert qa["palette"]["clean"]


def test_wang16_blob47_animated_and_isometric():
    s16, m16 = generate_autotile_sheet(16, "grass", "wang16", palette="endesga-32")
    assert m16["tile_count"] == 16 and s16.size == (64, 64)

    s47, m47 = generate_autotile_sheet(16, "stone", "blob47", palette="endesga-32")
    assert m47["tile_count"] == 47

    anim = generate_animated_tile(16, "water", frames=6, fps=6, palette="endesga-32")
    assert anim.n_frames == 6

    iso = generate_isometric_block(64, "grass", palette="endesga-32")
    assert iso.width == 64 and iso.height == 48
    assert audit_image(iso, grid_size=1, palette="endesga-32")["status"] == "pass"


@pytest.mark.parametrize("vtype", VFX_TYPES)
def test_all_12_vfx(vtype: str):
    doc = generate_vfx(vtype, 24, 24, frames=6, fps=12, palette="endesga-32")
    assert doc.n_frames == 6
    qa = audit_image(doc.composite(2), grid_size=1, palette="endesga-32", ignore_orphans=True)
    assert qa["status"] == "pass", f"VFX {vtype} failed QA: {qa}"


def test_items_zzsprite_ui_and_sprite_stacking():
    for it in ITEM_TYPES:
        doc = generate_item(it, 16, palette="endesga-32")
        assert audit_image(doc.composite(1), grid_size=16, palette="endesga-32")["status"] == "pass"

    zz = generate_zzsprite(16, seed=77, palette="pico-8")
    assert audit_image(zz.composite(1), grid_size=16, palette="pico-8")["status"] == "pass"

    for ut in UI_TYPES:
        doc, meta = generate_ui_asset(ut, 32, 16 if ut in ("health_bar", "button_3state") else 32)
        assert doc.composite(1).getbbox() is not None

    for preset in STACK_PRESETS:
        strip, meta = build_stack_preset(preset, 16, 20, 10, palette="endesga-32")
        assert strip.size == (160, 20)
    tt = render_stack_turntable(strip, 10, frames=8, fps=12)
    assert tt.n_frames == 8 and tt.composite(1).getbbox() is not None


# ---------------------------------------------------------------------------
# 6. CLI Smoke Tests Across All 21 Scripts
# ---------------------------------------------------------------------------

def test_all_21_cli_scripts_help_and_key_commands(tmp_path: Path):
    scripts = sorted(SCRIPTS_DIR.glob("*.py"))
    assert len(scripts) == 21
    for sc in scripts:
        proc = subprocess.run([sys.executable, str(sc), "--help"], capture_output=True, text=True)
        assert proc.returncode == 0, f"{sc.name} --help failed: {proc.stderr}"

    # End-to-end CLI pipeline test via pixel_studio.py
    p_info = subprocess.run([sys.executable, str(SCRIPTS_DIR / "pixel_studio.py"), "info", "--json"], capture_output=True, text=True)
    assert p_info.returncode == 0
    assert json.loads(p_info.stdout)["version"] == "1.0.0"

    p_char = subprocess.run(
        [
            sys.executable, str(SCRIPTS_DIR / "character_gen.py"),
            "--archetype", "mage", "--size", "16", "--dirs", "4", "--actions", "walk",
            "--frames", "4", "--fps", "8", "--output-dir", str(tmp_path / "cli_mage"),
            "--aseprite", "--gif", "--godot", "--rpgmaker", "--export-layers", "--preview", "--json",
        ],
        capture_output=True, text=True,
    )
    assert p_char.returncode == 0, p_char.stderr
    data = json.loads(p_char.stdout)
    assert data["status"] == "ok" and data["qa_frame1"] == "pass"

    p_audit = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "quality_audit.py"), "--image", data["sheet"]["sheet"], "--palette", "endesga-32", "--json"],
        capture_output=True, text=True,
    )
    assert p_audit.returncode == 0, p_audit.stdout
