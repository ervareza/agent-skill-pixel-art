# Layering, Rigging & Paper-Doll Architecture

Never bake an animated character into a single flat layer. Split body parts and equipment into ordered layers **before** animating so limbs move losslessly, equipment swaps cleanly, and the `.aseprite` source stays editable in Aseprite, LibreSprite, Godot, and Unity.

## Standard Bottom-to-Top Character Rig

PixelForge's `RIG_LAYERS` convention (synthesized from `with-pebbly/aseprite-ai-artist`, `Universal-LPC`, and `PixelDoll`):

| Z | Layer Name | Purpose |
|---|---|---|
| 0 | `shadow` | Ground contact shadow pinned to `ground_y` (shrinks slightly when airborne) |
| 1 | `cape_back` | Cape / cloak trailing behind torso (animated with 1-frame follow-through lag) |
| 2 | `hair_back` | Long hair behind shoulders & neck |
| 3 | `arm_far` | Far-side arm, shaded 1 ramp step darker for instant depth separation |
| 4 | `leg_far` | Far-side leg + boot, shaded 1 ramp step darker so legs never fuse during stride |
| 5 | `torso` | Tunic, chestplate, collar, belt, buckle, robe skirt |
| 6 | `leg_near` | Near-side leg + boot (brighter ramp, clear knee bend on pass pose) |
| 7 | `head` | Cranium + directional face (2 eyes S, shifted 2 eyes SE/SW, 1 eye E/W, **0 eyes N/NE/NW**) |
| 8 | `hair_front` | Crown hair, sideburns, asymmetric bangs/fringe |
| 9 | `headgear` | Swappable helmet, wizard hat, hood, crown, headband |
| 10 | `arm_near` | Near-side sleeve + contrasting hand swinging opposite `leg_near` |
| 11 | `weapon` | Swappable sword, staff, bow, dagger, axe anchored to hand socket |
| 12 | `shield` | Kite or round shield anchored to off-hand |
| 13 | `vfx` | Melee slash arc smears, spell glow rings (only non-empty on active frames) |
| 14 | `outline` | Unified 1px selective hue-shifted outline (`selout`) computed around all body/gear layers |

## Key Rigging Rules

1. **Unified Outline on Top:** Never outline each limb independently on small sprites — it creates ugly internal black seams where arms meet torso. Composite the body layers and run `selout` once on the `outline` layer.
2. **Far Limbs Darker:** Always tint `arm_far` and `leg_far` one ramp step cooler/darker than `arm_near` and `leg_near`. In profile walk cycles, this is what prevents two crossing legs from turning into a solid blob.
3. **Generous Joint Overlap:** Overlap shoulder/hip joints by 1–2 pixels under the torso so no transparent gap opens when limbs swing.
4. **Paper-Doll Export (`--export-layers`):** Exporting each layer as its own frame-aligned sprite sheet lets game engines swap hair, armor, capes, and weapons at runtime using identical frame coordinates.
5. **Blend Modes & Opacity:** `SpriteDocument.layer()` supports `normal`, `multiply`, `screen`, `add`, and `overlay` blend modes plus `0–255` layer opacity — all preserved verbatim in native `.aseprite` exports!
6. **Linked Cels:** Use `doc.link_cel(layer="bg", from_frame=1, to_frames="rest")` for static layers so editing frame 1 updates every frame.
