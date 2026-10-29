import hashlib
import json
import shutil
import pytest
from fitzsight.data.snapshot import NET_INPUTS, fingerprint_net_inputs
from fitzsight.investigation.request import InvestigationRequest
from test_request import payload


def bundle(root):
    root.mkdir()
    for name in NET_INPUTS:
        (root / name).write_bytes(b'a,b\n1,2\n')
    return root


def test_manifest_matches_independent_hash_and_relocation(tmp_path):
    root = bundle(tmp_path / 'original')
    before = {n: (root/n).read_bytes() for n in NET_INPUTS}
    s = fingerprint_net_inputs(root)
    manifest = {'format': 'fitzsight.net-inputs.v1', 'files': {n: hashlib.sha256(before[n]).hexdigest() for n in NET_INPUTS}}
    expected = 'sha256:' + hashlib.sha256(json.dumps(manifest,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert s.snapshot_id == expected
    shutil.copytree(root, tmp_path / 'copy')
    assert fingerprint_net_inputs(tmp_path / 'copy') == s
    (root/'truth_gt.csv').write_text('ignored')
    assert fingerprint_net_inputs(root) == s
    assert before == {n: (root/n).read_bytes() for n in NET_INPUTS}
    p = payload(); p['data_snapshot'] = expected
    assert InvestigationRequest.from_dict(p).verify_snapshot(root) == s


@pytest.mark.parametrize('name', NET_INPUTS)
def test_each_changed_file_invalidates_request(tmp_path, name):
    root = bundle(tmp_path/'data')
    p = payload(); p['data_snapshot'] = fingerprint_net_inputs(root).snapshot_id
    request = InvestigationRequest.from_dict(p)
    (root/name).write_bytes(b'a,b\n1,3\n')
    with pytest.raises(ValueError, match='does not match'):
        request.verify_snapshot(root)


@pytest.mark.parametrize('mode', ['missing', 'directory', 'symlink'])
def test_invalid_file_refused(tmp_path, mode):
    root = bundle(tmp_path/'data'); path = root/'customers.csv'; path.unlink()
    if mode == 'directory': path.mkdir()
    if mode == 'symlink': path.symlink_to(root/'deposits.csv')
    with pytest.raises(ValueError, match='customers.csv'):
        fingerprint_net_inputs(root)


def test_missing_directory_not_created(tmp_path):
    with pytest.raises(FileNotFoundError):
        fingerprint_net_inputs(tmp_path/'missing')
    assert not (tmp_path/'missing').exists()
