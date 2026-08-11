# FitzSight v0.7 Benchmark Scenarios

The v0.7 catalog reaches the planned five-scenario initial benchmark target. All data are synthetic and deterministic under the default seed.

## 1. CRM routing / FTD deterioration

Region: Europe.  
Signal: response latency rises in Team A/B after 2026-07-15; FTD conversion falls.  
Expected Agent behavior: compare affected/control cohorts, test significance, decompose team contributions, inspect event context, retain a causal guardrail.

## 2. High-value withdrawal cluster / net-deposit deterioration

Region: Europe.  
Signal: 11 high-value customers create concentrated current-week withdrawal pressure.  
Expected Agent behavior: reconstruct net-deposit movement, quantify concentration, compare regional controls, avoid inventing withdrawal motives.

## 3. Customer Intelligence

Region: Europe.  
Signal: observable deposits/trades/withdrawals support a transparent behavioral-value segmentation.  
Expected Agent behavior: create descriptive segments without reading `customer_segment_gt` or converting the result into credit/AML/adverse-action decisions.

## 4. Paid-media volume vs acquisition quality

Region: Americas.  
Window: 2026-06-01–14 vs 2026-06-15–28.  
Signal: lead volume and Paid Search share rise sharply while Paid Search conversion quality deteriorates.

Default-seed result:

```text
baseline leads:          266
current leads:         1,104
lead-volume change:      +838 (+315.0%)
aggregate FTD change:   -10.84 pp
Paid Search mix change: +60.52 pp
Paid Search FTD change: -16.44 pp
Paid Search p-value:     4.43e-05
```

The benchmark explicitly distinguishes:

- **volume effect** — more leads;
- **mix effect** — much larger Paid Search share;
- **within-channel performance** — Paid Search conversion deterioration.

## 5. False-correlation trap

Region: Asia.  
Window: 2026-07-06–19 vs 2026-07-20–08-02.  
Tempting event: office relocation on 2026-07-20.  
Actual observable driver pattern: Affiliate conversion quality deterioration.

Default-seed result:

```text
Asia FTD change:        -8.13 pp
Affiliate FTD change:  -15.81 pp
Affiliate p-value:      0.00463
top negative within-channel performance effect: Affiliate
nearby office-event causal support: false
false correlation rejected: true
```

The benchmark passes only if FitzSight sees the nearby event **and refuses to promote temporal proximity into a causal claim**.

## Evaluation policy

A scenario passes only when:

1. the expected analytical direction/status is recovered;
2. final verification passes;
3. all factual claims contain Evidence IDs;
4. the verifier reports no policy violations.
