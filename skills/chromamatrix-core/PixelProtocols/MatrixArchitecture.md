# ChromaMatrix Core — Matrix Architecture & Micro-Module System Design

Overview of ChromaMatrix Core architecture, micro-module decoupling, and multi-agent coordination specs.

---

## System Design Architecture

ChromaMatrix Core separates asset creation into discrete, mathematically deterministic stages:

```
[Agent System Prompt / Intent]
         │
         ▼
 ┌─────────────────────────┐
 │ ManifestVault           │ <── GridMatrices.json, LumaPalettes.json, SpriteCore.json
 └───────────┬─────────────┘
             │
             ▼
 ┌─────────────────────────┐
 │ CanvasBootstrapper      │ <── Voxel Canvas & Contract Initialization
 └───────────┬─────────────┘
             │
             ▼
 ┌─────────────────────────┐
 │ ChromaSynthesizer       │ <── Color Palette Remapping & Distance Metrics
 └───────────┬─────────────┘
             │
             ▼
 ┌─────────────────────────┐
 │ QualitySentinel         │ <── Quality Audit & Artifact Detection
 └───────────┬─────────────┘
             │
             ▼
 ┌─────────────────────────┐
 │ RasterRefiner           │ <── Anti-aliasing Clean, Orphan Purge, Indexed PNG Export
 └───────────┬─────────────┘
             │
             ▼
 ┌─────────────────────────┐
 │ AtlasSynthesizer        │ <── Texture Atlas & JSON Manifest Generation
 └─────────────────────────┘
```

---

## Multi-Agent Compatibility Matrix

| Platform | Trigger Pattern | Entry Point | Context Management |
| :--- | :--- | :--- | :--- |
| **Claude Code** | `/chromamatrix`, `pixel art` | `skills/chromamatrix-core/SKILL.md` | Discovers ManifestVault JSONs, executes RenderOrchestrators CLI |
| **OpenAI Codex** | `generate pixel art sprite` | `skills/chromamatrix-core/SKILL.md` | Parses specifications, runs QualitySentinel before emitting code |
| **Antigravity IDE** | `@chromamatrix`, skill injection | `skills/chromamatrix-core/SKILL.md` | Full context binding, auto-runs verification orchestrators |
