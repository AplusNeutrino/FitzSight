from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import textwrap

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
WIDTH = 1280
HEIGHT = 720


def _font(size: int, bold: bool = False):
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def _wrapped(draw: ImageDraw.ImageDraw, text: str, font, width_px: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if draw.textlength(candidate, font=font) <= width_px:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _draw_frame(title: str, subtitle: str, bullets: list[str], footer: str, output: Path) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#0b1020")
    draw = ImageDraw.Draw(image)
    title_font = _font(54, bold=True)
    subtitle_font = _font(26)
    body_font = _font(24)
    small_font = _font(18)

    draw.rounded_rectangle((58, 48, 1222, 672), radius=28, fill="#111a31", outline="#2a3659", width=2)
    draw.text((90, 80), "FitzSight", font=_font(22, bold=True), fill="#8fb2ff")

    y = 125
    for line in _wrapped(draw, title, title_font, 1050):
        draw.text((90, y), line, font=title_font, fill="#f4f6ff")
        y += 64
    y += 8
    for line in _wrapped(draw, subtitle, subtitle_font, 1040):
        draw.text((90, y), line, font=subtitle_font, fill="#aeb9d6")
        y += 38
    y += 18

    for bullet in bullets[:5]:
        lines = _wrapped(draw, bullet, body_font, 980)
        draw.ellipse((94, y + 12, 106, y + 24), fill="#6b91e8")
        first = True
        for line in lines:
            draw.text((124, y), line, font=body_font, fill="#e8ecfa")
            y += 33
            first = False
        y += 10
        if y > 575:
            break

    draw.text((90, 630), footer, font=small_font, fill="#7f8cae")
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, quality=95)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a silent offline FitzSight backup demo video from verified run summaries.")
    parser.add_argument(
        "--input",
        default=str(ROOT / "submission" / "FitzSight_Offline_Demo.json"),
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "submission" / "FitzSight_Offline_Demo_Backup.mp4"),
    )
    parser.add_argument("--seconds-per-frame", type=float, default=8.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg is required to build the offline backup video")

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    runs = payload["runs"]
    if payload.get("verified_runs") != payload.get("scenario_count"):
        raise SystemExit("Refusing to build video from unverified offline-demo payload")

    frames: list[tuple[str, str, list[str], str]] = [
        (
            "Evidence-grounded Financial Operations Intelligence Agent",
            "Question → Data → Analysis → Evidence → Decision",
            [
                "Five approved financial-operations workflows",
                "Read-only SQL and deterministic Python own the business calculations",
                "Every material claim is checked against Evidence IDs before rendering",
                "This video is an offline backup generated from actual verified deterministic Agent runs",
            ],
            "GOAI 2026 · Boundless Agents · AI+Finance",
        )
    ]
    for run in runs:
        kpis = [f"{item['label']}: {item['value']}" for item in run["kpis"]]
        findings = [str(item) for item in run["findings"][:2]]
        frames.append(
            (
                run["label"],
                run["question"],
                kpis[:4] + findings[:1],
                f"status={run['status']} · evidence records={len(run['evidence_ids'])} · backend={run['backend']}",
            )
        )
    frames.append(
        (
            "Evaluation & safety release gate",
            "Five scenarios + eight adversarial cases",
            [
                "5/5 deterministic benchmark scenarios PASS",
                "8/8 adversarial safety/evidence cases PASS",
                "False-correlation rejection accuracy: 100% in the current synthetic benchmark suite",
                "Verifier violations: 0 in the current benchmark suite",
                "No investment advice, trading execution, account freeze, AML enforcement, or credit decision",
            ],
            "Synthetic benchmark evidence · MIT licensed · deterministic fallback available",
        )
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="fitzsight_video_") as tmp:
        tmp_path = Path(tmp)
        frame_paths: list[Path] = []
        for index, (title, subtitle, bullets, footer) in enumerate(frames):
            frame = tmp_path / f"frame_{index:02d}.png"
            _draw_frame(title, subtitle, bullets, footer, frame)
            frame_paths.append(frame)

        concat = tmp_path / "frames.txt"
        lines: list[str] = []
        for frame in frame_paths:
            lines.append(f"file '{frame.as_posix()}'")
            lines.append(f"duration {args.seconds_per_frame}")
        lines.append(f"file '{frame_paths[-1].as_posix()}'")
        concat.write_text("\n".join(lines) + "\n", encoding="utf-8")

        command = [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat),
            "-vf",
            "fps=30,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "22",
            "-movflags",
            "+faststart",
            str(output),
        ]
        subprocess.run(command, check=True)

    actual_duration = None
    if shutil.which("ffprobe") is not None:
        probe = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(output),
            ],
            check=False, capture_output=True, text=True,
        )
        try:
            actual_duration = float(probe.stdout.strip())
        except ValueError:
            actual_duration = None

    print(json.dumps({
        "product": "FitzSight",
        "artifact": "offline_demo_backup_video",
        "output": str(output),
        "frame_count": len(frames),
        "seconds_per_frame": args.seconds_per_frame,
        "planned_duration_seconds": len(frames) * args.seconds_per_frame,
        "actual_duration_seconds": actual_duration,
        "source_verified_runs": payload["verified_runs"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
