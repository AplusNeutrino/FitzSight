# FitzSight v0.2.0 Repository Manifest

This manifest describes the intended GitHub snapshot for the v0.2.0 delivery.

## Root

- `.env.example` — secret-free configuration template
- `.gitignore` — generated-data, cache and secret exclusions
- `README.md` — project overview, quick start, safety and limitations
- `MASTER_PLAN.md` — competition/product master plan, normalized to FitzSight
- `PROJECT_PROGRESS.md` — pointer to external progress source of truth
- `IMPLEMENTATION_STATUS.md` — v0.2 implementation and validation state
- `RELEASE_NOTES_v0.1.md` — historical v0.1 notes with current product naming
- `RELEASE_NOTES_v0.2.md` — v0.2 release notes
- `pyproject.toml` — Python package/dependencies (`fitzsight` v0.2.0)
- `SHA256SUMS.txt` — integrity hashes for repository files other than itself

## Source package

```text
src/fitzsight/
├── analytics/
├── data/
│   └── store.py
├── evidence/
├── investigation/
└── tools/
```

v0.2 introduces the analytical store, read-only Tool Layer, expanded evidence registry and deterministic investigation engine.

## Scripts

- `scripts/generate_data.py`
- `scripts/run_baseline.py`
- `scripts/investigate.py`

## Tests

The repository contains v0.1 regression tests plus v0.2 tests for:

- evidence registry;
- SQL safety;
- store/schema/SQL integration;
- KPI and period comparison;
- statistical tests;
- deterministic investigation;
- optional DuckDB backend integration.

## Documentation

- `docs/DATA_DICTIONARY.md`
- `docs/BASELINE_RESULTS.md`
- `docs/ARCHITECTURE.md`
- `docs/TOOL_LAYER.md`
- `docs/V0.2_VALIDATION.md`

## Generated data

`data/generated/` contains only `.gitkeep` in the repository. CSV/JSON outputs are generated locally and ignored by Git.
