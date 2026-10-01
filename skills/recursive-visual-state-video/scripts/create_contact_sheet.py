#!/usr/bin/env python3
"""Create an ordered, labeled contact sheet from numbered frames."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("Pillow is required: python -m pip install Pillow")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames-dir", type=Path, default=Path("frames"))
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, required=True, help="inclusive final frame number")
    parser.add_argument("--output", type=Path, default=Path("contact_sheet.png"))
    parser.add_argument("--columns", type=int, default=4)
    parser.add_argument("--thumb-width", type=int, default=480)
    args = parser.parse_args()
    if args.start < 0 or args.end < args.start or args.columns < 1 or args.thumb_width < 1:
        parser.error("invalid range, columns, or thumbnail width")

    frames: list[tuple[int, Image.Image]] = []
    for index in range(args.start, args.end + 1):
        path = args.frames_dir / f"frame_{index:03d}.png"
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            frames.append((index, image.convert("RGB")))

    thumb_h = max(1, round(frames[0][1].height * args.thumb_width / frames[0][1].width))
    label_h, gap = 26, 8
    rows = (len(frames) + args.columns - 1) // args.columns
    cell_h = label_h + thumb_h + gap
    sheet = Image.new("RGB", (args.columns * args.thumb_width, rows * cell_h), "#eeeeee")
    draw = ImageDraw.Draw(sheet)
    for position, (index, image) in enumerate(frames):
        col, row = position % args.columns, position // args.columns
        x, y = col * args.thumb_width, row * cell_h
        draw.text((x + 8, y + 5), f"frame_{index:03d}", fill="#111111", font=ImageFont.load_default())
        image.thumbnail((args.thumb_width, thumb_h), Image.Resampling.LANCZOS)
        sheet.paste(image, (x, y + label_h))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output)
    with Image.open(args.output) as check:
        check.verify()
    print(f"Wrote {args.output} ({sheet.width}x{sheet.height}), {len(frames)} frame(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
