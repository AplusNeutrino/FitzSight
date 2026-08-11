from __future__ import annotations

from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PPTX = ROOT / "submission" / "FitzSight_GOAI_Initial_Round.pptx"
PDF = ROOT / "submission" / "FitzSight_GOAI_Initial_Round.pdf"


def test_submission_deck_and_pdf_exist():
    assert PPTX.exists() and PPTX.stat().st_size > 10_000
    assert PDF.exists() and PDF.stat().st_size > 10_000


def test_submission_deck_has_twelve_slides():
    with zipfile.ZipFile(PPTX) as archive:
        slides = [
            name
            for name in archive.namelist()
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        ]
    assert len(slides) == 12


def test_submission_pdf_has_pdf_header():
    with PDF.open("rb") as handle:
        assert handle.read(5) == b"%PDF-"
