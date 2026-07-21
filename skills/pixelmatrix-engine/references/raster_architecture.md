# PixelMatrix Engine — Raster Architecture & Multi-Agent Matrix

Overview of the PixelMatrix Engine architecture, component decoupling, and multi-agent coordination specs.

---

## Architecture Overview

PixelMatrix Engine separates asset creation into discrete, mathematically deterministic stages:

```
[Agent System Prompt / Intent]
         │
         ▼
 ┌─────────────────────────┐
 │ Specification Indexes   │ <── grid_canvas_presets.json, palette_lut_definitions.json, sprite_matrix_specs.json
 └───────────┬─────────────┘
             │
             ▼
 ┌─────────────────────────┐
 │ MatrixCanvasInitializer │ <── Workspace & Contract Initialization
 └───────────┬─────────────┘
             │
             ▼
 ┌─────────────────────────┐
 │ PaletteLUTSynthesizer   │ <── Color Palette Remapping & Distance Metrics
 └───────────┬─────────────┘
             │
             ▼
 ┌─────────────────────────┐
 │ RasterSpecInspector     │ <── Verification & Artifact Detection
 └───────────┬─────────────┘
             │
             ▼
 ┌─────────────────────────┐
 │ PixelRasterPostProcessor│ <── Anti-aliasing Clean, Orphan Clean, Indexed PNG Export
 └───────────┬─────────────┘
             │
             ▼
 ┌─────────────────────────┐
 │ SpriteAtlasCompiler     │ <── Texture Atlas & JSON Manifest Generation
 └─────────────────────────┘
```

---

## Multi-Agent Capability Matrix

| Platform | Trigger Pattern | Entry Point | Context Management |
| :--- | :--- | :--- | :--- |
| **Claude Code** | `/pixelmatrix`, `pixel art` | `skills/pixelmatrix-engine/SKILL.md` | Auto-discovers specs JSON, executes script pipeline via subshell |
| **OpenAI Codex** | `generate pixel art sprite` | `skills/pixelmatrix-engine/SKILL.md` | Parses specifications, runs CLI inspection before emitting code |
| **Antigravity IDE** | `@pixelmatrix`, skill injection | `skills/pixelmatrix-engine/SKILL.md` | Full system prompt context, auto-runs verification scripts |
