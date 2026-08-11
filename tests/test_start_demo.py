from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import start_demo


def args(**overrides):
    base = {
        "mode": "cli",
        "backend": "sqlite",
        "question": "Why did European FTD conversion deteriorate after July 15?",
        "port": 8501,
        "dry_run": True,
    }
    base.update(overrides)
    return argparse.Namespace(**base)


def test_cli_command_is_deterministic_and_bounded():
    mode, command = start_demo.build_command(args())
    assert mode == "cli"
    assert command[0] == sys.executable
    assert command[1].endswith("scripts/agent_investigate.py")
    assert "--planner" in command
    assert command[command.index("--planner") + 1] == "deterministic"
    assert command[command.index("--backend") + 1] == "sqlite"


def test_auto_falls_back_to_cli_when_streamlit_missing(monkeypatch):
    monkeypatch.setattr(start_demo, "streamlit_available", lambda: False)
    mode, command = start_demo.build_command(args(mode="auto"))
    assert mode == "cli"
    assert command[1].endswith("scripts/agent_investigate.py")


def test_ui_command_uses_python_module_streamlit(monkeypatch):
    monkeypatch.setattr(start_demo, "streamlit_available", lambda: True)
    mode, command = start_demo.build_command(args(mode="ui", port=8600))
    assert mode == "ui"
    assert command[:3] == [sys.executable, "-m", "streamlit"]
    assert "--server.headless=true" in command
    assert "--server.port=8600" in command
