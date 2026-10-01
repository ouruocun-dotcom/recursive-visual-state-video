---
name: recursive-visual-state-video
description: Plan and produce videos as numbered still-image sequences, recursively conditioning each frame on the previous frame; track and repair visual drift while preserving valid motion. Use when a user describes a video for Codex to build from images.
---

# Recursive Visual State Video

Use this skill when a user wants a sequence built by repeated image-to-image state transitions and needs scene consistency, drift diagnosis, or reference-anchored restoration.

Read [references/workflow.md](references/workflow.md) for the generation, diagnosis, and repair procedure. Read [references/state-and-report-schema.md](references/state-and-report-schema.md) when creating or updating run state and drift reports.

## Non-negotiable invariants

- The immediately previous frame defines the current visual state. Read it from disk before every transition and pass that file as the primary image input. Never silently substitute independent text-to-image generation.
- Track intended motion as a small per-step state change. Preserve identity, scene geometry, and all unrequested details. Stop and report if the available image interface cannot take the required local image input or save a decodable result.
- A long-term reference (normally `frame_000.png`) is an appearance anchor, not a pose template. The current frame defines the pose to preserve; the previous frame supports temporal continuity; the reference guides stable appearance and image quality.
- Diagnose legitimate temporal change separately from accumulated drift, image degradation, appearance drift, geometry/identity drift, and motion overshoot. Do not “repair” intended motion back toward the reference pose.
- Prefer the minimum correction needed. Preserve originals; write restoration outputs to a separate directory and validate them before accepting them.
- Never claim a frame was generated, saved, inspected, or repaired unless the tool call and local-file checks support that claim. Treat one run as an observed case, not general scientific evidence.

## Before acting

Default to completing the whole requested video in one run; do not make the user choose frame count or intermediate technical steps when they supplied duration and frame rate. Read [references/workflow.md](references/workflow.md) for defaults and planning rules. Inspect existing files/state first and never overwrite an existing sequence. Respect an explicit pilot/pause boundary.

Discover the actual image tools and their current input/output contract. Tool names and parameters vary by Codex installation. Use only documented available capabilities. An image displayed in a tool response is not proof of a file: locate its actual path or decode its returned bytes/data URL, write the PNG, reopen it locally, and verify it before advancing. Do not invent API names, infer support from UI display, or fall back to independent generation.

## Workflow

1. Translate the plain-language brief into duration, fps, scene, intended motion, aspect ratio, and output format. Calculate an exact frame count and checkpoint cadence; record any defaults in `state.json`.
2. Initialize or resume state without replacing the user's scene or files. Generate/verify the initial frame only if absent or explicitly requested.
3. Generate each next frame recursively from the immediately previous local PNG. Save and locally decode-verify each frame before proceeding.
4. At approximately two-second intervals, compare the current frame with its immediate predecessor and long-term reference. Diagnose, record, and adjust future per-frame prompting if needed. Two seconds is a review cadence, not a scene reset or independent generation batch.
5. If restoration is warranted, keep the original and use the current frame as pose/content authority, the previous frame for continuity when available, and the reference only for stable appearance/quality. Apply minimum necessary correction, save separately, then verify that legal motion survived.
6. Validate names, PNG decoding, dimensions, state/report consistency, and produce an ordered contact sheet. If the user requested a video and a compatible local encoder is installed, encode the ordered frames; otherwise deliver the verified frames and report the unavailable encoder.

The bundled scripts validate local frames and create contact sheets; they do not generate images or automatically decide whether a visual change is legitimate. See [references/workflow.md](references/workflow.md) for the full procedure and [examples/observed-run/](examples/observed-run/) for the specific pilot evidence from which this skill was derived.
