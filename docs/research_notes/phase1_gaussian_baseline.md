# Phase 1 — Initial baselines (historical note)

## Original scope (superseded)

Phase 1 originally targeted a Gaussian-only baseline with host VaR/CVaR. Since then, the project has expanded well beyond this scope.

## Current implementation status

| Component | Status | Location |
|-----------|--------|----------|
| Gaussian sampler (GPU) | Done | `src/core/distributions/gaussian.cu` |
| Student-t sampler (GPU) | Done | `src/core/distributions/student_t.cu` |
| Host VaR / CVaR | Done | `src/wrappers/risk_metrics.cpp` |
| Drawdown / pain metrics (GPU) | Partial | `src/core/Drawdown-Pain/` |
| Exposure / leverage (GPU) | Partial | `src/core/Exposure-Leverage/` |
| Structural ruin (GPU) | Partial | `src/core/Structural-Ruin/` |
| Warning state | Done | `src/wrappers/risk_metrics.cpp` |
| Position sizing | Done | `src/algorithms/position_sizing.cpp` |
| SPD manifold ops (GPU) | Planned | `src/core/manifolds/spd_operations.cu` |

## Next priorities

See `project-plan-docs/07-RISK-SIMPLE-PLAN.md` for the current roadmap.
