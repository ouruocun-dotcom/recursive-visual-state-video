# Recursive Visual State Video

Give Codex a natural-language scene, action, and duration. The skill plans the frame count, creates frames sequentially from the previous saved frame, checks for cumulative drift at roughly two-second intervals, repairs quality drift into a separate directory when needed, validates the sequence, and builds a contact sheet. If local `ffmpeg` is available, it also encodes a silent MP4.

This workflow was derived from an observed 11-frame living-room run and one restoration of its final frame. The pilot showed later-frame softness/warmth and pose/composition drift; the final frame's raised hand exceeded the shoulder-height target. The restoration retained the overhead-arm pose while appearing sharper and more neutral on qualitative inspection. These observations are documented in [`skills/recursive-visual-state-video/examples/observed-run/`](skills/recursive-visual-state-video/examples/observed-run/) and are not a benchmark or a guarantee.

## Install directly from GitHub

After this repository is public, a user can paste its GitHub URL into Codex with this instruction:

> Install the `recursive-visual-state-video` Codex skill from this repository. Use the built-in `$skill-installer` and install the `skills/recursive-visual-state-video` directory.

Codex's built-in installer uses the specific skill-directory URL. The final form will be:

```text
$skill-installer install https://github.com/OWNER/REPOSITORY/tree/main/skills/recursive-visual-state-video
```

Replace `OWNER/REPOSITORY` with the published GitHub path. After installation, restart/refresh Codex as prompted. Then a request can be as simple as:

> Make a 4-second, 10 fps video of a red kite slowly rising over a windy beach. Keep the camera fixed and the scene consistent.

The skill derives 40 frames, uses a two-second visual-diagnosis cadence (about every 20 frames at 10 fps), and continues one recursive chain across those checkpoints. The user does not need to specify filenames, frame count, directory layout, repair procedure, or contact-sheet steps.

Codex skill structure and GitHub directory installation follow the [OpenAI Skills documentation](https://developers.openai.com/plugins/concepts/skills) and the built-in installer's [GitHub workflow](https://github.com/openai/skills/blob/main/skills/.system/skill-installer/SKILL.md). Installation still depends on the user's Codex build exposing `$skill-installer` and network access. A README cannot install itself before Codex has read the repository; the user's first message should explicitly ask Codex to install the skill from the URL.

## Automatic planning behavior

- Duration is read from the brief; if omitted, default to 3 seconds and record the assumption.
- Frame rate is read from the brief; if omitted, default to 10 fps and record it.
- Frame count is `max(1, round(duration_seconds × fps))`; names run from `frame_000.png` through `frame_{count-1:03}.png`.
- About every two seconds, inspect the latest frame against its predecessor and long-term reference. This is a diagnosis checkpoint, not a fresh generation segment: every frame still uses the immediately previous file as its primary visual input.
- Create a new timestamped run directory to avoid overwriting previous work. Typical contents are `frames/`, `frames_restored/` when needed, `state.json`, `drift_report.json`, `contact_sheet.png`, and `output.mp4` when local encoding works.
- The generator must discover the real image tool available in the user's Codex. The Skill does not pretend every install has the same image model/API. If recursive local image input or real-file output is unavailable, Codex reports the missing capability rather than silently generating independent frames.

See the [minimal natural-language request example](skills/recursive-visual-state-video/examples/quick-start.md).

## Local utilities

Python 3 and Pillow are used for PNG validation/contact sheets. `ffmpeg` is optional and only used for MP4 encoding. From the skill folder:

```bash
python -m pip install Pillow
python scripts/validate_frames.py --frames-dir /path/to/run/frames --start 0 --end 39
python scripts/create_contact_sheet.py --frames-dir /path/to/run/frames --start 0 --end 39 --output /path/to/run/contact_sheet.png
python scripts/encode_video.py --frames-dir /path/to/run/frames --start 0 --count 40 --fps 10 --output /path/to/run/output.mp4
```

The scripts validate or package local frames; they do not create images or judge identity/motion. See [`skills/recursive-visual-state-video/references/workflow.md`](skills/recursive-visual-state-video/references/workflow.md) and [`skills/recursive-visual-state-video/references/state-and-report-schema.md`](skills/recursive-visual-state-video/references/state-and-report-schema.md).

## License

MIT. See [`LICENSE`](LICENSE).
