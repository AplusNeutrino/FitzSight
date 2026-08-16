from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FINAL_PDF = ROOT / "submission" / "FitzSight_GOAI_初赛方案_CN.pdf"
DEFAULT_FILES = ("submission/FitzSight_GOAI_初赛方案_CN.pdf",)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_bundle(output: Path) -> dict[str, object]:
    if not FINAL_PDF.exists():
        raise FileNotFoundError(FINAL_PDF)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.write(FINAL_PDF, FINAL_PDF.name)
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None or archive.namelist() != [FINAL_PDF.name]:
            raise RuntimeError("Upload bundle must contain exactly the final Chinese PDF.")
    return {
        "product": "FitzSight",
        "version": "0.13.0",
        "output": str(output),
        "bytes": output.stat().st_size,
        "sha256": sha256(output),
        "file_count": 1,
        "files": [FINAL_PDF.name],
        "integrity": "PASS",
        "external_submission_performed": False,
        "network_actions_performed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the PDF-only GOAI initial-round upload bundle.")
    parser.add_argument("--output", default=str(ROOT / "submission" / "FitzSight_GOAI_Upload_Bundle.zip"))
    args = parser.parse_args()
    print(json.dumps(build_bundle(Path(args.output)), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
