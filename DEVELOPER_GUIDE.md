# PixelForge Studio Developer Guide

Technical design doc and module internals reference for maintainers and engine developers.

---

## Code Base Layout

```
.
├── CHANGELOG.md                   # Semantic version history
├── CONTRIBUTING.md                # Contribution guidelines
├── DEVELOPER_GUIDE.md             # Developer & architectural manual
├── LICENSE                        # MIT License
├── README.md                      # Primary project overview
├── SECURITY.md                    # Security standards & policy
├── .env.example                   # Environment variable template
├── index.html                     # Web showcase & interactive dashboard
└── skills/
    └── pixelforge-studio/         # Skill & core engine codebase
        ├── SKILL.md               # AI Agent skill entry point
        ├── requirements.txt       # Dependencies
        ├── scripts/
        │   ├── atlas_packer.py    # SpriteAtlasPacker class
        │   ├── asset_inspector.py # PixelAssetInspector class
        │   ├── chroma_analyzer.py # ChromaPaletteAnalyzer class
        │   ├── forge_workspace.py # ForgeWorkspaceManager class
        │   └── post_processor.py  # AssetPostProcessor class
        ├── references/            # Pipeline reference guidelines
        ├── templates/             # JSON indices & markdown templates
        └── workflows/             # Standalone synthesis guides
```

---

## Module Architectural Design

### 1. `ForgeWorkspaceManager` (`forge_workspace.py`)
Responsible for setup, structure creation, source importing, and contract validation (`spec_lock.md`).

### 2. `ChromaPaletteAnalyzer` (`chroma_analyzer.py`)
Performs RGB frequency quantization, color clustering, Euclidean color space distance computation ($\Delta E_{RGB}$), and contract adherence checks.

### 3. `PixelAssetInspector` (`asset_inspector.py`)
Inspects PNG files for canvas dimension multiples, per-sprite color budgets, and semi-transparent alpha channel pixels (anti-aliasing defects).

### 4. `SpriteAtlasPacker` (`atlas_packer.py`)
Packs frame image sequences into 2D grid sheets and outputs structured JSON metadata manifests (`manifest.json`).

### 5. `AssetPostProcessor` (`post_processor.py`)
Executes 3 post-processing algorithms:
- Nearest-neighbor color quantization to declared palette.
- 4-neighborhood isolated orphan pixel removal.
- RGBA to 8-bit indexed PNG color table conversion.
