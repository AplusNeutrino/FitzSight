# FitzSight — Demo Video Script

Target length: **90–150 seconds**.

## Recording sequence

### 0:00–0:10 — Opening

Show the FitzSight title and state the problem:

> “Financial teams already have dashboards and SQL. FitzSight answers the harder question: why did this metric change, and what evidence supports the explanation?”

### 0:10–0:30 — Ask the question

Use the CRM / FTD benchmark:

> “Why did European FTD conversion deteriorate after July 15?”

Show the constrained planner and the approved investigation trace.

### 0:30–0:55 — Business result

Show KPI cards and the contribution chart. Highlight:

- affected FTD change;
- Europe control;
- response-time change;
- largest negative team contribution;
- verified-claim count.

### 0:55–1:20 — Evidence

Open at least two Evidence cards:

- one read-only SQL result;
- one statistical / contribution result.

Show Evidence IDs and result digests.

### 1:20–1:40 — Verifier and guardrail

Show `verified`, explain that important claims must reference evidence, and show the causal-language guardrail.

### 1:40–2:00 — Safety / reliability

Briefly show the false-correlation scenario or adversarial result and state:

> “Planner output is untrusted. The Agent cannot execute trades, freeze accounts, or turn temporal proximity into a causal conclusion.”

### 2:00–2:15 — Close

Show the architecture line:

**Question → Data → Analysis → Evidence → Decision**

Mention the five-scenario benchmark and MIT open-source repository.

## Recording requirements

- Record an actual FitzSight runtime when possible; do not fake tool-call animation.
- Keep browser zoom stable and Evidence IDs readable.
- Hide environment variables, API keys, terminal history containing secrets, personal browser tabs, and notifications.
- Keep a local copy and a second backup copy.
- If Streamlit is unavailable, record the deterministic CLI and use `FitzSight_Offline_Demo.html` as the visual backup.
