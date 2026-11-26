# Fake-3D Sprite Stacking Guide

Sprite stacking renders a 3D voxel-like pixel art object from a **horizontal strip of flat top-down 2D slices** (ground slice `z=0` on the left, roof slice `z=N-1` on the right). At render time, draw slices bottom to top, each rotated by angle `θ`, squashed vertically by camera pitch `squash`, and lifted `-round(z * spacing)` pixels.

## Core Rendering Formula

```js
for (let z = 0; z < sliceCount; z++) {
  // 1. Sample slice z around symmetric center ((w - 1) * 0.5, (h - 1) * 0.5)
  // 2. Inverse-rotate by heading angle `turn` with Math.round() nearest sampling
  // 3. Apply camera pitch vertical `squash` (default 0.75)
  // 4. Lift vertically by -Math.round(z * spacing) (default spacing = 1.0)
}
// 5. Trace a single 1px outline around the finished 1x buffer (NEVER per slice!)
```

## Critical Rules (Learned from `danielwh2/sprite-stacking`)

1. **Symmetric Rotation Centers:** Always rotate around `(w - 1) * 0.5, (h - 1) * 0.5` with `round()`. Using `floor(w / 2)` on even widths introduces a 0.5px wobble every 90°.
2. **Outline Once at the End:** Outlining individual slices paints dark horizontal stripes and speckle through the body. Render the entire stack into an unscaled 1× buffer, apply a single outer 1px outline, then upscale by an integer factor.
3. **Ground Shadow:** Project the union footprint of slice `z=0` offset by `(+2, +2)` before drawing slice `0`.
4. **Thickness Minimum (≥ 2px):** 1px-thin antennas, poles, or thin walls blink in and out during rotation. Make thin structural parts at least 2px wide.
5. **Validate Strip Width:** Assert `strip.width % slice_count == 0` on load so slice boundaries never drift mid-frame.
6. **CLI Usage:**
   ```bash
   python scripts/sprite_stack.py --preset car --slices 12 --frames 16 --fps 12 --output-dir ./out/car --gif --json
   ```
   Open `templates/turntable_viewer.html` to inspect any slice strip interactively in 360° with live pitch, slice spacing, exploded view, and slice scanner!
