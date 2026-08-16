from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FINAL_PDF = "submission/FitzSight_GOAI_初赛方案_CN.pdf"

REQUIRED_FILES = (
    "README.md",
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "pyproject.toml",
    "streamlit_app.py",
    "requirements.txt",
    ".streamlit/config.toml",
    ".streamlit/secrets.toml.example",
    "src/fitzsight/ui/demo_config.py",
    "src/fitzsight/providers/deepseek_planner.py",
    "scripts/validate_deepseek_runtime.py",
    "scripts/final_machine_check.py",
    "scripts/build_cn_submission.py",
    "scripts/render_cn_submission.mjs",
    "scripts/assemble_cn_pdf.py",
    "submission/deck-cn/index.html",
    "submission/deck-cn/BUILD_INFO.json",
    FINAL_PDF,
    "submission/PORTAL_COPY.md",
    "docs/ARCHITECTURE.md",
    "docs/MODEL_PROVIDER.md",
    "docs/COMPLIANCE_AND_SAFETY.md",
    "docs/ONLINE_DEMO_DEPLOYMENT.md",
    "docs/V0.13_VALIDATION.md",
    "docs/PROJFITZGERALD_PROGRESS_SNAPSHOT.md",
    "RELEASE_NOTES_v0.13.md",
)

SECRET_PATTERNS = (
    re.compile(r"DEEPSEEK_API_KEY[ \t]*=[ \t]*[^\s#]+"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
)

SAFE_SECRET_PLACEHOLDERS = {
    "...",
    "<api-key>",
    "<key>",
    "<your-key>",
    "your_deepseek_api_key",
    "在这里填写deepseekapikey",
    "在这里填写",
}

FORBIDDEN_ACTIVE_PATTERNS = (
    re.compile("Fin" + "Sight", re.IGNORECASE),
    re.compile(r"FIN\s+SIGHT", re.IGNORECASE),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan_secrets() -> list[str]:
    hits: list[str] = []
    text_suffixes = {".py", ".md", ".toml", ".json", ".txt", ".example", ".yaml", ".yml", ".html"}
    ignored_parts = {
        ".git",
        ".venv",
        ".test-deps",
        ".test-venv",
        "__pycache__",
        ".pytest_cache",
        "rendered",
        "pdf-review",
    }
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in text_suffixes:
            continue
        if any(part in ignored_parts for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            # Ignore unreadable local dependency shims; delivery contents are
            # controlled separately by explicit build allowlists.
            continue
        for pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                token = match.group(0)
                if token.startswith("DEEPSEEK_API_KEY"):
                    value = token.split("=", 1)[1].strip().strip('"\'') if "=" in token else ""
                    normalized = re.sub(r"\s+", "", value).casefold()
                    if normalized in SAFE_SECRET_PLACEHOLDERS:
                        continue
                if any(marker in token for marker in ("test-secret", "must-not-appear")):
                    continue
                hits.append(f"{path.relative_to(ROOT)}: {token[:40]}")
    return hits


def _pdf_page_count(path: Path) -> int | None:
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    return len(PdfReader(path).pages)


def run_preflight(*, require_final_machine_kit: bool = True) -> dict[str, object]:
    del require_final_machine_kit  # Kept for API compatibility with final_machine_check.py.
    missing = [rel for rel in REQUIRED_FILES if not (ROOT / rel).exists()]
    generated_csv = sorted(str(path.relative_to(ROOT)) for path in (ROOT / "data" / "generated").glob("*.csv"))
    pdf_path = ROOT / FINAL_PDF
    pdf_header_ok = pdf_path.exists() and pdf_path.read_bytes()[:5] == b"%PDF-"
    pdf_pages = _pdf_page_count(pdf_path) if pdf_header_ok else None
    old_pptx = sorted(str(path.relative_to(ROOT)) for path in (ROOT / "submission").glob("*.pptx"))
    deck_html = ROOT / "submission" / "deck-cn" / "index.html"
    deck_text = deck_html.read_text(encoding="utf-8", errors="ignore") if deck_html.exists() else ""
    forbidden_deck_terms = [pattern.pattern for pattern in FORBIDDEN_ACTIVE_PATTERNS if pattern.search(deck_text)]
    secrets = scan_secrets()
    passed = (
        not missing
        and not generated_csv
        and not secrets
        and not old_pptx
        and pdf_header_ok
        and pdf_pages in {12, None}
        and not forbidden_deck_terms
    )
    return {
        "product": "FitzSight",
        "version": "0.13.0",
        "passed": passed,
        "missing_required_files": missing,
        "generated_csv_files": generated_csv,
        "secret_hits": secrets,
        "legacy_pptx_files": old_pptx,
        "forbidden_deck_terms": forbidden_deck_terms,
        "final_pdf": {
            "path": FINAL_PDF,
            "header_ok": pdf_header_ok,
            "pages": pdf_pages,
            "bytes": pdf_path.stat().st_size if pdf_path.exists() else 0,
            "sha256": sha256(pdf_path) if pdf_path.exists() else None,
        },
        "deepseek_live": "not_requested",
        "manual_submission_boundary": {
            "mode": "user_manual_only",
            "external_write_actions_performed": False,
            "portal_upload_or_submit_by_automation": False,
            "email_access_by_automation": False,
        },
        "external_actions_still_required": [
            "USER MANUAL: upload only FitzSight_GOAI_初赛方案_CN.pdf to the GOAI initial-round portal",
            "USER MANUAL: review the portal state and complete final submission",
            "USER MANUAL: retain portal confirmation evidence",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="FitzSight v0.13 Chinese PDF submission preflight.")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    report = run_preflight()
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
