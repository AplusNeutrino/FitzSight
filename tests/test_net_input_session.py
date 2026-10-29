from pathlib import Path
import shutil
import sqlite3

import duckdb

import pytest

from fitzsight.data.snapshot import NET_INPUTS, fingerprint_net_inputs
from fitzsight.data.store import AnalyticsStore
from fitzsight.investigation.inputs import open_net_input_store
from fitzsight.investigation.request import InvestigationRequest
from test_request import payload


def source_bundle(root):
    root.mkdir()
    for name in NET_INPUTS:
        (root / name).write_text('id,amount\na,10\nb,20\n')
    (root / 'truth_gt.csv').write_text('secret\nnot_loaded\n')
    p = payload()
    p['data_snapshot'] = fingerprint_net_inputs(root).snapshot_id
    return InvestigationRequest.from_dict(p)


@pytest.mark.parametrize('backend', ['sqlite', 'duckdb'])
def test_materialized_session_survives_source_changes_and_removal(tmp_path, backend):
    root = tmp_path / 'source'
    request = source_bundle(root)
    original = {p.name: p.read_bytes() for p in root.iterdir()}
    with open_net_input_store(request, root, backend=backend) as session:
        store = session.store
        assert session.request == request
        assert session.snapshot.snapshot_id == request.data_snapshot
        assert store.list_tables() == sorted(Path(n).stem for n in NET_INPUTS)
        assert not store.data_dir.exists()  # Private staging deleted before yield.
        assert original == {p.name: p.read_bytes() for p in root.iterdir()}
        (root / 'deposits.csv').write_text('id,amount\na,999\n')
        shutil.rmtree(root)
        for table in store.list_tables():
            assert store.execute(f'SELECT SUM(amount) FROM {table}')[1] == [(30,)]
    with pytest.raises(sqlite3.ProgrammingError if backend == 'sqlite' else duckdb.ConnectionException):
        store.execute('SELECT 1')


@pytest.mark.parametrize('backend', ['sqlite', 'duckdb'])
@pytest.mark.parametrize('name', NET_INPUTS)
def test_changed_source_rejected_before_database_creation(tmp_path, backend, name, monkeypatch):
    root = tmp_path / 'source'
    request = source_bundle(root)
    (root / name).write_text('id,amount\na,99\n')
    def unexpected_store(*args, **kwargs):
        pytest.fail('Snapshot mismatch must fail before database construction')
    monkeypatch.setattr('fitzsight.investigation.inputs.AnalyticsStore', unexpected_store)
    with pytest.raises(ValueError, match='does not match'):
        with open_net_input_store(request, root, backend=backend):
            pytest.fail('Must not expose a mismatched session')


@pytest.mark.parametrize('backend', ['sqlite', 'duckdb'])
def test_consumer_error_closes_store(tmp_path, backend):
    root = tmp_path / 'source'
    request = source_bundle(root)
    with pytest.raises(RuntimeError, match='consumer'):
        with open_net_input_store(request, root, backend=backend) as session:
            store = session.store
            raise RuntimeError('consumer')
    assert not store.data_dir.exists()
    with pytest.raises(sqlite3.ProgrammingError if backend == 'sqlite' else duckdb.ConnectionException):
        store.execute('SELECT 1')


@pytest.mark.parametrize('backend', ['sqlite', 'duckdb'])
def test_loading_error_closes_store_and_removes_staging(tmp_path, backend, monkeypatch):
    root = tmp_path / 'source'
    request = source_bundle(root)
    seen = []
    original = AnalyticsStore.load_csv_directory
    def fail_after_loading(self, *args, **kwargs):
        seen.append(self)
        original(self, *args, **kwargs)
        raise RuntimeError('injected load error')
    monkeypatch.setattr(AnalyticsStore, 'load_csv_directory', fail_after_loading)
    with pytest.raises(RuntimeError, match='injected load error'):
        with open_net_input_store(request, root, backend=backend):
            pytest.fail('Must not expose partially loaded store')
    assert len(seen) == 1
    assert not seen[0].data_dir.exists()
    with pytest.raises(sqlite3.ProgrammingError if backend == 'sqlite' else duckdb.ConnectionException):
        seen[0].execute('SELECT 1')


@pytest.mark.parametrize('mode', ['missing', 'directory', 'symlink'])
def test_invalid_source_file_refused_without_source_writes(tmp_path, mode):
    root = tmp_path / 'source'
    request = source_bundle(root)
    path = root / 'customers.csv'
    path.unlink()
    if mode == 'directory':
        path.mkdir()
    elif mode == 'symlink':
        path.symlink_to(root / 'deposits.csv')
    with pytest.raises(ValueError, match='customers.csv'):
        with open_net_input_store(request, root, backend='sqlite'):
            pytest.fail('Invalid source must not yield')
    assert (root / 'deposits.csv').read_text() == 'id,amount\na,10\nb,20\n'


def test_copy_time_change_compared_to_copied_bytes(tmp_path, monkeypatch):
    root = tmp_path / 'source'
    request = source_bundle(root)
    original = shutil.copyfile
    destinations = []
    def changed_copy(src, dst):
        destinations.append(Path(dst).parent)
        original(src, dst)
        if Path(src).name == 'deposits.csv':
            Path(dst).write_text('id,amount\na,777\n')
    monkeypatch.setattr('fitzsight.investigation.inputs.shutil.copyfile', changed_copy)
    with pytest.raises(ValueError, match='does not match'):
        with open_net_input_store(request, root, backend='sqlite'):
            pytest.fail('Must verify copies rather than originals')
    assert all(not p.exists() for p in destinations)
    assert fingerprint_net_inputs(root).snapshot_id == request.data_snapshot


@pytest.mark.parametrize('backend', ['sqlite', 'duckdb'])
def test_two_sessions_keep_distinct_verified_inputs(tmp_path, backend):
    root = tmp_path / 'source'
    first = source_bundle(root)
    with open_net_input_store(first, root, backend=backend) as a:
        (root / 'deposits.csv').write_text('id,amount\na,99\n')
        p = first.to_dict()
        p['data_snapshot'] = fingerprint_net_inputs(root).snapshot_id
        second = InvestigationRequest.from_dict(p)
        with open_net_input_store(second, root, backend=backend) as b:
            assert a.snapshot != b.snapshot
            assert a.store.execute('SELECT SUM(amount) FROM deposits')[1] == [(30,)]
            assert b.store.execute('SELECT SUM(amount) FROM deposits')[1] == [(99,)]
        assert a.store.execute('SELECT SUM(amount) FROM deposits')[1] == [(30,)]
