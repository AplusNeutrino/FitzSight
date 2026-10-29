"""Request-bound input loading, independent of the legacy fixed-scenario runtime."""
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
from typing import Iterator

from fitzsight.data.snapshot import NET_INPUTS, NetInputSnapshot
from fitzsight.data.store import AnalyticsStore
from fitzsight.investigation.request import InvestigationRequest


@dataclass(frozen=True)
class NetInputSession:
    request: InvestigationRequest
    snapshot: NetInputSnapshot
    store: AnalyticsStore


@contextmanager
def open_net_input_store(
    request: InvestigationRequest, data_dir: str | Path, *, backend: str,
) -> Iterator[NetInputSession]:
    """Verify private copies, then materialize them before exposing the store.

    The copied bytes must match the explicit request, even if the source changes
    while copying. This is not an atomic upstream snapshot or a security boundary
    against same-process database writes. No synthetic inputs are generated.
    """
    if type(request) is not InvestigationRequest:
        raise ValueError('Expected a validated InvestigationRequest')
    root = Path(data_dir).resolve(strict=True)
    store = None
    try:
        with TemporaryDirectory(prefix='fitzsight-net-') as temporary:
            staging = Path(temporary)
            for name in NET_INPUTS:
                source = root / name
                if source.is_symlink() or not source.is_file():
                    raise ValueError(f'Expected regular non-symlink input: {name}')
                shutil.copyfile(source, staging / name)
            # Hash the exact private bytes that will be parsed, not the originals.
            snapshot = request.verify_snapshot(staging)
            store = AnalyticsStore(staging, backend=backend)
            store.load_csv_directory(
                include=[Path(name).stem for name in NET_INPUTS], materialize=True,
            )
        # Both backends now own in-memory tables; no CSV dependency survives.
        yield NetInputSession(request=request, snapshot=snapshot, store=store)
    finally:
        if store is not None:
            store.close()
