#!/usr/bin/env python3
"""Encode a contiguous numbered PNG sequence to a silent H.264 MP4 using ffmpeg."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    raise SystemExit("Pillow is required: python -m pip install Pillow")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames-dir", type=Path, default=Path("frames"))
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, required=True, help="number of contiguous frames")
    parser.add_argument("--fps", type=float, required=True)
    parser.add_argument("--output", type=Path, default=Path("output.mp4"))
    args = parser.parse_args()

    if args.start < 0 or args.count < 1 or args.fps <= 0:
        parser.error("start must be nonnegative, count and fps must be positive")
    if args.output.exists():
        print(f"Refusing to overwrite existing output: {args.output}", file=sys.stderr)
        return 2

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("ffmpeg is not installed or not on PATH; frames were not changed.", file=sys.stderr)
        return 127

    sizes: set[tuple[int, int]] = set()
    for index in range(args.start, args.start + args.count):
        path = args.frames_dir / f"frame_{index:03d}.png"
        if not path.is_file():
            print(f"Missing input frame: {path}", file=sys.stderr)
            return 1
        try:
            with Image.open(path) as image:
                if image.format != "PNG":
                    raise ValueError(f"expected PNG, got {image.format}")
                image.verify()
            with Image.open(path) as image:
                sizes.add(image.size)
        except Exception as exc:
            print(f"Unreadable input frame {path}: {exc}", file=sys.stderr)
            return 1
    if len(sizes) != 1:
        print(f"Input dimensions differ: {sorted(sizes)}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-n",
        "-framerate",
        str(args.fps),
        "-start_number",
        str(args.start),
        "-i",
        str(args.frames_dir / "frame_%03d.png"),
        "-frames:v",
        str(args.count),
        "-vf",
        "pad=ceil(iw/2)*2:ceil(ih/2)*2",
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(args.output),
    ]
    try:
        result = subprocess.run(command, check=False)
    except OSError as exc:
        print(f"Could not run ffmpeg: {exc}", file=sys.stderr)
        return 1
    if result.returncode != 0:
        print(f"ffmpeg failed with exit code {result.returncode}", file=sys.stderr)
        return result.returncode
    if not args.output.is_file() or args.output.stat().st_size == 0:
        print("ffmpeg returned success but no non-empty output file exists", file=sys.stderr)
        return 1
    verification = subprocess.run(
        [ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(args.output), "-f", "null", "-"],
        check=False,
    )
    if verification.returncode != 0:
        print(f"Encoded output failed a local decode check (exit {verification.returncode})", file=sys.stderr)
        return verification.returncode
    duration = args.count / args.fps
    print(f"Encoded {args.count} frames at {args.fps:g} fps ({duration:g}s): {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
