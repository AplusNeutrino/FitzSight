from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_FILES = (
    "submission/FitzSight_GOAI_Initial_Round.pptx",
    "submission/FitzSight_GOAI_Initial_Round.pdf",
    "submission/PORTAL_COPY.md",
    "submission/FitzSight_Offline_Demo.html",
    "submission/FitzSight_Offline_Demo.json",
    "submission/FitzSight_Offline_Demo_Backup.mp4",
    "submission/PITCH_SPEAKER_NOTES.md",
    "submission/DEMO_RUNBOOK.md",
    "submission/PITCH_REHEARSAL.md",
    "submission/SUBMISSION_CHECKLIST.md",
    "docs/INITIAL_ROUND_PROJECT_SUMMARY.md",
    "docs/EVALUATION_SUMMARY.md",
    "docs/COMPLIANCE_AND_SAFETY.md",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a convenience ZIP containing FitzSight's initial-round upload assets.")
    parser.add_argument(
        "--output",
        default=str(ROOT / "submission" / "FitzSight_GOAI_Upload_Bundle.zip"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    missing = [rel for rel in DEFAULT_FILES if not (ROOT / rel).exists()]
    if missing:
        raise SystemExit(f"Missing required upload assets: {', '.join(missing)}")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="fitzsight_upload_") as tmp:
        stage = Path(tmp)
        files_meta = []
        for rel in DEFAULT_FILES:
            source = ROOT / rel
            destination = stage / source.name
            if destination.exists():
                destination = stage / rel.replace("/", "__")
            shutil.copy2(source, destination)
            files_meta.append(
                {
                    "name": destination.name,
                    "source": rel,
                    "bytes": destination.stat().st_size,
                    "sha256": sha256(destination),
                }
            )

        (stage / "REPOSITORY_LINK.txt").write_text(
            "FitzSight public repository:\nhttps://github.com/AplusNeutrino/FitzSight\n",
            encoding="utf-8",
        )
        files_meta.append(
            {
                "name": "REPOSITORY_LINK.txt",
                "source": "generated",
                "bytes": (stage / "REPOSITORY_LINK.txt").stat().st_size,
                "sha256": sha256(stage / "REPOSITORY_LINK.txt"),
            }
        )

        manifest = {
            "product": "FitzSight",
            "competition": "GOAI 2026 · Boundless Agents · AI+Finance",
            "purpose": "initial_round_upload_convenience_bundle",
            "note": "The official portal may require individual uploads. This ZIP is a local handoff convenience package, not evidence of portal submission.",
            "files": files_meta,
        }
        manifest_path = stage / "UPLOAD_MANIFEST.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        if output.exists():
            output.unlink()
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in sorted(p for p in stage.iterdir() if p.is_file()):
                archive.write(path, path.name)

    with zipfile.ZipFile(output, "r") as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"Corrupt file in upload ZIP: {bad}")
    print(json.dumps({
        "product": "FitzSight",
        "output": str(output),
        "bytes": output.stat().st_size,
        "sha256": sha256(output),
        "file_count": len(DEFAULT_FILES) + 2,
        "integrity": "PASS",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
