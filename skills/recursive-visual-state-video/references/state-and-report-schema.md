# State and Drift Report Schema

These JSON examples are templates. Use relative paths within a run directory and update state only after local output verification.

## `state.json`

```json
{
  "schema_version": 1,
  "run_id": "example-run",
  "reference_frame": "frames/frame_000.png",
  "frames_dir": "frames",
  "restored_dir": "frames_restored",
  "first_frame": 0,
  "target_last_frame": 29,
  "frame_count": 30,
  "requested_duration_seconds": 3.0,
  "effective_duration_seconds": 3.0,
  "fps": 10,
  "checkpoint_interval_frames": 20,
  "current_frame": 0,
  "motion": {
    "description": "Raise the subject's right hand slowly to shoulder height.",
    "state_at_current_frame": "arm relaxed at side",
    "per_frame_limit": "small visible increment; do not pass shoulder height",
    "coordinate_or_pose_notes": "Use the subject's anatomical right, not screen left/right."
  },
  "image_tool": {
    "name": "record actual tool name",
    "local_image_input_verified": true,
    "output_file_path_or_decode_verified": true
  },
  "verified_frames": ["frames/frame_000.png"],
  "video_output": null,
  "updated_at": "YYYY-MM-DD"
}
```

Use `current_frame` for the latest frame that exists and passed local decoding, not the requested target. Set capability fields from actual checks; never assume `true`. Record fps, model/tool version, prompt references, seed, or settings only when they are actually known and useful. Avoid secrets.

## `drift_report.json`

```json
{
  "schema_version": 1,
  "reference_frame": "frames/frame_000.png",
  "assessment_type": "qualitative_visual_review",
  "frames": [
    {
      "frame": 10,
      "compared_with": {
        "previous": "frames/frame_009.png",
        "reference": "frames/frame_000.png"
      },
      "legitimate_temporal_change": ["right arm remains raised"],
      "detected_drift": ["warm_color_shift", "softness", "composition_drift"],
      "image_degradation": ["fine_detail_loss"],
      "geometry_identity_drift": [],
      "motion_overshoot": {
        "detected": true,
        "evidence": "hand is above head although target is shoulder height"
      },
      "confidence": "medium",
      "evidence_method": "visual side-by-side inspection",
      "repair": {
        "applied": false,
        "output": null,
        "operations": [],
        "motion_state_preserved": null
      },
      "validation": "not_repaired"
    }
  ]
}
```

Suggested issue terms include `red_speckle`, `noise`, `blur`, `softness`, `fine_detail_loss`, `warm_color_shift`, `white_balance_drift`, `contrast_drift`, `exposure_drift`, `texture_artifact`, `appearance_drift`, `composition_drift`, `identity_drift`, `geometry_drift`, and `motion_overshoot`. Use only categories supported by inspection; preserve free-text evidence. `validation` may be `passed`, `failed_motion_changed`, `failed_identity_or_geometry_changed`, `failed_artifact`, `unreadable`, `not_repaired`, or another clear value.

## Status semantics

- `intended_motion` describes what should happen.
- `observed_motion` describes what the pixels show.
- `detected_drift` excludes changes that are valid parts of the intended state transition.
- `repair_applied` records operations actually requested/applied, not just desired operations.
- `motion_state_preserved` is `true` only after comparing the output pose with the pre-repair current frame. If not checked, use `null` and say so.
- Keep diagnosis confidence separate from image-file integrity. A valid PNG does not prove a visually successful repair.
