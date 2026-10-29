from copy import deepcopy
from dataclasses import replace
from datetime import date

import pytest

from fitzsight.data.store import AnalyticsStore
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.concentration_claims import verify_concentration
from fitzsight.investigation.regional_claims import verify_regional
from fitzsight.investigation.net_deposit import NetDepositInvestigationEngine
from fitzsight.tools.sql import ReadOnlySQLTool
from test_concentration_claims import make_claim
from test_regional_claims import make_regional
from test_cashflow_completeness import write_bundle


@pytest.mark.parametrize('source_index', range(5))
@pytest.mark.parametrize('defect', ['truncated', 'missing_flag', 'false_string', 'false_integer',
                                  'missing_count', 'wrong_count', 'boolean_count', 'preview'])
def test_incomplete_comparison_source_rejected(source_index, defect):
    registry = EvidenceRegistry()
    concentration = source_index == 0
    claim = make_claim(registry) if concentration else make_regional(registry)
    binding = claim.numeric_binding
    ids = [binding.source_evidence_id] if concentration else list(binding.source_evidence_ids)
    index = 0 if concentration else source_index - 1
    original = registry.get(ids[index])
    payload = deepcopy(original.result)
    # Explicit valid metadata first, so only the selected defect causes rejection.
    payload.update(truncated=False, row_count=len(payload['rows']))
    if defect == 'truncated': payload['truncated'] = True
    elif defect == 'missing_flag': del payload['truncated']
    elif defect == 'false_string': payload['truncated'] = 'false'
    elif defect == 'false_integer': payload['truncated'] = 0
    elif defect == 'missing_count': del payload['row_count']
    elif defect == 'wrong_count': payload['row_count'] += 1
    elif defect == 'boolean_count': payload['row_count'] = True
    else:
        payload['evidence_mode'] = 'compact_preview'
        payload['rows_preview'] = payload['rows']
    changed = registry.register(original.tool_name, original.parameters, payload)
    ids[index] = changed.evidence_id
    derived = registry.get(binding.evidence_id)
    if concentration:
        derived.parameters['source_evidence_id'] = ids[0]
        binding = replace(binding, source_evidence_id=ids[0])
    else:
        derived.parameters['source_evidence_ids'] = tuple(ids)
        binding = replace(binding, source_evidence_ids=tuple(ids))
    claim = replace(claim, numeric_binding=binding, evidence_ids=claim.evidence_ids+(changed.evidence_id,))
    verify = verify_concentration if concentration else verify_regional
    assert not verify(claim, registry)


@pytest.mark.parametrize('backend', ['sqlite', 'duckdb'])
@pytest.mark.parametrize('start,end', [(date(2026,7,27),date(2026,8,2)),
                                     (date(2026,8,3),date(2026,8,9))])
def test_actual_regional_truncation_and_exact_limit(tmp_path, backend, start, end):
    write_bundle(tmp_path, None)
    with AnalyticsStore(tmp_path, backend=backend) as store:
        store.load_csv_directory()
        registry = EvidenceRegistry()
        engine = NetDepositInvestigationEngine(schema_tool=None,
            sql_tool=ReadOnlySQLTool(store, registry, max_rows=1), registry=registry)
        with pytest.raises(ValueError, match='Regional comparison requires complete SQL rows'):
            engine._regional_net_per_customer(start, end)
        assert any(r.result.get('truncated') is True for r in registry.records())
        engine.sql_tool = ReadOnlySQLTool(store, registry, max_rows=2)
        output, ids = engine._regional_net_per_customer(start, end)
        assert set(output) == {'Asia', 'Europe'}
        assert output['Europe']['net_deposits'] == 0
        assert all(registry.get(eid).result['row_count'] == 2 for eid in ids)
