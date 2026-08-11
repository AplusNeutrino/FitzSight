# Implementation Status

**Version:** v0.1  
**Date:** 2026-08-11  
**Phase:** Synthetic Data + Baseline Analytics

## Completed

- [x] Repository scaffold
- [x] Deterministic synthetic data generator
- [x] Customers / salespeople / sales activity / deposits / withdrawals / trades / business events
- [x] `CRM_ROUTING_CHANGE` anomaly injection
- [x] KPI helpers
- [x] Baseline before/after investigation
- [x] Evidence registry primitive
- [x] Tests
- [x] Data dictionary
- [x] CLI generation and baseline scripts

## Next P0 slice

1. DuckDB read-only SQL tool.
2. Schema inspection tool.
3. Evidence IDs for every tool execution.
4. Period-comparison tool.
5. Statistical-test tool.
6. Investigation-plan data model.
7. Deterministic autonomous investigation workflow.
8. Only then add the LLM orchestration layer.

## Next Definition of Done

```bash
python scripts/investigate.py --question "Why did European FTD conversion deteriorate after July 15?"
```

should produce a structured, evidence-linked result without relying on an LLM for arithmetic.
