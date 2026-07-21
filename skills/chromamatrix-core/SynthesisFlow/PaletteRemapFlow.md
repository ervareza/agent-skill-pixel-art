# Palette Remapping & Quantization Synthesis Flow Guide

This flow guides AI Agents through color extraction, LumaLUT distance matching, anti-aliasing cleaning, and 8-bit indexed PNG quantization.

## Step-by-Step Color Remap Procedure

1. **Extract Source Colors & Match LumaLUT**:
   Analyze source image colors against target palette (e.g. NES 54, PICO-8 16, Cyberpunk 16):
   ```bash
   python3 skills/chromamatrix-core/RenderOrchestrators/ChromaSynthesizer.py \
     --image source_rasters/raw_concept.png --json
   ```

2. **Clean Anti-Aliasing & Post-Process**:
   Clean semi-transparent pixel fringes, purge isolated orphans, and quantize color palette:
   ```bash
   python3 skills/chromamatrix-core/RenderOrchestrators/RasterRefiner.py \
     --input source_rasters/raw_concept.png \
     --output exports/indexed_png/clean_concept.png \
     --max-colors 16 --json
   ```

3. **Verify Compliance**:
   Run `QualitySentinel.py` to confirm zero anti-aliasing and strict palette bounds adherence.
