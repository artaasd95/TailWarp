# TailWarp Improvement Roadmap (Verified Against Codebase)

## 1) Executive Context

This roadmap was built by validating the repository implementation against `sugestions.md`.

Key finding: the existing suggestion map targets **LLM serving tail-latency optimization** (TTFT/ITL/KV cache/vLLM/TGI), while this repository is a **CUDA/C++ quantitative risk engine** for fat-tail simulation and risk metrics.

Therefore, most original suggestions are **not applicable** to the current product scope.  
This document replaces that map with a **domain-correct, execution-ready roadmap** from engineering + project management perspectives.

---

## 1a) Portfolio North Star (Resume / Hiring Signal)

This project is positioned as a **high-signal technical showcase**, not a feature warehouse. The roadmap below is intentionally biased toward **reproducible numbers**, **fair baselines**, and a **defensible “why we win (or tie)” story**—including an optional **arXiv-style technical report** if you want a credential that survives a skeptical reviewer or hiring manager.

### Principle: depth over breadth

- Prefer **one benchmark table nobody can dismiss** over ten half-finished modules.
- Prefer **documented methodology** (hardware, build flags, seeds, warm-up, statistical aggregation) over ad-hoc “it felt faster.”
- Prefer **honest deltas** (we match CPU reference; we beat library X on workload Y because Z) over vague “state-of-the-art” claims.

### Tier A — “Good portfolio” (credible, not exceptional)

What a reviewer should conclude: *this person ships real C++/CUDA and cares about correctness.*

| Evidence | Acceptable bar |
|----------|----------------|
| Repo hygiene | Builds from README; tests pass; no broken doc commands |
| Correctness story | Tests + at least one CPU/GPU or reference check on a hot path |
| Performance story | At least one timing with **methodology stated** (not just a single ms printout) |
| Narrative | README explains problem, approach, and limits (what is / is not implemented) |

### Tier B — “Hire me immediately” (hard to fake)

What a reviewer should conclude: *this person can measure, compare, and defend results like a senior engineer or researcher.*

| Evidence | Acceptable bar |
|----------|----------------|
| **Reproducible benchmark bundle** | Fixed commit, `RESULTS.md` (or equivalent): exact commands, environment capture, raw outputs or checked-in summary JSON |
| **Fair SOTA or strong baselines** | Apples-to-apples comparison vs best available baseline for *this workload* (see §4a)—not a strawman |
| **Numbers with variance** | Report median + IQR or mean ± stdev over **K** runs after warm-up; state **K** and warm-up policy |
| **WHY, not just WHAT** | Short rationale: bottleneck (memory vs compute), algorithmic choice, expected scaling with N; optional roofline or simple model |
| **Claims you can defend under cross-examination** | Every row in the results table ties to a script and a comparator implementation |
| **Optional arXiv / tech report** | 4–8 pages: problem, method, experimental setup, results table, threats to validity, reproducibility appendix—**same numbers as the repo** |

**Explicit non-goals for the showcase path:** more features for their own sake, sprawling scope, or “impressive” architecture without measured outcomes.

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

### 4a) SOTA and baseline discipline (for defensible “beat or match” claims)

“State of the art” here means **the strongest fair baseline for the same defined workload**, not the flashiest paper title.

| Claim type | Example fair baseline | Notes |
|------------|----------------------|--------|
| Sampling throughput | Optimized CPU (e.g. vectorized or parallel CPU reference), or vendor RNG throughput on same GPU class if you introduce that path | Same `N`, same dtype, include allocation/transfers if that is part of your API contract |
| Risk metrics on device | CPU reference on identical samples (file-backed or deterministic seed) | Report host/device transfer policy explicitly |
| End-to-end experiment | `experiment_run`-class pipeline vs “naive” script doing equivalent stages | State what is included in the timed region |

**Rules that make numbers hire-proof:**

1. **One workload definition per row** (input size, distribution parameters, batching, precision).
2. **Warm-up runs** excluded from reported statistics; state how many.
3. **Report throughput and time** (e.g. samples/sec *and* ms) so reviewers can sanity-check.
4. **If you cannot beat a baseline**, say so and explain **why** (I/O bound, intentional accuracy trade-off, unoptimized path)—that reads as maturity, not weakness.
5. **Hardware pinning**: GPU model, driver/CUDA version, clock behavior note (if laptop thermal throttling is possible, say it).

Deliverable artifact (Tier B): a single **`RESULTS.md`** (or `docs/BENCHMARKS.md`) that is the canonical place a recruiter opens after the README.

---

## 5) Detailed Delivery Roadmap

Each epic below includes a **portfolio lens**: what Tier A vs Tier B looks like, without requiring net-new feature surface—mostly **rigor, measurement, and narrative**.

## Epic A - Repository Truth and Operational Hygiene
**Goal:** eliminate docs-code drift and make all instructions executable.

### Portfolio lens
- **Tier A:** A reviewer can clone, build, and run tests without guesswork—basic trust.
- **Tier B:** The same clone path is the **exact** path cited in `RESULTS.md` and any arXiv appendix—zero “works on my machine” drift.

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

### Portfolio lens
- **Tier A:** Tests exist; interviewer believes you did not hand-wave CUDA correctness.
- **Tier B:** You can point to **one** flagship path (e.g. sampler → metric) with **published error bounds or parity thresholds** in docs—defensible under technical interview follow-up.

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

### Portfolio lens (this epic is the main “hire me” lever)
- **Tier A:** You show *some* timings with stated `N` and GPU.
- **Tier B:** You ship a **small, frozen benchmark suite** + table: TailWarp vs baselines, **K-run statistics**, methodology paragraph, and **why** each comparison is fair. This is the core artifact recruiters screenshot.

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

### Portfolio lens
- **Tier A:** README clearly labels placeholders (honesty beats overselling).
- **Tier B:** Only pursue fidelity upgrades that **change a claim you want to make** (e.g. “affine-invariant SPD distance”) **and** that you can validate + benchmark; otherwise defer—**no math for math’s sake**.

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

### Portfolio lens
- **Tier A:** `experiment_run` outputs look intentional; validation script exists.
- **Tier B:** Artifacts are **citable**: commit, config, environment JSON, and metrics tie 1:1 to a row in `RESULTS.md` / tech report—reviewer can replay your headline number.

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

### Portfolio lens
- **Tier A:** One plot or table of throughput vs `N` showing you understand scaling.
- **Tier B:** A short **roofline or bottleneck paragraph** tied to measured occupancy/memory throughput—answers “why not faster?” in interviews.

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

### Portfolio-first sequencing (optimize for hiring signal, not feature count)

| Milestone | Target outcome | Tier |
|-----------|----------------|------|
| M1 | Epic A done + README “reproduce everything” path | A |
| M2 | Epic B: one flagship correctness story (sampler + VaR/CVaR or one risk kernel) with published tolerances | A → B |
| M3 | Epic C: **`RESULTS.md` v1** with ≥2 fair baselines, K-run stats, methodology | **B (core)** |
| M4 | Epic E: one experiment folder that replays a headline row from `RESULTS.md` | B |
| M5 | Epic F: one scaling or roofline explanation tied to numbers | B |
| M6 | Optional: arXiv / tech report PDF in repo or linked release, **numbers identical to M3** | B+ |

### Q1 (Foundation)
- Epic A → Epic B (narrow: **prove one path end-to-end**)
- Epic C: implement only enough harness to publish **RESULTS.md v1** (small scope)

### Q2 (Trust and Narrative)
- Epic C: freeze benchmark definitions; tighten variance reporting
- Epic D: **only** if required to defend a claim you already published in M3; otherwise defer
- Epic F: one scaling/roofline section for the same workloads (no new kernels required)

### Q3 (Optional depth)
- Epic E: artifact replay polish for interviews (“here is the exact run that produced row 2”)
- Epic C: CI regression as guardrail, not as new benchmarks

### Q4 (Optional)
- arXiv / workshop paper / tech report: **same tables as repo**, extended threats-to-validity and related work
- Productization (API, Prometheus, etc.) **only** if it strengthens the story; otherwise skip for showcase purity

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

### 7.4 Recruiter / interviewer narrative (keep in README or `RESULTS.md` intro)

Use a fixed structure so hiring managers get signal in 60 seconds:

1. **Problem:** tail-aware risk metrics / sampling at scale (one sentence).
2. **What I built:** CUDA kernels + host API + reproducible experiments (one sentence).
3. **Evidence:** link or anchor to **one table** (throughput / time vs baselines).
4. **Why it wins or ties:** bottleneck + fairness rules (three bullets max).
5. **Integrity:** what is out of scope / placeholder (one sentence—builds trust).

---

## 8) Definition of Done (Cross-Epic)

A workstream is complete only if all are true:
- Code implemented and peer-reviewed
- Tests added/updated and passing in CI
- Benchmark impact documented (if performance-sensitive)
- Docs updated to match shipped behavior
- Acceptance criteria explicitly met and recorded

### Definition of Done — **Showcase / Tier B add-ons**

For any work that supports a public performance claim:

- [ ] Numbers appear in **`RESULTS.md`** (or equivalent) with command line, commit hash, and environment
- [ ] Baselines are **fair** per §4a; strawman comparisons are explicitly avoided
- [ ] **K** runs, warm-up policy, and aggregation (median/IQR or mean ± stdev) are stated
- [ ] **WHY** paragraph exists for each headline row (bottleneck + design choice)
- [ ] If arXiv/report exists: **tables match repo**; PDF includes reproducibility appendix

---

## 9) Optional arXiv / Technical Report (Same Numbers, Stronger Credential)

Use this **only** if you want a durable external pointer (LinkedIn, CV, interviews). It is **not** an excuse to add features; it is a **write-up of what you already measured**.

**Suggested outline (4–8 pages):**

1. Abstract — one quantitative headline (e.g. throughput delta at fixed `N`)
2. Problem & motivation — fat tails, risk metrics, need for fast simulation
3. Method — kernel/API overview; complexity and memory traffic at high level
4. Experimental setup — hardware, software, seeds, warm-up, baselines (mirror `RESULTS.md`)
5. Results — **same table as repo**; uncertainty bars or IQR
6. Discussion — why results make sense (roofline, bandwidth, Amdahl)
7. Threats to validity — thermal throttling, driver variance, comparator fairness
8. Reproducibility — git SHA, build flags, exact commands

**Acceptance criterion:** a reader can, in principle, replicate your headline row without emailing you.

---

## 10) Immediate Next Actions (Portfolio-Optimized, Not Feature-Optimized)

Prioritize **credibility and a first publishable table** over expanding module coverage.

1. **Epic A:** Fix doc/script drift so “clone → build → test → benchmark” is one documented path.
2. **Epic C:** Define **2–3 benchmark rows** you are willing to defend in an interview (workload + baseline + metric).
3. **Epic C:** Implement or script **only** the minimum to produce those rows with **K-run** statistics.
4. **Epic B:** Add **one** flagship correctness anchor for the same workloads (parity or bound)—enough to survive “how do you know it’s right?”
5. **Author `RESULTS.md` v1:** methodology at the top, table in the middle, “why” bullets at the bottom.
6. **README:** add the §7.4 narrative block linking to `RESULTS.md`.
7. **Epic E (light):** ensure one `experiment_run` output matches a table row (replay story).
8. **Epic F (light):** one scaling or bottleneck paragraph **grounded in those numbers**.
9. **Defer** Epic D placeholders unless a **published claim** requires the real SPD math—otherwise label honestly in README.
10. **Optional:** draft arXiv/tech report from `RESULTS.md` + setup section; **no new benchmarks** unless fixing a review gap.

This sequence maximizes **“hire me immediately”** signal per hour spent: defensible comparisons, explicit methodology, and narrative discipline—**not** a larger feature surface.
