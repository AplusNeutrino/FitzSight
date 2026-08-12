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


def test_current_submission_deck_uses_v0121_one_plus_one_evidence_story():
    text = _pptx_text(ROOT / "submission" / "FitzSight_GOAI_Initial_Round.pptx")
    for expected in (
        "Autonomous investigation. Human decision.",
        "-7.53 pp",
        "-1.21 pp",
        "+29.15 min",
        "CRM-CHANGE-2026-0715#p1",
        "False correlation",
        "75%",
        "100%",
    ):
        assert expected in text
    for stale in ("Demo 2 —", "Demo 3 —", "Demo 4 —", "Demo 5 —"):
        assert stale not in text


def test_speaker_notes_are_generated_from_current_hero_and_evaluation(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(build_pitch_deck, "SUBMISSION_DIR", tmp_path)
    path = build_pitch_deck.build_speaker_notes()
    notes = path.read_text(encoding="utf-8")
    assert "-7.53 pp" in notes
    assert "+29.15 min" in notes
    assert "75%" in notes
    assert "architecture ablation" in notes.lower()
    assert "Generic LLM baseline" in notes
