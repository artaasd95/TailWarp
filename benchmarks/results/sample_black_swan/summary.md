# Black Swan sample benchmark

Synthetic **stress** replay. TailWarp triggers on warning-state composite score;
the variance EWMA baseline uses the **same** return stream.

## Headline

| Field | Value |
|-------|-------|
| Scenario | sample_stress_2026q1 |
| TailWarp first alert | 2026-01-05T09:00:00Z |
| Baseline first alert | 2026-01-07T15:00:00Z |
| Lead time | +54.0 h |

## Limitations

- CPU-only replay path; CUDA reproduction may differ on GPU-sorted CVaR.
- Student-t scenario refresh optional and disabled in default config.
- Thresholds are deterministic per docs/VALIDATION.md (S2-02).
