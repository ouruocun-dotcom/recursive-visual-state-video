# Package audit

Audit performed locally on 2026-10-01 after implementation. This is a scoped package review, not an external security or scientific review.

## Requested behavior

- **Recursive input is mandatory:** the skill requires reading the previous PNG from disk and passing it as the primary image input for every transition. It explicitly forbids silent independent-frame fallback.
- **Long-term reference has a separate role:** current frame controls pose/content; predecessor supplies local continuity; reference anchors appearance/quality. The repair prompt must not transfer the reference pose.
- **Diagnosis distinguishes motion and errors:** the workflow names legitimate temporal change, cumulative drift, degradation, appearance drift, geometry/identity drift, and motion overshoot, and requires evidence/confidence rather than assuming each difference is drift.
- **Repair is conservative:** it specifies minimum-correction ordering, preserves source files, separates outputs, and treats a changed valid pose as failed restoration.
- **Post-repair checks are explicit:** image decodability and visual comparison against current, previous, and reference are both required. The docs state that a valid PNG alone is not proof of visual success.
- **State and reporting are reproducible:** JSON templates distinguish intended from observed motion, verified frames, findings, repair details, evidence method, and limitations.
- **No hidden API assumptions:** the tool discovery gate requires checking actual session capabilities. The observed `image_gen.imagegen` parameters and path behavior are scoped to this case; no API endpoint or SDK is invented.
- **No inflated research claims:** the observed case is labeled qualitative, with red-speckle reduction and quantitative metrics explicitly unverified.

## Checks run

- Existing `frames/frame_000.png` through `frame_010.png`: all 11 files passed local PNG decoding and had consistent 1672×941 dimensions.
- `scripts/validate_frames.py`: passed against the retained 11-frame sequence.
- Smoke test: generated three temporary PNGs, ran sequence validation, generated a contact sheet, and reopened/verified that sheet.
- Both example JSON files parsed; all three Python scripts compiled; linked reference/example paths were checked.
- User-flow docs define duration/fps defaults, exact frame-count derivation, a two-second diagnostic cadence that preserves one continuous recursive chain, and first-install guidance through the built-in GitHub skill installer.
- The optional local encoder refuses existing outputs, checks its PNG input sequence, attempts a local decode verification, and does not download/install ffmpeg or add audio. No ffmpeg binary exists in this environment, so successful MP4 encoding could not be exercised here.
- The observed sequence and restoration comparison images were created from the retained local PNGs and visually inspected.
- The Skill Creator `quick_validate.py` was attempted but could not run because PyYAML (`yaml`) is absent from both the active and bundled Python runtimes. The simple frontmatter structure, required keys, naming pattern, and description were checked locally instead. No package was installed for this audit.

## Remaining limits

- The image-tool restoration is generative and may change pixels beyond the requested quality correction. The skill requires visual rejection/retry when state changes, but cannot guarantee perfect recovery.
- A single restored frame does not validate whole-sequence restoration or general model performance.
- No actual `frame_000`–`frame_010` restoration batch, video encoding, external API integration, or GitHub publication was performed.
- No independent human reviewer participated. This audit is an additional checklist pass over the resulting package and test outputs.
