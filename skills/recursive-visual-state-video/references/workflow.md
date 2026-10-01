# Generation, Drift Diagnosis, and Repair Workflow

This workflow is grounded in a small observed run: eleven recursively edited frames (`frame_000`–`frame_010`) and one reference-anchored restoration of `frame_010`. It is an operational recipe, not evidence that a model will behave identically in other scenes or interfaces.

## 0. Turn a plain-language request into a run plan

Extract the scene, subject, action, duration, requested fps/frame count, aspect ratio, output location, reference frame, and whether audio is requested. Do not ask the user to calculate frame counts or name intermediate files.

- If duration is given, use it. If omitted, default to 3 seconds and record that default.
- If fps is given, use it. Otherwise default to 10 fps and record it.
- If aspect ratio is absent, default to 16:9. Use the image model's documented size controls when available; do not invent a resolution parameter.
- If duration is given in seconds and fps is known, set `frame_count = max(1, round(duration_seconds × fps))`. Create exactly `frame_count` files named `frame_000.png` through `frame_{frame_count-1:03}.png`. The encoded duration is `frame_count / fps`; record this effective duration because rounding can differ from the requested value by at most half a frame.
- If only an exact frame count is given, use it and the requested/default fps; derive effective duration as `frame_count / fps`.
- If the user specifies both duration and frame count, calculate the implied fps. Use the explicit fps if present; otherwise set `fps = frame_count / duration`. State the chosen interpretation in `state.json`.
- Default output is a new timestamped run directory under the current workspace, containing `frames/`, `frames_restored/` (only if used), `state.json`, `drift_report.json`, `contact_sheet.png`, and, when encoding succeeds, a silent `output.mp4`. Never reuse or overwrite a prior run silently.
- Audio is out of scope unless the user requested it and a supported audio-generation path is available. Do not imply a silent frame sequence contains audio.

For stability, review at approximately two-second intervals: `checkpoint_frames = max(1, round(2 × fps))`. At each checkpoint, inspect the most recent transition, compare the checkpoint frame to the immediate predecessor and long-term reference, record diagnosed issues, and adapt later per-frame prompts. This is a diagnostic cadence only: continue the same recursive chain across checkpoints, never restart from `frame_000` or generate each window independently. Validate local file integrity after every frame even between checkpoints. If two seconds was chosen as a default, record it. Do not ask the user to approve ordinary checkpoints; pause only on a blocking tool/file failure, a severe uncorrectable drift, or a requested pause boundary.

Create state before the first generation and update it after each verified frame. This lets Codex resume from the last verified frame if execution is interrupted without regenerating completed frames.

## 1. Capability gate and file contract

Before generation, inspect the image-generation/editing tools actually available in this Codex session. Confirm all of the following:

1. The tool can accept a local previous-frame image as visual input. For restoration, determine whether it can accept the current frame plus a separate appearance reference (and optionally the previous frame).
2. Its output exposes decodable image bytes/data or an actual local artifact path accessible to the workspace.
3. A returned image can be written as a real PNG and reopened by a local decoder.

Use the tool's documented interface. Do not assume that an OpenAI Images API, SDK, parameter name, key, or output path exists. If an official API is available and configured, verify its current documentation before using it. Never print, search for, or copy credentials. If no supported path satisfies the image-input and output-file requirements, explain exactly which capability is missing and stop; do not generate independent frames as a substitute.

In the observed Codex desktop session, `image_gen.imagegen` accepted `referenced_image_paths`. Its result exposed an `image_url` data URL and an `output_hint` naming a PNG saved in a generated-images directory. Copying that actual PNG into the workspace, then reopening it with Pillow, worked. These were observed details of that session, not a promise about other installations.

## 2. Recursive generation

For every transition `t → t+1`:

1. Read `frames/frame_t.png` from disk. Confirm it exists, decodes, and has the expected dimensions. Do not rely on a remembered or previously displayed version.
2. Pass that exact file as the primary/authoritative visual input. State that it defines current identity, pose, clothing, composition, objects, lighting, and geometry.
3. Describe only the intended next small physical delta, including direction and constraints. If the target is shoulder height, explicitly bound the hand at/under shoulder height. Do not ask the image model to recreate the whole scene from text.
4. Generate one next frame, not a batch of independent images. Save it as `frames/frame_{t+1:03}.png`.
5. Confirm the file exists and reopen/verify it locally before the next transition. A displayed image or successful model response alone is insufficient.
6. Compare the new frame with the immediate predecessor and the long-term reference. If there is a concerning jump, pause the sequence, document it, and repair or ask the user before compounding the error.

Keep original frames immutable. Keep generation prompts or concise per-step notes where practical so the run can be understood later. Update state only after the file is saved and verified.

## 3. Drift diagnosis: compare before labeling

For each frame under review, inspect a three-way sequence: current frame, immediate predecessor, and long-term reference `R` (default `frame_000.png`). A contact sheet helps reveal trends but does not replace inspection at useful resolution.

Classify observations along independent axes; one frame may have more than one issue:

| Class | Diagnostic question | Example |
|---|---|---|
| Legitimate temporal change | Is the difference required by the user's motion/state instruction? | The intended right arm rises between adjacent frames. |
| Accumulated visual drift | Has an unrequested visual property moved progressively away from the sequence's stable appearance? | Furniture proportions or face appearance change over several transitions. |
| Image degradation | Has fidelity worsened without an intended scene change? | Speckle/noise, blur, texture artifacts, or lost fine detail. |
| Appearance drift | Did color or tonal rendering shift? | Warm/red cast, white-balance, saturation, contrast, or exposure change. |
| Geometry/identity drift | Did identity, anatomy, clothing, object layout, scale, or spatial relation change unexpectedly? | Face, body proportions, room layout, or camera framing changes. |
| Motion overshoot | Did the subject move farther than the allowed per-frame or target state? | Hand passes the requested shoulder-height endpoint and rises above the head. |

Do not call motion drift just because the current pose differs from `R`. Ask whether it follows the requested motion and whether the change from the predecessor is within the declared delta. A hand progressively moving upward can be valid motion; a hand jumping from waist level to overhead in one step can be overshoot even though its direction is correct.

Record evidence and confidence. A model's visual comparison is qualitative unless a separately specified measurement is performed. Do not infer red speckle, identity drift, or a successful fix solely from a prompt or tool response. In the observed pilot, the contact sheet showed increasing softness/warmth and later framing/pose drift; the overhead hand in the last frame visibly exceeded the earlier shoulder-height target. Red speckle was part of the restoration target reported for the experiment, but the included small contact-sheet view is not a quantitative speckle measurement.

## 4. Reference-anchored restoration

Keep three roles distinct:

- **Current frame**: authoritative scene contents, current pose, and motion state to preserve.
- **Immediate previous frame**: temporal continuity and local transition context.
- **Reference frame `R`**: long-term appearance/quality anchor (normally `frame_000.png`, or a user-selected frame).

Conceptually use `I_(t+1) = F(I_t, R, Δs_t)` for generation and `I'_t = Restore(I_t, I_(t-1), R | preserve state_t)` for repair. These expressions describe roles, not a provided API.

For restoration, explicitly label the inputs in the prompt if the tool accepts multiple images. Say that the current frame controls exact pose, hand/wrist/elbow location, identity, scene geometry, and time position; the previous frame is for continuity; the reference is only for stable appearance, color, and quality. Do not transfer the reference pose, framing, or objects. If multiple image roles cannot be represented safely in that interface, do not proceed with a restoration that risks resetting motion.

Preserve a copy of originals under `frames/`; write outputs under `frames_restored/` with matching names. Never overwrite source frames. Do not automatically “fix” geometry, identity, or overshoot by inventing a pose. Those corrections can change the intended state and should be treated as a separate, explicit editorial decision.

## 5. Minimum-correction ladder

Start with the least invasive correction supported by the tool and the observed issue. The following order is a preference for isolating changes, not a claim that every model exposes these as separate controls:

1. Color temperature / white balance.
2. Noise and speckle.
3. Blur and fine-detail degradation.
4. Contrast, exposure, and saturation.
5. Broader appearance stabilization.
6. Geometry correction.
7. Identity correction.

If a combined image-edit model cannot isolate corrections, request only the identified quality changes and strongly constrain content/pose. Escalate reconstruction strength only when lighter correction is inadequate and the user authorizes the semantic change. If the edit changes valid motion, treat it as a failed restoration: keep the source, record the failure, and retry with a narrower correction or stop for user review.

## 6. Restoration validation

After every repair, reopen the PNG and compare `restored` against `current original`, `previous`, and `R`. Check:

- identity, face, hair, clothing, body proportions;
- background, object count/placement, camera geometry, lighting/shadows;
- color temperature, white balance, exposure, contrast, saturation;
- sharpness, speckle/noise, fine detail, and new texture/artifact formation;
- exact pose and motion state, especially hand, wrist, elbow, and limb location.

The restoration fails if it erases or changes valid motion, changes identity/scene geometry without authorization, is unreadable, or introduces a material new artifact. Report unresolved issues as unresolved. Keep both original and restored files available for rollback and comparison.

## 7. State, validation, and deliverables

Use the schemas in [state-and-report-schema.md](state-and-report-schema.md). State should distinguish intended motion from observed motion and only advance the current frame after a successful local file check. A drift report should identify the frame, evidence, categories, confidence, repair, and post-repair result.

Validate every required filename and PNG, dimension consistency, frame ordering, and report references. Use:

```powershell
python scripts/validate_frames.py --frames-dir frames --start 0 --end 10
python scripts/create_contact_sheet.py --frames-dir frames --start 0 --end 10 --output frames/contact_sheet.png
```

For restored outputs, validate their directory separately. If Pillow is unavailable, explain the dependency and use another installed local decoder rather than silently skipping the check. A contact sheet must label frame numbers and preserve order. When possible, create a side-by-side original/restored comparison sheet.

If the user asked for a playable video, check whether `ffmpeg` is installed and run the bundled encoder only after all requested frame files have passed validation:

```powershell
python scripts/encode_video.py --frames-dir frames --start 0 --count 30 --fps 10 --output output.mp4
```

The encoder refuses to overwrite an existing output, validates the numbered PNG inputs, and writes a silent H.264 MP4. It does not install ffmpeg or add audio. If it is unavailable, keep the frame sequence/contact sheet complete and say that MP4 encoding was blocked by the missing local encoder. Do not substitute an unverified or unrelated video API.

Final reporting separates: files verified; generation/restoration method actually used; observed identity/appearance/geometry/motion findings; detected or unresolved drift; frames that failed; and qualitative versus measured claims.
