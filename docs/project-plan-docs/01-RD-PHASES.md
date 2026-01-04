# R&D Phases and Gates (Long-Term Plan)

This document converts the roadmap into **phase gates** with clear "done" criteria.

---

## What is a "phase gate"?

A phase is **done** only when it produces:
- ✅ Working code (compiles, runs, no crashes)
- ✅ Validation evidence (checks pass, artifacts recorded)
- ✅ Performance evidence (baseline recorded, meets budget)
- ✅ Reproducible experiment artifacts (config + metrics + provenance)

**Use this as your "what should we do next?" map.**

---

## Phase 0 — Repo & Workflow Foundations

**Goal**: Make the repo capable of producing research artifacts reliably.

**Timeline**: 1–2 weeks

**Scope**:
- Build system (CMake, CUDA compilation)
- Experiment folder structure (see `../EXPERIMENTS.md`)
- Validation harness (see `../VALIDATION.md`)
- Performance measurement tools (see `06-PERFORMANCE-PROTOCOL.md`)

**Done when**:
- [ ] An experiment run writes a complete experiment folder with all required files
- [ ] Validation outputs are captured as `validation.json`
- [ ] Performance outputs are captured as `performance.json`
- [ ] You can run the benchmark protocol and get stable baseline numbers
- [ ] Checklists from `02-CHECKLISTS.md` are integrated into workflow

**Deliverables**:
- Working build system
- Experiment harness (scripts or minimal CLI)
- First experiment folder (even if just a dummy run)

**How to verify**: Run a trivial kernel (e.g., copy data), produce experiment folder, check all files are present.

## Phase 1 — Core Monte Carlo + Basic Risk Metrics

**Goal**: Establish the first trustworthy vertical slice (end-to-end).

**Timeline**: 2–3 weeks

**Scope**:
- Gaussian sampler (CUDA kernel)
- RNG wrapper (cuRAND)
- VaR and CVaR calculation (GPU)
- CPU reference implementation
- Single-position PnL distribution

**Done when**:
- [ ] Gaussian sampler passes Level 0–3 validation (sanity + invariants + statistical)
- [ ] VaR/CVaR pass invariant checks (CVaR >= VaR, monotonicity)
- [ ] GPU vs CPU comparison within tolerance (< 1% error)
- [ ] Baseline performance recorded: > 500M scenarios/sec for Gaussian on RTX 3060
- [ ] End-to-end experiment produces all artifacts
- [ ] At least 3 runs with different seeds show stable results

**Deliverables**:
- `gaussian_sampler.cu`
- `risk_metrics.cu` (VaR/CVaR kernels)
- CPU reference in `scripts/` or `src/reference/`
- Experiment config: `gaussian_varcvar.json`
- Research note: `docs/research_notes/phase1_gaussian_baseline.md`

**How to verify**: Use checklist from `02-CHECKLISTS.md` → "Adding a New Distribution Kernel" + "Adding a New Risk Metric"

## Phase 2 — Heavy Tails + EVT (POT)

**Goal**: Implement the "fat-tail" thesis with research-grade tail validation.

**Timeline**: 3–4 weeks

**Scope**:
- Student-t distribution (inverse CDF method)
- α-Stable distribution (CMS method, optional for later)
- POT/EVT estimation (Peaks-Over-Threshold on GPU)
- Tail-specific validation (tail index recovery, POT stability)

**Done when**:
- [ ] Student-t sampler passes Level 0–3 validation
- [ ] Tail validation implemented: log-log survival plot slope checks
- [ ] POT estimation kernel works and produces stable parameter estimates
- [ ] POT stability measured vs N (documented in artifacts)
- [ ] Threshold selection policy documented (fixed quantile vs adaptive)
- [ ] Comparison study: Gaussian vs Student-t VaR/CVaR with reproducible artifacts
- [ ] Performance: > 200M scenarios/sec for Student-t on RTX 3060
- [ ] VRAM usage stays under 10 GB for 100M scenarios

**Deliverables**:
- `student_t_sampler.cu`
- `pot_estimator.cu`
- Tail validation functions
- Experiment configs for multiple ν values
- Research note: "Gaussian vs Student-t: VaR underestimation in heavy tails"

**How to verify**: Run experiment from `04-RESEARCH-WORKFLOW.md` example, review using `05-EXPERIMENT-REVIEW.md` (aim for Level 2)

## Phase 3 — Scenario Engines and Path-Dependent Risk

**Goal**: Move from iid returns to time/process scenarios.

**Timeline**: 4–6 weeks

**Scope**:
- Correlated multi-asset paths (Cholesky decomposition)
- Geometric Brownian Motion (GBM) path generator
- Drawdown calculation (parallel prefix scan)
- Optional: Hawkes process (microstructure), regime switching (HMM)

**Done when**:
- [ ] Multi-asset path generator works with configurable correlation matrix
- [ ] Drawdown metric implemented with invariants (>= 0, monotonic)
- [ ] Path-based validation: check correlation recovery, path continuity
- [ ] Process parameters recorded in experiment artifacts
- [ ] Diagnostic artifacts produced (correlation matrices, path samples, event counts)
- [ ] Performance acceptable for multi-asset (e.g., 10 assets, 1000 timesteps, 1M paths)

**Deliverables**:
- `gbm_path_generator.cu`
- `drawdown_calculator.cu`
- Optional: `hawkes_process.cu`
- Multi-asset experiment configs
- Research note: "Path-dependent risk: drawdown under correlated shocks"

**How to verify**: Generate correlated paths, verify correlation matrix recovery, check drawdown invariants, compare to CPU reference

## Phase 4 — Broad Risk Coverage (Multi-Asset, Instruments, Use Cases)

**Goal**: Expand risk computation across asset types and instrument logic while keeping the same harness.

**Timeline**: Ongoing (add incrementally)

**Scope** (pick and choose based on research needs):
- **Portfolio aggregation**: weighted PnL, portfolio VaR/CVaR
- **Options/derivatives**: Black-Scholes pricing, Greeks, PnL scenarios
- **FX/crypto**: jump-diffusion, regime switching, high volatility
- **Scenario analysis**: stress testing, tail scenarios, what-if analysis
- **Copulas**: tail dependence (t-copula, Gaussian copula)

**Done when** (for each new target):
- [ ] Data schema defined and documented
- [ ] Pricing/PnL logic implemented and validated
- [ ] Sign conventions documented (profit vs loss, returns vs prices)
- [ ] Validation invariants defined (no-arbitrage, Greeks sanity, etc.)
- [ ] Sample experiment configs created
- [ ] Performance impact measured vs baseline
- [ ] Research note or example produced

**Deliverables** (incremental):
- Instrument-specific kernels (e.g., `black_scholes_pricer.cu`)
- Portfolio aggregation logic
- Copula samplers
- Experiment configs for each use case
- Research notes demonstrating each capability

**How to verify**: Use checklist from `02-CHECKLISTS.md` → "Adding Support for a New Asset/Instrument Type"

## Phase 5 — Optimization & Research Extensions

**Goal**: Make the framework a research platform for optimization and algorithm exploration.

**Timeline**: Long-term (after Phases 1–3 are solid)

**Scope**:
- Gradient descent on GPU (batched)
- Risk-constrained optimization (minimize CVaR, maximize Sharpe)
- Geometric optimization (manifold descent for covariance matrices)
- Optional: RL integration (parallel environment stepping)

**Done when**:
- [ ] Optimization kernels implemented and validated
- [ ] Convergence diagnostics captured (loss history, gradient norms)
- [ ] Constraints validated (e.g., CVaR limit respected)
- [ ] Inner-loop performance benchmarked (iterations/sec)
- [ ] Optimization outputs include: final parameters, convergence plot, validation report
- [ ] At least one research use case demonstrated (e.g., optimal position sizing under tail risk)

**Deliverables**:
- `gradient_descent.cu`
- `geometric_optimizer.cu` (optional)
- Optimization validation functions
- Research note: "Optimal position sizing under CVaR constraints"

**How to verify**: Run optimization, check constraints are satisfied, verify convergence, compare to CPU optimizer

## Guidance on choosing "what's next"

### Decision framework:

**Prefer work that improves**:
1. **Measurement** → better experiment tracking, better benchmarks, better diagnostics
2. **Trust** → stronger validation evidence, more rigorous checks, reproducibility
3. **Capability** → new distribution/process, new risk metric, new asset target

**Avoid**:
- Adding complexity that can't be validated or benchmarked yet
- Building features without a clear research question
- Skipping validation to "move faster"

### Priority matrix:

| Priority | What to build | Why |
|----------|---------------|-----|
| **High** | Validation/benchmarking infrastructure | Enables everything else |
| **High** | Core distributions (Gaussian, Student-t) | Foundation for all risk work |
| **Medium** | Additional risk metrics (drawdown, POT) | Expands research capability |
| **Medium** | Multi-asset / portfolio support | Common use case |
| **Low** | Exotic distributions (until needed) | Add when research demands |
| **Low** | Optimization / RL | Only after core is solid |

### When in doubt:

1. **Check Phase gates**: Are you done with the current phase?
2. **Check validation**: Can you validate what you're building?
3. **Check research value**: Will this enable a paper/demo/learning content?

If the answer to all three is "yes", proceed. Otherwise, finish current work first.

---

## Phase transition checklist

Before moving to the next phase:

```
[ ] All "done when" criteria met for current phase
[ ] All deliverables produced and committed
[ ] Experiment artifacts archived and indexed
[ ] Research notes written and reviewed
[ ] Performance baselines recorded
[ ] No known validation failures
[ ] Checklists from 02-CHECKLISTS.md completed
```

**Don't rush phases**. A solid foundation is worth the time investment.


