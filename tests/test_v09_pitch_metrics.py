from __future__ import annotations

from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_pitch_deck


def _pptx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        chunks = []
        for name in sorted(archive.namelist()):
            if name.startswith("ppt/slides/slide") and name.endswith(".xml"):
                chunks.append(archive.read(name).decode("utf-8", errors="ignore"))
        return "\n".join(chunks)


def test_pitch_metric_source_is_current_verified_runtime():
    runs = build_pitch_deck._pitch_runs()
    assert len(runs) == 5
    assert all(run["final_answer"]["status"] == "verified" for run in runs.values())
    assert all(run["verification"]["passed"] for run in runs.values())


def test_current_submission_deck_uses_current_fixed_seed_values():
    text = _pptx_text(ROOT / "submission" / "FitzSight_GOAI_Initial_Round.pptx")
    for expected in ("-$187.8k", "+$59.2k", "+$246.9k", "91.6%", "3.7%", "53.7%"):
        assert expected in text
    for stale in ("-$223.9k", "+$24.4k", "+$248.3k", "92.2%", "55.8%"):
        assert stale not in text


def test_speaker_notes_are_generated_from_current_metrics(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(build_pitch_deck, "SUBMISSION_DIR", tmp_path)
    path = build_pitch_deck.build_speaker_notes()
    notes = path.read_text(encoding="utf-8")
    assert "-$187.8k" in notes
    assert "+$59.2k" in notes
    assert "91.6%" in notes
    assert "3.7%" in notes
    assert "53.7%" in notes
    assert "-$223.9k" not in notes
