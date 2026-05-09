# TailWarp Improvement Roadmap (Verified Against Codebase)

## 1) Executive Context

This roadmap was built by validating the repository implementation against `sugestions.md`.

Key finding: the existing suggestion map targets **LLM serving tail-latency optimization** (TTFT/ITL/KV cache/vLLM/TGI), while this repository is a **CUDA/C++ quantitative risk engine** for fat-tail simulation and risk metrics.

Therefore, most original suggestions are **not applicable** to the current product scope.  
This document replaces that map with a **domain-correct, execution-ready roadmap** from engineering + project management perspectives.

---

## 2) Current State (Code-Verified)

### 2.1 Implemented Capabilities
- GPU samplers: `src/core/distributions/student_t.cu`, `src/core/distributions/gaussian.cu`
- Risk modules (mostly CUDA kernels):  
  - `src/core/Drawdown-Pain/*`
  - `src/core/Structural-Ruin/*`
  - `src/core/Exposure-Leverage/exposure_metrics.cu`
- Host wrappers: `src/wrappers/distributions.cpp`, `src/wrappers/risk_metrics.cpp`
- Algorithms: `src/algorithms/position_sizing.cpp`, `src/algorithms/robust_covariance.cpp`
- Experiment runner and artifact output: `examples/experiment_run.cpp`
- Test suites present: `tests/unit/*`, `tests/validation/statistical_tests.cpp`, `tests/integration/test_end_to_end.cpp`

### 2.2 Confirmed Gaps and Risks
- Domain mismatch in prior roadmap (LLM-serving assumptions do not fit codebase)
- Docs-code drift in scripts/benchmarks instructions:
  - `benchmarks/README.md` references non-existing `scripts/run_benchmarks.sh`
  - `scripts/README.md` references missing files (`clean.sh`, `compare_gpu_cpu.py`, `generate_config.py`, `plot_results.py`)
- Mathematical placeholder implementations:
  - `src/core/manifolds/spd_operations.cu` (`spd_log_kernel`, `spd_distance_kernel` TODO/placeholder)
- Simplified covariance estimator:
  - `src/algorithms/robust_covariance.cpp` ignores `max_iter` and `tol`
- Test coverage is narrow relative to implemented module surface:
  - limited direct verification for many Drawdown/Structural-Ruin/Exposure kernels
- No automated performance regression gate in CI

---

## 3) Verification Matrix for `sugestions.md`

Status legend: `Implemented`, `Partially Implemented`, `Missing`, `Not Applicable`.

### Phase 1 (Measurement & Foundations)
- Per-token/TTFT/ITL latency tracking -> `Not Applicable`
- P50/P95/P99 request latency -> `Not Applicable`
- GPU utilization metrics -> `Missing` (no telemetry for utilization)
- Synthetic workload generator -> `Partially Implemented` (experiment config + sampling workflows exist, not serving traffic workloads)
- Real trace replay (ShareGPT) -> `Not Applicable`
- vLLM/TGI/TensorRT/HF baseline comparison -> `Not Applicable`

### Phase 2 (Optimization Techniques)
- KV-cache/PagedAttention/sliding window/eviction -> `Not Applicable`
- Serving scheduler features (continuous batching, prefill/decode split) -> `Not Applicable`
- CUDA memory pooling/allocator strategy -> `Missing`
- Model weight/activation quantization for LLM inference -> `Not Applicable`

### Phase 3 (Formal Modeling)
- Queueing/SLO latency models -> `Not Applicable`
- Roofline and compute-vs-memory performance modeling -> `Missing` (useful and applicable to this domain)
- Cost model by token latency -> `Not Applicable`

### Phase 4 (System Integration)
- vLLM/TGI plugin/proxy mode -> `Not Applicable`
- Bayesian auto-tuning of system configs -> `Missing` (adaptable to risk-kernel parameter tuning)
- Multi-GPU/multi-node support -> `Missing` (applicable for large scenario sets)
- Health checks/Prometheus/A-B rollout -> `Partially Applicable` (if productized service/API is planned)

---

## 4) Product Direction (Recommended)

Replace LLM-latency roadmap with these strategic tracks:

1. **Correctness-first scientific engine**  
   Complete missing math fidelity and robust statistical validation.
2. **Performance-trust platform**  
   Reproducible benchmark pipeline + regression budgets.
3. **Research-to-production pathway**  
   Stable experiment schemas, deterministic artifacts, optional service boundary.
4. **Scale readiness**  
   Memory/runtime optimization and multi-GPU planning.

---

## 5) Detailed Delivery Roadmap

## Epic A - Repository Truth and Operational Hygiene
**Goal:** eliminate docs-code drift and make all instructions executable.

### Work Items
- A1. Reconcile `scripts/README.md` with actual script inventory
- A2. Reconcile `benchmarks/README.md` with implemented benchmark tooling
- A3. Add CI check for missing internally referenced files
- A4. Standardize build/test/run commands in `README.md`

### File Touchpoints
- `README.md`
- `scripts/README.md`
- `benchmarks/README.md`
- `.github/workflows/*` (or equivalent CI config)

### Tests/Validation
- Link/reference check for docs
- Script existence check in CI
- Smoke command verification on clean workspace

### Acceptance Criteria
- No broken internal references in docs
- Every command in READMEs executes successfully on a clean machine
- CI fails when docs reference non-existing files/scripts

### Risks
- Hidden local environment assumptions
- Platform-specific script compatibility

### Dependencies
- None

---

## Epic B - Correctness Hardening for Existing Risk Modules
**Goal:** ensure every implemented metric/module has deterministic and statistical validation.

### Work Items
- B1. Add direct tests for all Drawdown-Pain kernels
- B2. Add direct tests for all Structural-Ruin kernels
- B3. Add direct tests for Exposure-Leverage kernels
- B4. Add CPU reference checks where feasible (golden fixtures)
- B5. Add edge-case tests (degenerate series, tiny N, extreme values, barriers)

### File Touchpoints
- `src/core/Drawdown-Pain/*`
- `src/core/Structural-Ruin/*`
- `src/core/Exposure-Leverage/*`
- `tests/unit/*`
- `tests/validation/*`

### Tests/Validation
- Kernel-level unit tests
- GPU vs CPU parity tests with tolerance thresholds
- Statistical sanity checks across multiple seeds/distributions

### Acceptance Criteria
- Every production kernel has at least one direct correctness test
- Parity thresholds documented and enforced in CI
- No known NaN/Inf regressions in critical paths

### Risks
- Floating-point non-determinism across architectures
- Brittle thresholds without robust tolerance strategy

### Dependencies
- Epic A recommended first

---

## Epic C - Benchmarking and Performance Regression Guardrails
**Goal:** establish repeatable performance baselines and automated regression alerts.

### Work Items
- C1. Implement benchmark runners currently documented but missing
- C2. Define canonical benchmark scenarios for each kernel family
- C3. Record baseline JSONs by hardware profile
- C4. Add CI performance gate (warn/fail by threshold)
- C5. Add benchmark report artifact publishing

### File Touchpoints
- `benchmarks/configs/*`
- `benchmarks/baselines/*`
- `benchmarks/results/*` (generated)
- `scripts/*` (benchmark entrypoints)
- CI workflow files

### Tests/Validation
- Repeated benchmark runs (variance envelope)
- Baseline comparison test
- Performance trend snapshots over commits

### Acceptance Criteria
- One-command benchmark execution from clean checkout
- Baselines versioned and reproducible
- CI surfaces regression signal with clear diagnostics

### Risks
- Hardware noise causing false positives
- Benchmark drift from changing workloads

### Dependencies
- Epic B preferred before strict performance gates

---

## Epic D - Mathematical Fidelity Upgrade
**Goal:** replace placeholders/simplifications with research-grade implementations.

### Work Items
- D1. Implement true SPD log map in `spd_log_kernel`
- D2. Implement true affine-invariant SPD distance in `spd_distance_kernel`
- D3. Upgrade `estimate_robust_covariance` to actual robust iterative estimator
- D4. Respect `max_iter`/`tol` and expose convergence diagnostics
- D5. Add numeric stability and convergence tests

### File Touchpoints
- `src/core/manifolds/spd_operations.cu`
- `src/algorithms/robust_covariance.cpp`
- corresponding headers and tests

### Tests/Validation
- Analytical small-case validation vs trusted CPU reference
- Convergence tests (iteration count, tolerance behavior)
- Stability tests under ill-conditioned covariance inputs

### Acceptance Criteria
- No placeholder TODOs in core math path
- Convergence controls active and test-covered
- Error bounds documented for representative workloads

### Risks
- Numerical instability in poorly conditioned matrices
- Performance hit from mathematically correct kernels

### Dependencies
- Epic B test scaffolding
- Epic C benchmark harness for perf impact tracking

---

## Epic E - Experiment Platform and Reproducibility
**Goal:** make experiments traceable, comparable, and automation-ready.

### Work Items
- E1. Version experiment artifact schema (`manifest.json`, `metrics.json`, etc.)
- E2. Add schema validation tests and backward compatibility checks
- E3. Expand metadata capture (runtime, seed policy, precision mode)
- E4. Add experiment index/summary generator for portfolio comparisons
- E5. Define experiment lifecycle SOP (run, validate, review, archive)

### File Touchpoints
- `examples/experiment_run.cpp`
- `scripts/validate_experiment.py`
- `docs/EXPERIMENTS.md`
- `docs/VALIDATION.md`

### Tests/Validation
- Schema validation test suite
- Replayability checks using fixed configs/seeds
- Artifact integrity checks (required files + checksum optional)

### Acceptance Criteria
- Repeatable runs produce structurally identical artifacts
- Validation script enforces schema contract
- Experiment review can be completed from artifacts alone

### Risks
- Schema churn across fast iteration cycles
- Backward compatibility overhead

### Dependencies
- Epic A for documentation consistency

---

## Epic F - Scale and Runtime Optimization
**Goal:** prepare for larger scenario volumes and tighter compute budgets.

### Work Items
- F1. Introduce memory allocation strategy (pooling/reuse) for hot paths
- F2. Add stream-based concurrency where beneficial
- F3. Evaluate batch partitioning and multi-GPU decomposition strategy
- F4. Add roofline-style performance characterization docs and scripts
- F5. Add adaptive execution presets by hardware tier

### File Touchpoints
- `src/core/*` hot kernels
- wrapper orchestration files in `src/wrappers/*`
- benchmark scripts/configs
- performance docs under `docs/project-plan-docs/*`

### Tests/Validation
- Throughput/latency microbenchmarks
- Memory footprint tracking
- Cross-GPU comparability tests (when available)

### Acceptance Criteria
- Measurable throughput improvement on reference GPU
- Stable memory behavior at target sample scales
- Runtime profile published per release

### Risks
- Added complexity in runtime orchestration
- Hardware-dependent optimizations reducing portability

### Dependencies
- Epic C strongly recommended first

---

## 6) Quarter-Level Sequencing (Suggested)

### Q1 (Foundation)
- Epic A -> Epic B
- Start Epic C benchmark runner implementation

### Q2 (Trust and Fidelity)
- Complete Epic C regression gate
- Execute Epic D mathematical fidelity upgrades

### Q3 (Platformization)
- Execute Epic E experiment schema + automation
- Begin Epic F runtime optimization and scale strategy

### Q4 (Optional Productization)
- If external service/API is planned: add observability endpoints, health/readiness, and deployment SLO policy

---

## 7) PM Execution Model

### 7.1 Roles
- Tech Lead: architecture decisions, risk acceptance, phase-gate signoff
- Quant/Research Engineer: model correctness and statistical validity
- GPU Engineer: kernel/runtime performance and memory strategy
- QA/Validation: deterministic and statistical test governance

### 7.2 Governance Cadence
- Weekly engineering sync: progress vs epic goals
- Biweekly validation review: test flakiness, numerical stability
- Monthly performance review: benchmark trends and regressions
- Phase exit review: acceptance criteria checklist signoff

### 7.3 Tracking Artifacts
- Epic board with statuses: `Backlog`, `In Progress`, `Blocked`, `Ready for Validation`, `Done`
- Risk register: issue, impact, mitigation, owner
- Decision log: rationale for major math/performance trade-offs

---

## 8) Definition of Done (Cross-Epic)

A workstream is complete only if all are true:
- Code implemented and peer-reviewed
- Tests added/updated and passing in CI
- Benchmark impact documented (if performance-sensitive)
- Docs updated to match shipped behavior
- Acceptance criteria explicitly met and recorded

---

## 9) Stretch Opportunities (If Capacity Allows)

- Add EVT/POT module for explicit tail modeling and stress extrapolation
- Add richer calibration datasets and scenario libraries
- Add lightweight Python bindings for analytics workflow adoption
- Add reproducible report generation for paper/technical note output

---

## 10) Immediate Next 10 Tasks (Actionable Starter List)

1. Fix script/readme drift in `scripts/README.md`
2. Fix benchmark/readme drift in `benchmarks/README.md`
3. Add CI doc reference integrity check
4. Add direct unit tests for `maximum_drawdown.cu`
5. Add direct unit tests for `ulcer_index.cu`
6. Add direct unit tests for `survival_probability.cu`
7. Add direct unit tests for `solvency_distance.cu`
8. Add direct unit tests for `exposure_metrics.cu`
9. Replace placeholder logic in `spd_log_kernel`
10. Upgrade `estimate_robust_covariance` to use iterative robust method

This sequence provides immediate reduction in project risk while preserving momentum toward mathematically sound, performant, and reproducible research tooling.
