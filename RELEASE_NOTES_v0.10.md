# FitzSight v0.10.0 Release Notes

**Release theme:** Operator handoff and manual-submission boundary.

## Why this release exists

The analytical core and competition assets were already complete enough for the initial round. v0.10 does not expand the Agent intent catalog. Instead, it makes the final operating boundary explicit and packages the project so the user can take over all remaining external submission actions directly.

## Added

- `docs/OPERATOR_BOUNDARY.md`
- `submission/START_HERE_MANUAL.md`
- `submission/MANUAL_SUBMISSION_CHECKLIST.md`
- `submission/RUNTIME_VALIDATION_FOR_USER.md`
- `submission/GOAI_FIELD_MAP.md`
- `scripts/build_manual_handoff.py`
- `scripts/handoff_readiness.py`
- `submission/FitzSight_Manual_Handoff.zip`
- tests for the manual-boundary and handoff-packet behavior

## Changed

- package version updated to `0.10.0`;
- README/implementation status now describe the user-manual submission policy;
- local submission preflight now verifies the manual handoff ZIP and reports `external_write_actions_performed=false`;
- convenience upload bundle includes the manual operator documents;
- tracker/progress source records actual submission/confirmation as user-manual only.

## External action policy

By default, project automation may prepare, validate, hash, and package local assets. It does not:

- submit or edit the GOAI portal;
- upload competition files;
- access Gmail for confirmation;
- send/modify email;
- perform external account writes.

The user performs the actual portal submission and retains confirmation evidence.

## Unchanged analytical guarantees

- five approved Agent intents;
- read-only SQL / deterministic calculations;
- Evidence Registry;
- fail-closed EvidenceClaimVerifier;
- five-scenario benchmark;
- adversarial release gate;
- deterministic/offline demo fallback.
