# Palette LUT Remapping & Quantization Workflow Guide

This workflow guides AI Agents through color extraction, LUT distance matching, anti-aliasing cleaning, and 8-bit indexed PNG quantization.

## Step-by-Step Color Remap Procedure

1. **Extract Source Colors & Match LUT**:
   Analyze source image colors against target palette (e.g. NES 54, PICO-8 16, Cyberpunk 16):
   ```bash
   python3 skills/pixelmatrix-engine/scripts/lut_synthesizer.py --image source_rasters/raw_concept.png --json
   ```

2. **Clean Anti-Aliasing & Post-Process**:
   Clean semi-transparent pixel fringes, purge isolated orphans, and quantize color palette:
   ```bash
   python3 skills/pixelmatrix-engine/scripts/raster_processor.py \
     --input source_rasters/raw_concept.png \
     --output exports/indexed_png/clean_concept.png \
     --max-colors 16 --json
   ```

3. **Verify Compliance**:
   Run `spec_inspector.py` to confirm zero anti-aliasing and strict palette bounds adherence.
