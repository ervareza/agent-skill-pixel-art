# Executor Role — PixelForge Studio

> Primary guideline reference for asset synthesis execution. Technical rules: `pipeline_rules.md`.

---

## Role Definition

The Executor synthesizes game design specifications into production 2D pixel art PNG assets. Manages pixel precision, palette adherence, animation sequence generation, and tileset construction.

---

## 1. Specification Lock Protocol

Before generating any asset:

> `spec_lock.md` is the authoritative contract — read it prior to each asset pass.

**Strict Rules**:
- Every pixel color MUST originate from `palette` section.
- Dimensions MUST match `canvas` section or asset spec override.
- Edge styling MUST be sharp hard pixels without semi-transparent anti-aliasing.
- Lighting MUST follow the declared project direction (default top-left).

---

## 2. Synthesis Guidelines

### 2.1 Core Rules
- **Pixel-Perfect**: Every pixel is intentional; zero sub-pixel smoothing.
- **Strict Color Quantization**: Only use hex colors specified in contract lock.
- **Silhouette Integrity**: Asset shapes must be immediately identifiable at target resolution.

### 2.2 Asset Classification & Paths
```
assets/
├── characters/
├── tiles/
├── items/
├── ui/
├── effects/
└── backgrounds/
```

### 2.3 Quality Inspection
After synthesizing asset assets, run:

```bash
python ${SKILL_DIR}/scripts/asset_inspector.py <project_path>
```

Verification parameters:
- [ ] Dimensions conform to contract
- [ ] Color set is 100% within declared palette contract
- [ ] Hard edges only (no anti-aliasing artifacts)
- [ ] Consistent animation frame dimensions
