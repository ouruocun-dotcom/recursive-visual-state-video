# Minimal user request

> Make a 4-second, 10 fps video of a red kite slowly rising over a windy beach. Keep the camera fixed and the scene consistent.

The Skill plans 40 frames (`frame_000.png`–`frame_039.png`) at a nominal four-second duration. It creates one initial image, then each subsequent image from the immediately preceding local PNG. It reviews drift after about every 20 frames (two seconds at 10 fps) without resetting the chain. It validates each saved file, repairs only when a diagnosed issue warrants it, and creates an ordered contact sheet. If `ffmpeg` is present it also writes and locally decode-checks a silent MP4. Otherwise it reports that MP4 encoding is unavailable and leaves the verified frames ready.

The user can override fps, duration, aspect ratio, reference frame, output directory, and checkpoint interval in the same natural-language request. No separate frame-count calculation is needed.
