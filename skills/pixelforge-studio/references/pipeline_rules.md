# PixelForge Studio Technical Pipeline Rules

Comprehensive technical standards and quality rules for PixelForge Studio asset generation.

---

## 1. Pixel Art Standards & Blacklist

The following features are **strictly forbidden** in generated assets:

| Banned Feature | Reason |
|----------------|--------|
| Anti-aliasing | Destroys sharp pixel clarity |
| Sub-pixel rendering | Invalid at pixel grid resolution |
| Gradient fills | Use dithering patterns instead |
| Semi-transparency (1-254 alpha) | Assets must use full opacity or full transparency |
| Anti-aliased text | Text rendered in pixel art must be crisp pixel-aligned font |

---

## 2. File & Atlas Standards

- Format: PNG-32 (RGBA) or PNG-8 (Indexed Color).
- Grid Alignment: All frames must align to base canvas boundaries (`32x32`, `64x64`, etc.).
- Manifest: Packed atlases generate a structured `manifest.json` using `atlas_packer.py`.
