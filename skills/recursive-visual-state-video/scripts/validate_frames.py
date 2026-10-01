#!/usr/bin/env python3
"""Validate numbered PNG frames locally; does not generate or alter images."""

from __future__ import annotations

import argparse
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
    parser.add_argument("--end", type=int, required=True, help="inclusive final frame number")
    parser.add_argument("--prefix", default="frame_")
    args = parser.parse_args()

    if args.start < 0 or args.end < args.start:
        parser.error("require 0 <= start <= end")

    failures: list[str] = []
    sizes: set[tuple[int, int]] = set()
    for index in range(args.start, args.end + 1):
        path = args.frames_dir / f"{args.prefix}{index:03d}.png"
        if not path.is_file():
            failures.append(f"missing: {path}")
            continue
        try:
            with Image.open(path) as image:
                if image.format != "PNG":
                    raise ValueError(f"decoded as {image.format}, expected PNG")
                image.verify()
            with Image.open(path) as image:
                sizes.add(image.size)
                print(f"OK {path} {image.size[0]}x{image.size[1]}")
        except Exception as exc:  # report decoder failures for each path
            failures.append(f"unreadable: {path}: {exc}")

    if len(sizes) > 1:
        failures.append(f"inconsistent image dimensions: {sorted(sizes)}")
    if failures:
        print("Validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"Validated {args.end - args.start + 1} PNG frame(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
