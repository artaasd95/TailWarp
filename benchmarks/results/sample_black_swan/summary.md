# Black Swan benchmark — sample_stress_2026q1

Synthetic **stress** replay. TailWarp triggers on warning-state composite score;
the variance EWMA baseline uses the **same** return stream.

## Headline

| Field | Value |
|-------|-------|
| Measurement | cpu_sample |
| Scenario | sample_stress_2026q1 |
| K runs | 1 |
| Aggregation | single_run |
| TailWarp first alert | 2026-01-05T09:00:00Z |
| Baseline first alert | 2026-01-07T15:00:00Z |
| Lead time | +54.0 h |

| Convexity score | -0.699029 |
| Antifragility posture | fragile |
| Complexity regime | stable |
| Posture status | cpu_replay_heuristic |

## Limitations

- Thresholds are deterministic per docs/VALIDATION.md (S2-02).
- Posture metrics use CPU replay heuristics until Lens-5 kernels ship.
- SPD / robust covariance excluded from headline rows.
