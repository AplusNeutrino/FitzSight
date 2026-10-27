"""Separate runtime checks from competition assets without changing default collection."""
from pathlib import Path

import pytest

# Artifact-only modules. Mixed modules are classified per test below so runtime
# safety checks remain in the product suite regardless of historical filenames.
COMPETITION_MODULES = {
    'test_submission_assets.py',
    'test_submission_preflight.py',
    'test_v09_pitch_metrics.py',
    'test_v10_manual_handoff.py',
    'test_v12_1_deck_sync.py',
}
COMPETITION_TESTS = {
    'test_v09_submission_runtime_assets.py': {
        'test_offline_demo_contains_five_verified_workflows',
        'test_offline_backup_video_is_packaged_mp4',
        'test_upload_bundle_is_integrity_checked',
    },
    'test_v11_final_machine.py': {
        'test_rehearsal_evaluation_boundaries',
        'test_rehearsal_dry_run_has_no_external_action',
        'test_final_machine_kit_builds_with_local_only_manifest',
        'test_final_machine_docs_keep_submission_manual',
    },
    'test_v12_evaluation.py': {
        'test_v12_saved_holdout_evidence_is_complete',
    },
}


def pytest_collection_modifyitems(items):
    for item in items:
        filename = Path(item.path).name
        name = item.originalname or item.name
        competition = filename in COMPETITION_MODULES or name in COMPETITION_TESTS.get(filename, set())
        item.add_marker(pytest.mark.competition if competition else pytest.mark.product)
