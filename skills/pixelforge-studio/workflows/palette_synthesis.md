---
description: Create and analyze custom pixel art color palettes
---

# Palette Synthesis Workflow

Standalone workflow for synthesizing custom pixel art color palettes in PixelForge Studio.

## Steps

1. **Requirements Analysis**
   - Identify game genre, mood, and color count (8 / 16 / 32 / 64).

2. **Extract or Synthesize Colors**
   - Extract from reference artwork:
     ```bash
     python scripts/chroma_analyzer.py extract <image_path> --count <N>
     ```

3. **Validate Palette Adherence**
   - Validate workspace assets:
     ```bash
     python scripts/chroma_analyzer.py validate <project_path>
     ```

4. **Register Palette Contract**
   - Save palette to `templates/palettes/palettes_index.json` and `spec_lock.md`.
