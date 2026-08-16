from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUESTION = "Why did European FTD conversion deteriorate after July 15?"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="One-command FitzSight competition demo launcher."
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "ui", "cli"],
        default="auto",
        help="auto launches Streamlit when installed, otherwise runs the deterministic CLI fallback.",
    )
    parser.add_argument(
        "--backend",
        choices=["auto", "duckdb", "sqlite"],
        default=os.getenv("FITZSIGHT_BACKEND", "auto"),
    )
    parser.add_argument("--question", default=DEFAULT_QUESTION)
    parser.add_argument("--port", type=int, default=8501)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the selected command without launching it.",
    )
    return parser.parse_args()


def streamlit_available() -> bool:
    return importlib.util.find_spec("streamlit") is not None


def build_command(args: argparse.Namespace) -> tuple[str, list[str]]:
    requested = args.mode
    actual = requested
    if requested == "auto":
        actual = "ui" if streamlit_available() else "cli"

    if actual == "ui":
        if not streamlit_available():
            raise SystemExit(
                "Streamlit is not installed. Install the UI dependency with "
                '`pip install -e ".[ui]"` or use `--mode cli`.'
            )
        return actual, [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(ROOT / "streamlit_app.py"),
            "--global.developmentMode=false",
            "--server.headless=true",
            f"--server.port={args.port}",
        ]

    return actual, [
        sys.executable,
        str(ROOT / "scripts" / "agent_investigate.py"),
        "--backend",
        args.backend,
        "--planner",
        "deterministic",
        "--question",
        args.question,
    ]


def main() -> int:
    args = parse_args()
    actual_mode, command = build_command(args)

    print(f"FitzSight demo mode: {actual_mode}")
    print("Command:", " ".join(command))
    if args.mode == "auto" and actual_mode == "cli":
        print(
            "Streamlit is unavailable in this environment; running the deterministic "
            "competition-safe CLI fallback instead."
        )

    if args.dry_run:
        return 0

    completed = subprocess.run(command, cwd=ROOT, check=False)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
