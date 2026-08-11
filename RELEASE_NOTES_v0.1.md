# FitzSight v0.1 Release Notes

Date: 2026-08-11

## Purpose

The first implementation slice follows the master plan's instruction to build the synthetic data and prove the ground-truth anomaly is analytically detectable **before adding an Agent**.

## Included

- repository scaffold;
- deterministic synthetic financial-operations generator;
- customers, salespeople, sales activity, deposits, withdrawals, trades, business events;
- CRM routing change benchmark scenario;
- KPI helpers;
- deterministic baseline investigation;
- statistical comparison for conversion shift;
- evidence-registry primitive;
- data dictionary;
- automated tests;
- implementation-status document;
- full `MASTER_PLAN.md`.

## Validated

`pytest -q` passes all current tests.

The current benchmark detects:

- affected conversion deterioration;
- affected response-time increase;
- a stronger affected-cohort shift than the control cohort;
- a statistically significant conversion shift in the affected cohort.

## Deliberately deferred

- DuckDB / SQL tool layer;
- schema-inspection tool;
- evidence-wrapped tool execution;
- investigation plan model;
- autonomous investigation workflow;
- LLM orchestration;
- Streamlit UI.

The next version should implement the Tool Layer before any LLM integration.
