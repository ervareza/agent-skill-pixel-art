# ChromaMatrix Core (v3.0.0)

> **Next-Generation Autonomous 2D Pixel Art, Tilemap, Character Matrix & Luma Palette Synthesis Engine for AI Agents and Game Developers.**

[![Version](https://img.shields.io/badge/version-v3.0.0-06b6d4.svg?style=for-the-badge)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-10b981.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-8b5cf6.svg?style=for-the-badge)](https://python.org)
[![Compatibility](https://img.shields.io/badge/agent-Claude%20Code%20%7C%20Codex%20%7C%20Antigravity-f59e0b.svg?style=for-the-badge)](#multi-agent-integration)

---

## 🌟 Value Proposition

**ChromaMatrix Core** redefines 2D pixel art synthesis for AI Agents. It decouples creative generation from deterministic raster engineering—enforcing strict grid snapping, hardware LumaLUTs, zero anti-aliasing artifacts, and structured texture atlas synthesis with JSON manifests.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CHROMAMATRIX CORE v3.0.0                            │
└─────────────────────────────────────────────────────────────────────────────┘
          │                                                       │
          ▼                                                       ▼
┌───────────────────────────┐                           ┌────────────────────┐
│      ManifestVault        │                           │RenderOrchestrators │
├───────────────────────────┤                           ├────────────────────┤
│ • GridMatrices            │                           │ • Bootstrapper     │
│ • LumaPalettes            │                           │ • ChromaSynthesizer│
│ • SpriteCore              │                           │ • QualitySentinel  │
└─────────┬─────────────────┘                           │ • RasterRefiner    │
          │                                             │ • AtlasSynthesizer │
          └───────────────────────────┬─────────────────┴────────────────────┘
                                      │
                                      ▼
                   ┌──────────────────────────────────────┐
                   │  Production Game Assets & JSON Meta  │
                   │  (Godot / Unity / Defold / Web Canvas│
                   └──────────────────────────────────────┘
```

---

## ⚡ Installation & Skill Binding

### Option 1: Direct Skill Registration (Claude Code & Antigravity IDE)
Copy the `skills/chromamatrix-core` folder into your agent's skill root:
```bash
# Antigravity IDE / Global Gemini Skill Root
mkdir -p ~/.gemini/config/skills/
cp -r skills/chromamatrix-core ~/.gemini/config/skills/

# Claude Code Skill Registration
cp -r skills/chromamatrix-core ~/.claude/skills/
```

### Option 2: Package Managers (`npm` / `pnpm` / `cargo` / `pip`)
```bash
# Node / npm
npm install -g chromamatrix-core

# pnpm
pnpm add -g chromamatrix-core

# Rust / Cargo
cargo install chromamatrix-core

# Python / Pip
pip install -r skills/chromamatrix-core/requirements.txt
```

---

## 🚀 Render Orchestrators Matrix

| Render Orchestrator | Primary Function | Execution Command Example |
| :--- | :--- | :--- |
| **`CanvasBootstrapper.py`** | Initialize voxel canvas & contracts | `python3 skills/chromamatrix-core/RenderOrchestrators/CanvasBootstrapper.py --asset-id hero --grid-matrix standard_sprite_32 --palette-lut pico8_fantasy_16 --json` |
| **`ChromaSynthesizer.py`** | Color extraction & LumaLUT remapping | `python3 skills/chromamatrix-core/RenderOrchestrators/ChromaSynthesizer.py --image raw.png --json` |
| **`QualitySentinel.py`** | Quality audit & AA artifact detection | `python3 skills/chromamatrix-core/RenderOrchestrators/QualitySentinel.py --image sprite.png --width 32 --height 32 --max-colors 16 --json` |
| **`RasterRefiner.py`** | Clean AA, orphan purge & export PNG | `python3 skills/chromamatrix-core/RenderOrchestrators/RasterRefiner.py --input raw.png --output clean.png --max-colors 16 --json` |
| **`AtlasSynthesizer.py`** | Texture atlas & JSON metadata packing | `python3 skills/chromamatrix-core/RenderOrchestrators/AtlasSynthesizer.py --frames-dir ./frames/ --output atlas.png --width 32 --height 32 --json` |

---

## 🤖 Multi-Agent Integration

### 1. Claude Code
In Claude Code CLI, trigger the skill using:
```bash
claude "Synthesize a 32x32 isometric terrain tile using chromamatrix-core with Cyberpunk LUT"
```

### 2. OpenAI Codex
In OpenAI Codex environments, include the skill path in prompt context:
```python
# System prompt context points to skills/chromamatrix-core/SKILL.md
```

### 3. Antigravity IDE
In Antigravity IDE, invoke using `@chromamatrix-core` or mention pixel art sprite synthesis in chat.

---

## 📄 License & Standards

Licensed under the [MIT License](LICENSE). Built for high-performance 2D game asset creation.
