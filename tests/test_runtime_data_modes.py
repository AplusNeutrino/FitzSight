from pathlib import Path
import subprocess
import sys

import pytest
from pandas.errors import EmptyDataError

from fitzsight.agent.planner import ConstrainedRulePlanner
from fitzsight.data.generator import GeneratorConfig, write_csv_bundle
from fitzsight.runtime import build_agent_runtime

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ('customers', 'sales_activity', 'deposits', 'withdrawals', 'trades', 'business_events')


def snapshot(path):
    return {str(p.relative_to(path)): p.read_bytes() for p in path.rglob('*') if p.is_file()}


def build(path, **kwargs):
    return build_agent_runtime(data_dir=path, backend='sqlite', planner=ConstrainedRulePlanner(), **kwargs)


@pytest.mark.parametrize('mode', [None, 'import'])
def test_import_missing_directory_has_no_side_effects(tmp_path, mode):
    path = tmp_path / 'absent'
    with pytest.raises(FileNotFoundError, match='customers.csv'):
        build(path, **({} if mode is None else {'data_mode': mode}))
    assert not path.exists()


@pytest.mark.parametrize('missing', REQUIRED)
def test_each_missing_import_file_preserves_all_existing_bytes(tmp_path, missing):
    for name in REQUIRED:
        if name != missing:
            (tmp_path / f'{name}.csv').write_text('user-owned data,do not replace\n')
    before = snapshot(tmp_path)
    with pytest.raises(FileNotFoundError, match=missing + '.csv'):
        build(tmp_path, data_mode='import')
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize('mode', ['import', 'demo'])
def test_directory_in_place_of_required_file_is_rejected(tmp_path, mode):
    (tmp_path / 'customers.csv').mkdir()
    with pytest.raises((FileNotFoundError, ValueError)):
        build(tmp_path, data_mode=mode)
    assert list(tmp_path.iterdir()) == [tmp_path / 'customers.csv']


def test_demo_refuses_partial_bundle_and_unrelated_files(tmp_path):
    (tmp_path / 'notes.txt').write_text('keep me')
    before = snapshot(tmp_path)
    with pytest.raises(ValueError, match='empty directory'):
        build(tmp_path, data_mode='demo')
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize('backend', ['sqlite', 'duckdb'])
def test_explicit_demo_then_import_reads_identical_bundle(tmp_path, backend):
    path = tmp_path / 'data'
    config = GeneratorConfig(seed=123, n_customers=1000, n_salespeople=20)
    store, _, _ = build_agent_runtime(data_dir=path, backend=backend,
        planner=ConstrainedRulePlanner(), data_mode='demo', generator_config=config)
    store.close()
    before = snapshot(path)
    assert all(f'{name}.csv' in before for name in REQUIRED)
    store, _, _ = build_agent_runtime(data_dir=path, backend=backend,
        planner=ConstrainedRulePlanner(), data_mode='import')
    store.close()
    assert snapshot(path) == before


def test_invalid_mode_and_import_generator_config_fail_before_writes(tmp_path):
    path = tmp_path / 'absent'
    for kwargs in ({'data_mode': 'typo'}, {'data_mode': 'import', 'generator_config': GeneratorConfig()}):
        with pytest.raises(ValueError):
            build(path, **kwargs)
    assert not path.exists()


def test_cli_default_import_missing_data_fails_without_output_or_writes(tmp_path):
    path = tmp_path / 'absent'
    output = tmp_path / 'result.json'
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/agent_investigate.py'),
        '--data-dir', str(path), '--output', str(output), '--backend', 'sqlite'],
        capture_output=True, text=True, timeout=30)
    assert result.returncode != 0
    assert 'Import data is incomplete' in result.stderr
    assert not path.exists()
    assert not output.exists()


def test_complete_but_malformed_import_does_not_repair_files(tmp_path):
    for name in REQUIRED:
        (tmp_path / f'{name}.csv').write_bytes(b'')
    before = snapshot(tmp_path)
    with pytest.raises(EmptyDataError):
        build(tmp_path, data_mode='import')
    assert snapshot(tmp_path) == before


def test_cli_explicit_import_reads_existing_bundle(tmp_path):
    import json
    path = tmp_path / 'data'
    write_csv_bundle(path, GeneratorConfig(seed=123, n_customers=1000, n_salespeople=20))
    before = snapshot(path)
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/agent_investigate.py'),
        '--data-mode', 'import', '--data-dir', str(path), '--backend', 'sqlite',
        '--question', 'How are European customer segments distributed by behavioral value, and which segment contributes most to deposits?'],
        capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['runtime']['data_mode'] == 'import'
    assert snapshot(path) == before
