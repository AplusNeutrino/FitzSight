# Customer Intelligence / Behavioral Segmentation

## Purpose

FitzSight v0.6 adds a deterministic customer-intelligence capability without turning the Agent into a credit, AML, suitability, or adverse-action system.

Supported demo question:

```text
How are European customer segments distributed by behavioral value, and which segment contributes most to deposits?
```

The normal Agent never queries the synthetic benchmark field `customer_segment_gt`.

## Observable features

`CustomerSegmentationTool` aggregates only operational fields that are visible to the analytical system:

- completed deposit count and value;
- completed withdrawal count and value;
- trading count and volume;
- region, acquisition channel, and assigned team for descriptive context.

The feature query is executed through the existing read-only SQL tool and therefore inherits:

- SELECT/WITH-only policy;
- blocked write/admin/external-scan keywords;
- bounded row output;
- append-only evidence registration.

## Method: `behavioral_value_score_v1`

Customers with no completed deposit, withdrawal, or trade activity are assigned to `Low Activity`.

For active customers, FitzSight computes within-cohort percentile ranks:

```text
value_score =
    0.55 × deposit-value percentile
  + 0.30 × trade-volume percentile
  + 0.15 × trade-count percentile
```

Approved value bands:

```text
High Value   score >= 0.75
Growth       0.50 <= score < 0.75
Core         score < 0.50 among active customers
Low Activity no completed deposit / withdrawal / trade activity
```

This policy is deliberately transparent and reproducible. It is a descriptive business-analysis segmentation, not a prediction of customer risk or future behavior.

## Default synthetic Europe result

Using the fixed benchmark seed:

| Segment | Customers | Customer share | Deposit share | Withdrawal share | Net deposits |
|---|---:|---:|---:|---:|---:|
| High Value | 252 | 3.7% | 53.7% | 63.7% | $2,054,709.70 |
| Growth | 440 | 6.5% | 33.4% | 26.8% | $1,401,103.92 |
| Core | 732 | 10.8% | 12.9% | 9.5% | $548,265.20 |
| Low Activity | 5,346 | 79.0% | 0.0% | 0.0% | $0.00 |

Total European customers segmented: **6,770**. Coverage: **100%**.

The `High Value` group contains about 3.7% of customers but accounts for about 53.7% of completed European deposits in the current fixed-seed synthetic dataset.

## Evidence boundary

The system may state:

- observed deposit concentration;
- observed withdrawal concentration;
- descriptive segment-level trading activity;
- transparent score inputs and thresholds.

The system must not infer from these segments alone:

- suspicious behavior;
- AML status;
- creditworthiness;
- investment suitability;
- eligibility for a product;
- whether a customer should be restricted, contacted, frozen, or treated adversely.

Human review and a separately authorized decision system would be required for any high-impact action.
