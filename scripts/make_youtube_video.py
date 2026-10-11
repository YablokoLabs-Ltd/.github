#!/usr/bin/env python3
"""Combine vertical and horizontal clips into one 16:9 YouTube-ready video.

Every clip is placed on a 1920x1080 canvas:
  - Horizontal clips fill the frame.
  - Vertical (or any non-16:9) clips sit in the centre, sharp, on top of a
    blurred, zoomed-in copy of themselves, so there are no black bars.

Clips are joined with short crossfades (video and audio), audio levels are
evened out, and the whole video fades in and out. Clips without sound get
silence so the audio track never drops out.

Usage:
  python3 make_youtube_video.py clip1.mp4 clip2.mov ... -o final.mp4
  python3 make_youtube_video.py ./my_clips_folder -o final.mp4

Needs ffmpeg and ffprobe on PATH. Python standard library only.
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi", ".mts"}


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json",
         "-show_streams", "-show_format", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    info = json.loads(out)
    has_audio = any(s["codec_type"] == "audio" for s in info["streams"])
    duration = float(info["format"]["duration"])
    return has_audio, duration


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(result.stderr[-3000:])
        sys.exit(f"ffmpeg failed: {' '.join(cmd[:6])} ...")


def normalize(src, dst, w, h, fps, blur):
    """Re-encode one clip onto a WxH canvas with blur fill and clean audio."""
    has_audio, duration = probe(src)

    video = (
        f"[0:v]setsar=1,split=2[bgsrc][fgsrc];"
        # Background: zoom to cover the frame, blur it, dim it slightly.
        f"[bgsrc]scale={w}:{h}:force_original_aspect_ratio=increase,"
        f"crop={w}:{h},gblur=sigma={blur},eq=brightness=-0.08[bg];"
        # Foreground: fit inside the frame without cropping.
        f"[fgsrc]scale={w}:{h}:force_original_aspect_ratio=decrease[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2,fps={fps},format=yuv420p[v]"
    )
    audio = (
        "aresample=48000,aformat=channel_layouts=stereo,"
        "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000"
    )

    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(src)]
    if has_audio:
        graph = f"{video};[0:a]{audio}[a]"
    else:
        cmd += ["-f", "lavfi", "-t", f"{duration}",
                "-i", "anullsrc=channel_layout=stereo:sample_rate=48000"]
        graph = f"{video};[1:a]anull[a]"

    cmd += [
        "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
        "-t", f"{duration}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        str(dst),
    ]
    run(cmd)


def join(clips, out, fade, w, h):
    """Crossfade all normalized clips together and fade the ends."""
    durations = [probe(c)[1] for c in clips]
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for c in clips:
        cmd += ["-i", str(c)]

    parts = []
    v_prev, a_prev = "[0:v]", "[0:a]"
    timeline = durations[0]
    for i in range(1, len(clips)):
        # A fade can't be longer than half of either neighbouring clip.
        d = min(fade, durations[i - 1] / 2, durations[i] / 2)
        offset = timeline - d
        parts.append(
            f"{v_prev}[{i}:v]xfade=transition=fade:duration={d:.3f}:"
            f"offset={offset:.3f}[v{i}]"
        )
        parts.append(f"{a_prev}[{i}:a]acrossfade=d={d:.3f}[a{i}]")
        v_prev, a_prev = f"[v{i}]", f"[a{i}]"
        timeline = offset + durations[i]

    edge = min(0.5, timeline / 4)
    parts.append(
        f"{v_prev}fade=t=in:d={edge:.3f},"
        f"fade=t=out:st={timeline - edge:.3f}:d={edge:.3f}[vout]"
    )
    parts.append(
        f"{a_prev}afade=t=in:d={edge:.3f},"
        f"afade=t=out:st={timeline - edge:.3f}:d={edge:.3f}[aout]"
    )

    cmd += [
        "-filter_complex", ";".join(parts),
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(out),
    ]
    run(cmd)
    return timeline


def collect(inputs):
    files = []
    for item in inputs:
        p = Path(item)
        if p.is_dir():
            files += sorted(f for f in p.iterdir()
                            if f.suffix.lower() in VIDEO_EXTS)
        else:
            files.append(p)
    return files


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("inputs", nargs="+",
                    help="video files (in play order) or a folder")
    ap.add_argument("-o", "--output", default="youtube_ready.mp4")
    ap.add_argument("--fade", type=float, default=0.6,
                    help="crossfade seconds between clips (default 0.6)")
    ap.add_argument("--res", default="1920x1080",
                    help="output size, e.g. 1920x1080 or 3840x2160")
    ap.add_argument("--fps", default="30", help="output frame rate")
    ap.add_argument("--blur", type=float, default=40,
                    help="background blur strength (default 40)")
    args = ap.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found on PATH")

    clips = collect(args.inputs)
    if not clips:
        sys.exit("no video files found")
    w, h = (int(x) for x in args.res.lower().split("x"))

    with tempfile.TemporaryDirectory() as tmp:
        normalized = []
        for i, clip in enumerate(clips):
            print(f"[{i + 1}/{len(clips)}] preparing {clip.name}")
            dst = Path(tmp) / f"{i:04d}.mp4"
            normalize(clip, dst, w, h, args.fps, args.blur)
            normalized.append(dst)

        print("joining clips ...")
        total = join(normalized, args.output, args.fade, w, h)

    print(f"done: {args.output} ({total:.1f}s, {w}x{h})")


if __name__ == "__main__":
    main()
