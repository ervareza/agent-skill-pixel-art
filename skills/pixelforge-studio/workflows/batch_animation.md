---
description: Batch generate animation frames for existing static sprites
---

# Batch Animation Workflow

Standalone workflow for adding animation frames to existing static pixel art sprites in PixelForge Studio.

## Steps

1. **Identify Assets to Animate**
   - Read `spec_lock.md` for declared animation requirements.
   - List all assets requiring animation sequences.

2. **Define Animation Specifications**
   - Define frame counts, action loops, and direction vectors.

3. **Generate Animation Frames**
   - Generate frames sequentially keeping identical size and palette contracts.

4. **Validate Animation Assets**
   ```bash
   python scripts/asset_inspector.py <project_path>
   ```

5. **Organize and Atlas Pack**
   - Group files as `<asset>_<animation>_<frame>.png`.
   - Run `atlas_packer.py <project_path>`.
