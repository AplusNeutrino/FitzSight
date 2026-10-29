"""Content manifest for net-deposit inputs; not an immutable database snapshot."""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

NET_INPUTS = ('business_events.csv', 'customers.csv', 'deposits.csv', 'withdrawals.csv')


@dataclass(frozen=True)
class NetInputSnapshot:
    files: tuple[tuple[str, str], ...]

    def to_dict(self):
        return {'format': 'fitzsight.net-inputs.v1', 'files': dict(self.files)}

    @property
    def snapshot_id(self):
        encoded = json.dumps(self.to_dict(), sort_keys=True, separators=(',', ':')).encode('utf-8')
        return 'sha256:' + hashlib.sha256(encoded).hexdigest()


def fingerprint_net_inputs(data_dir):
    """Read only four approved regular files. Caller must prevent concurrent writes.

    Paths and mtimes are excluded so identical bytes in relocated directories
    produce the same identifier. No CSV/schema/financial semantics are inferred.
    """
    root = Path(data_dir).resolve(strict=True)
    files = []
    for name in NET_INPUTS:
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f'Expected regular non-symlink input: {name}')
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
        files.append((name, digest.hexdigest()))
    return NetInputSnapshot(tuple(files))
