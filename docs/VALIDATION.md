# Validation strategy

TailWarp uses **layered validation** before results are trusted. Aligns with [project-plan-docs/QUICK-REFERENCE.md](project-plan-docs/QUICK-REFERENCE.md).

## Levels

| Level | What | When |
|-------|------|------|
| **0** | Sanity: no NaN/Inf, array lengths, basic bounds | Always |
| **1** | Unit tests: small deterministic inputs | Always (CI) |
| **2** | Invariants: monotonicity, ordering (e.g. CVaR vs VaR) | Before claiming a metric works |
| **3** | Statistical: moments, tail behavior vs theory | Distributions and heavy tails |
| **4** | End-to-end: config → run → artifact folder | Before publishing or sharing numbers |

**Minimum to call code “working”:** levels **0–2** pass.

## Artifact validation

`scripts/validate_experiment.py` checks that an experiment directory contains the required files and that JSON parses. Stricter schema checks can be added as fields stabilize.

## Risk-metric checks (examples)

- **CVaR:** For a fixed sample, CVaR at higher confidence (e.g. 99%) is no greater (algebraically) than at 95% when measuring the same lower tail convention as in unit tests.  
- **Student-t samples:** No NaN/Inf; sample mean and variance loosely consistent with \(\nu / (\nu-2)\) for \(\nu > 2\) at large \(N\).  
- **GPU vs CPU:** Where both exist, compare tail statistics within tolerance.

## Phase gates

Phase completion criteria in [project-plan-docs/01-RD-PHASES.md](project-plan-docs/01-RD-PHASES.md) require validation evidence in **`validation.json`** inside each experiment folder.

## Running tests

Preferred (CMake + GTest):

```bash
cmake -B build -DBUILD_TESTS=ON
cmake --build build
ctest --test-dir build --output-on-failure
```

The root `Makefile` may also delegate to this flow; see [Makefile](../Makefile).
