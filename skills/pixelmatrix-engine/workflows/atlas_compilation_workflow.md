# Atlas Compilation Workflow Guide

This workflow details how AI Agents compile raw sprite frames into production-ready texture atlases.

## Step-by-Step Atlas Compilation Procedure

1. **Verify Source Frame Resolution**:
   Ensure all input frames match the specified dimensions (e.g. 32x32).
   ```bash
   python3 skills/pixelmatrix-engine/scripts/spec_inspector.py --image source_rasters/frame_01.png --width 32 --height 32
   ```

2. **Execute Atlas Compiler**:
   Combine all frames into a packed atlas and output JSON metadata:
   ```bash
   python3 skills/pixelmatrix-engine/scripts/atlas_compiler.py \
     --frames-dir source_rasters/character_walk/ \
     --output compiled_atlases/character_walk_atlas.png \
     --width 32 --height 32 --json
   ```

3. **Validate JSON Manifest**:
   Check `compiled_atlases/character_walk_atlas.json` to verify frame coordinates and UV mapping parameters.
