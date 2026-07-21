# PixelMatrix Engine (v2.0.0)

> **Next-Generation Autonomous 2D Pixel Art, Tilemap, Character Matrix & Palette LUT Synthesis Engine for AI Agents and Game Developers.**

[![Version](https://img.shields.io/badge/version-v2.0.0-06b6d4.svg?style=for-the-badge)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-10b981.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-8b5cf6.svg?style=for-the-badge)](https://python.org)
[![Compatibility](https://img.shields.io/badge/agent-Claude%20Code%20%7C%20Codex%20%7C%20Antigravity-f59e0b.svg?style=for-the-badge)](#multi-agent-integration)

---

## 🌟 Value Proposition

**PixelMatrix Engine** completely reimagines 2D pixel art synthesis for AI Agents. It decouples creative generation from deterministic raster engineering—enforcing strict grid alignment, hardware color palette LUTs, zero anti-aliasing artifacts, and structured texture atlas packing with JSON metadata.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PIXELMATRIX ENGINE v2.0.0                          │
└─────────────────────────────────────────────────────────────────────────────┘
          │                                                       │
          ▼                                                       ▼
┌───────────────────────────┐                           ┌────────────────────┐
│   Specification Indexes   │                           │ Python CLI Engines │
├───────────────────────────┤                           ├────────────────────┤
│ • Grid Canvas Presets     │                           │ • Initializer      │
│ • Palette LUT Definitions │                           │ • LUT Synthesizer  │
│ • Sprite Matrix Specs     │                           │ • Spec Inspector   │
└─────────┬─────────────────┘                           │ • PostProcessor    │
          │                                             │ • Atlas Compiler   │
          └───────────────────────────┬─────────────────┴────────────────────┘
                                      │
                                      ▼
                   ┌──────────────────────────────────────┐
                   │  Production Game Assets & JSON Meta  │
                   │  (Godot / Unity / Defold / Web Canvas│
                   └──────────────────────────────────────┘
```

---

## ⚡ Installation & Skill Injection

### Option 1: Direct Agent Skill Injection (Recommended for Claude Code & Antigravity IDE)
Copy the `skills/pixelmatrix-engine` folder into your agent's skill root:
```bash
# Antigravity IDE / Global Gemini Skill Root
mkdir -p ~/.gemini/config/skills/
cp -r skills/pixelmatrix-engine ~/.gemini/config/skills/

# Claude Code Agent Injection
cp -r skills/pixelmatrix-engine ~/.claude/skills/
```

### Option 2: Package Managers (`npm` / `pnpm` / `cargo` / `pip`)
```bash
# Node / npm
npm install -g pixelmatrix-engine

# pnpm
pnpm add -g pixelmatrix-engine

# Rust / Cargo
cargo install pixelmatrix-engine

# Python / Pip
pip install -r skills/pixelmatrix-engine/requirements.txt
```

---

## 🚀 CLI Engine Execution Matrix

| Engine CLI Script | Primary Function | Command Trigger Example |
| :--- | :--- | :--- |
| **`canvas_initializer.py`** | Initialize workspace & contracts | `python3 skills/pixelmatrix-engine/scripts/canvas_initializer.py --asset-name hero --preset standard_sprite_32 --palette pico8_fantasy_16 --json` |
| **`lut_synthesizer.py`** | Color extraction & LUT remapping | `python3 skills/pixelmatrix-engine/scripts/lut_synthesizer.py --image raw.png --json` |
| **`spec_inspector.py`** | Quality control & AA detection | `python3 skills/pixelmatrix-engine/scripts/spec_inspector.py --image sprite.png --width 32 --height 32 --max-colors 16 --json` |
| **`raster_processor.py`** | Clean AA, orphan clean & export PNG | `python3 skills/pixelmatrix-engine/scripts/raster_processor.py --input raw.png --output clean.png --max-colors 16 --json` |
| **`atlas_compiler.py`** | Texture atlas & JSON manifest packing | `python3 skills/pixelmatrix-engine/scripts/atlas_compiler.py --frames-dir ./frames/ --output atlas.png --width 32 --height 32 --json` |

---

## 🤖 Multi-Agent Integration

### 1. Claude Code
In Claude Code CLI, reference the skill using:
```bash
claude "Create a 32x32 isometric terrain tile using pixelmatrix-engine with Cyberpunk LUT"
```

### 2. OpenAI Codex
In OpenAI Codex environments, include the skill path in prompt context:
```python
# System prompt context points to skills/pixelmatrix-engine/SKILL.md
```

### 3. Antigravity IDE
In Antigravity IDE, invoke using `@pixelmatrix-engine` or mention pixel art sprite synthesis in chat.

---

## 📄 License & Standards

Licensed under the [MIT License](LICENSE). Built for high-performance 2D game asset creation.
