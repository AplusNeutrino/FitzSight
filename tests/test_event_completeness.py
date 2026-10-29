"""N-C5 must not certify absence or presence from preview event evidence."""
from copy import deepcopy
from dataclasses import replace

import pytest

from fitzsight.agent.verifier import EvidenceClaimVerifier
from fitzsight.data.store import AnalyticsStore
from fitzsight.evidence.registry import EvidenceRegistry
from fitzsight.investigation.event_claims import verify_event
from fitzsight.investigation.net_deposit import NetDepositInvestigationEngine
from fitzsight.tools.schema import SchemaInspectorTool
from fitzsight.tools.sql import ReadOnlySQLTool
from test_event_claims import make_event, row
from test_numeric_claims import fixture
from test_cashflow_completeness import write_bundle


@pytest.mark.parametrize('present', [False, True])
@pytest.mark.parametrize('marker', ['evidence_mode', 'rows_preview'])
def test_preview_marked_rows_never_certify_event_facts(present, marker):
    registry, result = fixture()
    claim = make_event(registry, [row()] if present else [])
    assert verify_event(claim, registry)
    original = registry.get(claim.event_binding.evidence_id)
    payload = deepcopy(original.result)
    payload[marker] = 'compact_preview' if marker == 'evidence_mode' else payload['rows']
    source = registry.register(original.tool_name, original.parameters, payload)
    # New ID and correct digest; only the preview marker differs.
    binding = replace(claim.event_binding, evidence_id=source.evidence_id)
    claim = replace(claim, event_binding=binding, evidence_ids=(source.evidence_id,))
    assert not verify_event(claim, registry)
    report = EvidenceClaimVerifier(registry).verify(replace(result, claims=result.claims[:-1]+(claim,)))
    failed = {check.check_id for check in report.checks if not check.passed}
    assert 'event_binding:N-C5' in failed


@pytest.mark.parametrize('backend', ['sqlite', 'duckdb'])
@pytest.mark.parametrize('count', [0, 2, 3])
def test_actual_event_limit_empty_and_complete_results(tmp_path, backend, count):
    write_bundle(tmp_path, None)
    (tmp_path / 'business_events.csv').write_text(
        'event_id,date,event_type,region,affected_team,description\n' + ''.join(
            f'event-{i},2026-08-05,HIGH_VALUE_WITHDRAWAL_CLUSTER,Europe,Team A,context\n'
            for i in range(count)))
    with AnalyticsStore(tmp_path, backend=backend) as store:
        store.load_csv_directory()
        registry = EvidenceRegistry()
        engine = NetDepositInvestigationEngine(schema_tool=SchemaInspectorTool(store, registry),
            sql_tool=ReadOnlySQLTool(store, registry, max_rows=2), registry=registry)
        if count > 2:
            with pytest.raises(ValueError, match='Event facts require complete SQL rows'):
                engine.investigate('Why did European net deposits decline this week?')
            assert registry.records()[-1].result['truncated'] is True
        else:
            result = engine.investigate('Why did European net deposits decline this week?')
            assert EvidenceClaimVerifier(registry).verify(result).passed
            claim = result.claims[-1]
            assert claim.event_binding.matched_event_ids == tuple(f'event-{i}' for i in range(count))
            assert claim.status == ('supported_with_guardrail' if count else 'insufficient_evidence')
            source = registry.get(claim.event_binding.evidence_id)
            assert source.result['row_count'] == count
            assert source.result['truncated'] is False


@pytest.mark.parametrize('backend', ['sqlite', 'duckdb'])
@pytest.mark.parametrize('count', [0, 2])
def test_actual_compact_evidence_cannot_certify_event_facts(tmp_path, backend, count):
    from fitzsight.investigation.event_claims import EventBinding, event_query, render_event
    from fitzsight.investigation.models import Claim

    write_bundle(tmp_path, None)
    (tmp_path / 'business_events.csv').write_text(
        'event_id,date,event_type,region,affected_team,description\n' + ''.join(
            f'event-{i},2026-08-05,HIGH_VALUE_WITHDRAWAL_CLUSTER,Europe,Team A,context\n'
            for i in range(count)))
    with AnalyticsStore(tmp_path, backend=backend) as store:
        store.load_csv_directory()
        registry = EvidenceRegistry()
        sql = ReadOnlySQLTool(store, registry)
        source = sql.run(event_query('2026-08-03', '2026-08-08'),
                         compact_evidence=True, evidence_preview_rows=1)
        binding = EventBinding(source.evidence_id, tuple(f'event-{i}' for i in range(count)))
        claim = Claim('N-C5', render_event(binding),
                      'supported_with_guardrail' if count else 'insufficient_evidence',
                      'high' if count else 'low', (source.evidence_id,), event_binding=binding)
        assert len(source.data['rows']) == count  # The caller has rows; the registry does not.
        assert registry.get(source.evidence_id).result['evidence_mode'] == 'compact_preview'
        assert not verify_event(claim, registry)
