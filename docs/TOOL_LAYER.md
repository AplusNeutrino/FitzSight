# FitzSight v0.2 Tool Layer

## Schema Inspector

Purpose: expose the tables and columns that an investigation is allowed to reason about.

Current output:

- backend;
- table names;
- column names;
- data types;
- nullable metadata where the backend exposes it.

## Read-only SQL Tool

Purpose: execute bounded analytical SQL while rejecting obvious mutation, configuration, file-access, and multi-statement paths.

Accepted first statement classes:

- `SELECT`
- `WITH`

Rejected classes include:

- INSERT / UPDATE / DELETE / MERGE;
- CREATE / DROP / ALTER / REPLACE / TRUNCATE;
- ATTACH / DETACH;
- COPY / EXPORT / IMPORT;
- INSTALL / LOAD;
- PRAGMA / SET / RESET;
- external readers and scan functions.

The Tool wraps approved queries with a row limit and registers success/error evidence.

## KPI Tool

Canonical metrics currently implemented:

- `ftd_conversion_rate`
- `total_deposits`
- `total_withdrawals`
- `trading_volume`

The KPI Tool calls the SQL Tool rather than directly reading DataFrames, so numeric results preserve a query evidence chain.

## Period Comparison Tool

Runs the same KPI definition for a baseline and current filter, then reports:

- current value;
- baseline value;
- absolute change;
- relative percentage change;
- source Evidence IDs.

## Statistical Test Tool

Implemented:

- two-proportion z-test plus equivalent uncorrected 2×2 chi-square diagnostic;
- 95% CI for difference in proportions;
- Mann–Whitney U;
- Welch independent-samples t-test.

## Evidence Registry

Tools return a `ToolResult` containing an Evidence ID. The registry stores the Tool parameters, result digest, status, and compact result.

## v0.2 security boundary

This layer is intentionally read-only and local. It is not an enterprise sandbox. Future deployment hardening should additionally rely on:

- database-level read-only credentials;
- isolated service accounts;
- network egress control;
- query timeouts / resource quotas;
- audit storage outside the Agent process;
- PII classification and access control.

## v0.6 compact SQL evidence mode

Customer segmentation needs the full synthetic European customer feature matrix for computation, but shipping thousands of raw rows inside every Agent audit payload would make the demo unnecessarily large.

`ReadOnlySQLTool.run()` therefore supports an explicit `compact_evidence=True` mode:

- the caller receives the full bounded query result for deterministic computation;
- the Evidence Registry stores query metadata, row count, a bounded row preview, backend, and a digest of the full result;
- the Evidence ID/digest/status chain remains verifier-compatible;
- the normal SQL safety policy remains unchanged.

The v0.6 customer-intelligence feature query uses this mode. The fixed-seed Agent sample drops from multi-megabyte raw-row evidence to a compact audit payload while preserving the executed query and full-result digest.
