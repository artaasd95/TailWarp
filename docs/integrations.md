# TailWarp integrations appendix (v1.0 prep)

**v1.0 ships no live cross-repo wiring.** This document defines consumer contracts for **v2.0 OPT-INTEG** mock adapters.

## RADA — `TailwarpOptimizerAdapter` (deferred)

```python
# Mock v2.0 — not wired in v1.0
from tailwarp import TailWarpClient

class TailwarpOptimizerAdapter:
    def __init__(self) -> None:
        self._client = TailWarpClient()

    def max_size_for_tail_budget(
        self,
        max_cvar_limit: float,
        price: float,
        nu: float = 4.0,
    ) -> float:
        r = self._client.compute_position_size(max_cvar_limit, price, nu=nu)
        return r.optimal_size
```

Enables RADA **SP-CALC-05** in v2.0.

## raft-lm — `engine_labels` metadata (deferred)

```python
# Mock metadata passthrough for audit trails
def tailwarp_engine_labels(client: TailWarpClient) -> dict:
    return {
        "tailwarp_version": "1.0.0",
        "backend": "native" if client.has_native else "numpy",
        "measurement_class": "cpu_sample",
    }
```

Enables RADA `RaftAuditorAdapter` live path when raft-lm **SP-TOOLS** (RAFT-19–22) lands.

## scenario-reasoner — verifier hook (deferred)

```python
from tailwarp import TailWarpClient, WarningStateParams

def verify_scenario_tail(returns: list[float], params: WarningStateParams) -> dict:
    client = TailWarpClient()
    return {
        "cvar_95": client.compute_cvar(returns, alpha=0.95).value,
        "warning": client.compute_warning_state(params).to_dict(),
    }
```

Enables RADA `ScenarioReasonerAdapter` when scenario-reasoner **SP-SERVE** (SR-09–14) lands.

## Dependency map (prep only)

```
TailWarp SP-PYAPI (v1.0)
    └─> RADA SP-CALC-05, scenario SP-VERIFY-05 (v2.0)
raft-lm SP-TOOLS
    └─> RADA RaftAuditorAdapter (v2.0)
scenario-reasoner SP-SERVE
    └─> RADA ScenarioReasonerAdapter (v2.0)
```

No claim of live integration in v1.0 releases.
