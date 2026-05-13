# Black Swan sample benchmark

Synthetic **stress** replay for dashboard development. TailWarp (sample logic) triggers on
joint move in drawdown and exposure; the variance EWMA baseline uses the **same** return stream
with a fixed lag so lead time is positive in this scenario.

## Headline

| Field | Value |
|-------|-------|
| TailWarp first alert | 2026-01-05T09:00:00Z |
| Baseline first alert | 2026-01-07T15:00:00Z |
| Lead time | +54 h |

## Limitations

- Static CSV; not a live GPU run.
- Thresholds are illustrative only.
