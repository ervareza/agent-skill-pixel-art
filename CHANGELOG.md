# Changelog

All notable changes to **PixelForge Studio** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.0.0] - 2026-07-22

### Added
- Initial release of **PixelForge Studio** engine.
- `ForgeWorkspaceManager` (`forge_workspace.py`): Command-line workspace initialization, source asset importing, and contract validation.
- `ChromaPaletteAnalyzer` (`chroma_analyzer.py`): Color palette extraction from reference assets, Euclidean distance calculations, and contract adherence verification.
- `PixelAssetInspector` (`asset_inspector.py`): Quality inspection engine for verifying canvas dimensions, palette limits, and detecting anti-aliasing artifacts.
- `SpriteAtlasPacker` (`atlas_packer.py`): Automated sprite sheet assembly with structured JSON metadata manifests.
- `AssetPostProcessor` (`post_processor.py`): Color quantization, isolated orphan pixel cleaning, and indexed 8-bit PNG conversion.
- `pixelforge-studio` AI Skill integration package (`skills/pixelforge-studio`).
- Comprehensive web showcase dashboard (`index.html`) featuring interactive tab navigation, CLI generator, workflow preview, and `/changelog` route view.

### Changed
- Rebranded and refactored the legacy architecture into modern, type-annotated, object-oriented Python modules.
- Re-architected tile generation standards to enforce 4-edge wrapping, Voronoi noise distribution, and seamless texture rules.
