# Observed pilot: recursive transitions and one-frame restoration

This example records an actual local experiment retained in the source workspace when the skill was authored. It is intentionally limited to what was generated and visually inspected; it is not a benchmark or a general performance claim.

- Eleven 1672×941 PNGs were present as `frames/frame_000.png` through `frame_010.png`, and all passed local Pillow decoding checks.
- The transitions were performed sequentially with the immediately previous PNG passed as the image-edit reference.
- An ordered contact sheet showed a consistent recognizable subject and living-room scene overall, with accumulated softness/warmth and some later composition/pose drift. The right hand rose above the head by the last frames, exceeding the original shoulder-height target.
- A restoration was run only for `frame_010.png`, using the current frame as the pose/content authority and `frame_000.png` only as a quality/appearance reference. It was saved separately as `frames_restored/frame_010.png` and passed PNG decoding.
- In a direct side-by-side inspection of reference, original final frame, and restored final frame, the restored hand remained overhead rather than returning to the reference pose. The restored result looked sharper and more neutral than the original final frame. This was a qualitative visual judgment; no pixel-level denoising, color, or pose metric was run.
- Red speckle was included in the requested repair target, but this artifact set does not claim a measured reduction in red speckle.

Artifacts here are compact contact sheets from that run, not the source frames. The original local frames remain outside the checked-in example so the example does not silently replace a user's data.
