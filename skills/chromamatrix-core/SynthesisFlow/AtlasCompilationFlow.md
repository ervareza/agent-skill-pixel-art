# Atlas Compilation Synthesis Flow Guide

This flow details how AI Agents compile raw sprite frames into production-ready texture atlases.

## Step-by-Step Atlas Compilation Procedure

1. **Verify Source Frame Dimensions**:
   Ensure input frames match expected dimensions (e.g. 32x32):
   ```bash
   python3 skills/chromamatrix-core/RenderOrchestrators/QualitySentinel.py \
     --image source_rasters/frame_01.png --width 32 --height 32
   ```

2. **Execute Atlas Synthesizer**:
   Combine frames into a packed atlas and output JSON metadata manifest:
   ```bash
   python3 skills/chromamatrix-core/RenderOrchestrators/AtlasSynthesizer.py \
     --frames-dir source_rasters/character_walk/ \
     --output compiled_atlases/character_walk_atlas.png \
     --width 32 --height 32 --json
   ```

3. **Validate JSON Manifest**:
   Inspect `compiled_atlases/character_walk_atlas.json` to verify frame bounds and UV metrics.
