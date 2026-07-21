# ChromaMatrix Core Developer Guide

Developer documentation for extending and building upon the **ChromaMatrix Core** engine.

## System Architecture

The engine is built with 5 decoupled core Python micro-modules under `RenderOrchestrators/`:

1. **`CanvasBootstrapper.py` (`CanvasBootstrapper`)**:
   Sets up voxel canvas structures (`source_rasters/`, `compiled_atlases/`, `luma_palettes/`, `contract_manifests/`) and asset contract manifests.

2. **`ChromaSynthesizer.py` (`ChromaSynthesizer`)**:
   Performs 3D RGB Euclidean color distance calculations, extracts palettes, and maps rasters to target LumaLUTs.

3. **`QualitySentinel.py` (`QualitySentinel`)**:
   Audits image grid bounds, checks color counts, detects semi-transparent pixels (anti-aliasing artifacts), and flags orphan pixels.

4. **`AtlasSynthesizer.py` (`AtlasSynthesizer`)**:
   Packs sprite frames into grid texture atlases and exports JSON metadata containing frame bounds and UV metrics.

5. **`RasterRefiner.py` (`RasterRefiner`)**:
   Applies alpha thresholding, orphan pixel purging, color quantization, and indexed 8-bit PNG export.

## Running Tests & Verification

Execute all CLI micro-modules to ensure working state:
```bash
python3 skills/chromamatrix-core/RenderOrchestrators/CanvasBootstrapper.py --json
python3 skills/chromamatrix-core/RenderOrchestrators/ChromaSynthesizer.py --json
python3 skills/chromamatrix-core/RenderOrchestrators/QualitySentinel.py --image index.html --json || true
python3 skills/chromamatrix-core/RenderOrchestrators/AtlasSynthesizer.py --help
python3 skills/chromamatrix-core/RenderOrchestrators/RasterRefiner.py --help
```
