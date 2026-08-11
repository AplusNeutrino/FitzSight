# Repository Manifest

This package is the clean GitHub-ready FinSight v0.1.0 starter repository.

Key files:

- `MASTER_PLAN.md` — full GOAI/product/engineering plan and single project plan.
- `IMPLEMENTATION_STATUS.md` — current implementation truth for this release.
- `RELEASE_NOTES_v0.1.md` — what has actually been implemented and validated.
- `README.md` — public repository landing page.
- `src/finsight/` — implementation package.
- `scripts/` — runnable data-generation and baseline-analysis entry points.
- `tests/` — automated tests.
- `docs/BASELINE_RESULTS.md` — deterministic first benchmark result.
- `docs/DATA_DICTIONARY.md` — synthetic schema documentation.

Generated CSVs are deliberately excluded from the release package because they are reproducible from a fixed seed and are ignored by Git. Run `python scripts/generate_data.py` after setup.
