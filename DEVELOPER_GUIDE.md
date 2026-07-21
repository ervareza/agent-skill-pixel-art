# PixelMatrix Engine Developer Guide

Developer documentation for extending and building upon the **PixelMatrix Engine** pipeline.

## System Architecture

The engine is built with 5 decoupled core Python modules:

1. **`canvas_initializer.py` (`MatrixCanvasInitializer`)**:
   Sets up workspace structures (`source_rasters/`, `compiled_atlases/`, `lut_palettes/`, `spec_manifests/`) and asset contract manifests.

2. **`lut_synthesizer.py` (`PaletteLUTSynthesizer`)**:
   Performs 3D RGB Euclidean color distance calculations, extracts palettes, and maps rasters to target LUTs.

3. **`spec_inspector.py` (`RasterSpecInspector`)**:
   Verifies image grid bounds, checks color palette counts, detects semi-transparent pixels (anti-aliasing artifacts), and flags orphan pixels.

4. **`atlas_compiler.py` (`SpriteAtlasCompiler`)**:
   Packs sprite frames into grid texture atlases and exports JSON metadata containing frame bounds and UV coordinates.

5. **`raster_processor.py` (`PixelRasterPostProcessor`)**:
   Applies alpha thresholding, orphan pixel cleaning, color quantization, and indexed 8-bit PNG export.

## Running Tests & Verification

Execute all script CLI modules to ensure working state:
```bash
python3 skills/pixelmatrix-engine/scripts/canvas_initializer.py --json
python3 skills/pixelmatrix-engine/scripts/lut_synthesizer.py --json
python3 skills/pixelmatrix-engine/scripts/spec_inspector.py --image index.html --json || true
python3 skills/pixelmatrix-engine/scripts/atlas_compiler.py --help
python3 skills/pixelmatrix-engine/scripts/raster_processor.py --help
```
