from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "README.md",
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "streamlit_app.py",
    "evaluation/benchmark_catalog.json",
    "evaluation/adversarial_cases.json",
    "docs/COMPLIANCE_AND_SAFETY.md",
    "docs/INITIAL_ROUND_PROJECT_SUMMARY.md",
    "submission/FitzSight_GOAI_Initial_Round.pptx",
    "submission/FitzSight_GOAI_Initial_Round.pdf",
    "submission/DEMO_RUNBOOK.md",
    "submission/SUBMISSION_CHECKLIST.md",
    "submission/JUDGE_QA.md",
)

SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"OPENAI_API_KEY[ \t]*=[ \t]*[^\s#]+"),
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_secrets() -> list[str]:
    hits: list[str] = []
    text_suffixes = {".py", ".md", ".toml", ".json", ".txt", ".example", ".yaml", ".yml"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in text_suffixes:
            continue
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        if "SUBMISSION_PREFLIGHT" in path.name.upper():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                token = match.group(0)
                if token.startswith("OPENAI_API_KEY"):
                    value = token.split("=", 1)[1].strip().strip('"\'') if "=" in token else ""
                    if value in {"", "...", "<model>", "<key>", "<api-key>"}:
                        continue
                hits.append(f"{path.relative_to(ROOT)}: {token[:40]}")
    return hits


def run_preflight() -> dict[str, object]:
    missing = [rel for rel in REQUIRED_FILES if not (ROOT / rel).exists()]
    generated_csv = sorted(
        str(path.relative_to(ROOT))
        for path in (ROOT / "data" / "generated").glob("*.csv")
    )
    secrets = scan_secrets()

    pptx = ROOT / "submission" / "FitzSight_GOAI_Initial_Round.pptx"
    pdf = ROOT / "submission" / "FitzSight_GOAI_Initial_Round.pdf"
    assets = {}
    for path in (pptx, pdf):
        if path.exists():
            assets[path.name] = {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }

    passed = not missing and not generated_csv and not secrets and len(assets) == 2
    return {
        "passed": passed,
        "missing_required_files": missing,
        "generated_csv_files": generated_csv,
        "secret_hits": secrets,
        "submission_assets": assets,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FitzSight initial-round submission preflight.")
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
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
