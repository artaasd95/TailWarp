# TailWarp CI/CD Plan (S2-06)

**Status:** Template & Documentation (Decision Date: 2026-05-26)  
**Owner:** @artaasd95  
**Acceptance Criteria:** CI plan states which checks are CPU-safe and which remain manual GPU checks; release checklist links artifacts.

---

## Overview

This document defines the **CI/CD strategy** for TailWarp, separating:
1. **Always-on CPU checks** (fast, cheap, every commit)
2. **Manual GPU checks** (slow, expensive, on-demand for releases)
3. **Artifact collection** (experiment folders, benchmarks, validation evidence)

---

## CI/CD Architecture

### Stage 1: Pre-Commit (Local Developer Machine)

Before pushing to GitHub, developers should run locally:

```bash
# Lint C++ code
clang-format -i src/**/*.{h,cpp}

# Build and unit test (CPU, ~1-2 minutes)
cmake -B build -DBUILD_TESTS=ON
cmake --build build -j$(nproc)
ctest --test-dir build -V

# Run Python validation scripts (CPU)
python scripts/validate_experiment.py data/output/experiments/*/
```

**Goal:** Catch obvious errors before CI runs.

---

### Stage 2: Continuous Integration (GitHub Actions / CI Runner)

#### Workflow 2.1: Auto-Gate on Every Commit (CPU-Safe)

**Trigger:** Every push to `main` or `develop`  
**Runner:** Standard CPU runner (no GPU required)  
**Duration:** ~5–10 minutes  
**Cost:** $0.008/minute (cheap)

**Checks:**

| Check | Tool | Time | Status | Notes |
|-------|------|------|--------|-------|
| **Linting (C++)** | `clang-format` check | 30s | ✅ Auto-gate | Enforce code style |
| **CMake Configuration** | `cmake -B build` | 20s | ✅ Auto-gate | Verify build setup |
| **Unit Tests (CPU)** | `ctest -L unit` | 2–3 min | ✅ Auto-gate | VaR/CVaR invariants, warning state logic |
| **Integration Tests (CPU)** | `ctest -L integration` | 1–2 min | ✅ Auto-gate | E2E: config → artifact folder (no GPU) |
| **Documentation Build** | `sphinx-build -b html docs/` | 1 min | ✅ Auto-gate | Ensure docs are buildable |
| **Python Linting** | `pylint app/` | 30s | ✅ Auto-gate | Dashboard code quality |
| **Artifact Validation** | `validate_experiment.py` | 30s | ✅ Auto-gate | Sanity checks on test artifacts |

**Pass Criteria:** All checks pass → PR can be merged

**Fail Criteria:** Any check fails → PR blocked until fixed

**Example GitHub Actions Template:**

```yaml
# .github/workflows/ci-cpu-safety.yml (TEMPLATE — NOT AN ACTUAL FILE)
#
# This is a REFERENCE TEMPLATE for how to set up CPU-safe CI checks.
# Do NOT check this into .github/workflows directly; instead:
# 1. Use explicit docker build/run commands or plain shell scripts
# 2. See docs/project-plan-docs/CI-PLAN.md for full guidance
#
# For actual CI setup, use simple bash scripts in scripts/ directory
# Example: scripts/ci-run-cpu-checks.sh

name: CPU Safety Checks (Template Reference)

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  cpu-checks:
    runs-on: ubuntu-latest
    container:
      image: python:3.10-slim
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Build Dependencies
        run: apt-get update && apt-get install -y cmake build-essential
      
      - name: Configure CMake
        run: cmake -B build -DBUILD_TESTS=ON
      
      - name: Build
        run: cmake --build build -j4
      
      - name: Run Unit Tests
        run: ctest --test-dir build -L unit -V
      
      - name: Run Integration Tests
        run: ctest --test-dir build -L integration -V
      
      - name: Validate Artifacts
        run: python scripts/validate_experiment.py data/output/experiments/*/
```

---

#### Workflow 2.2: Manual GPU Validation (On-Demand)

**Trigger:** Manual (GitHub Actions `workflow_dispatch` trigger)  
**Runner:** GPU-equipped CI agent (NVIDIA RTX 3060 or better)  
**Duration:** 15–30 minutes  
**Cost:** $0.30+/minute (expensive; only run when needed)

**When to Run:**
- Before a release (S2-06 Release Checklist)
- After modifying GPU kernels (Student-t sampling, CVaR sort, etc.)
- Quarterly performance regression check
- After CUDA toolkit update

**Checks:**

| Check | Tool | Duration | Status | Notes |
|-------|------|----------|--------|-------|
| **CUDA Build** | `cmake --build build` (GPU kernels) | 5–10 min | 🟡 Manual | Compiles Student-t, Gaussian, manifold stubs |
| **GPU Unit Tests** | `ctest -L gpu` | 2–3 min | 🟡 Manual | GPU kernel correctness (sample moments, no NaN) |
| **GPU vs CPU Match** | `ctest -L gpu-cpu-validation` | 3–5 min | 🟡 Manual | Distribution stats: GPU tail ≈ CPU tail |
| **Benchmark Suite** | `benchmarks/run_benchmark_suite.sh` | 5–10 min | 🟡 Manual | Throughput: samples/sec, kernel latency |
| **Performance Regression** | Compare to baseline (RESULTS.md) | 2 min | 🟡 Manual | Flag if performance drops >5% |
| **Experiment Artifact** | Full config → run → validation.json | 3–5 min | 🟡 Manual | E2E: produces valid experiment folder |

**Pass Criteria:** All checks pass → GPU validation passed; safe to release

**Fail Criteria:** Any check fails → Investigate; do not release without fix

**Example Manual Check Invocation:**

```bash
# Developer or CI operator manually runs (on GPU machine):
docker build -f docker/Dockerfile.cuda -t tailwarp:cuda .
docker run --rm --gpus all tailwarp:cuda \
  bash -c "
    ctest --test-dir build -L gpu -V && \
    ctest --test-dir build -L gpu-cpu-validation -V && \
    ./benchmarks/run_benchmark_suite.sh && \
    ./build/examples/experiment_run configs/experiment_student_t_cvar.json
  "
```

---

### Stage 3: Release Checklist (Pre-Production)

Before publishing a release (e.g., v0.2.0):

**Manual Approval Gate:**
1. ✅ All CPU checks passing (Stage 2.1)
2. ✅ GPU validation passed (Stage 2.2)
3. ✅ RESULTS.md updated with new performance numbers
4. ✅ Release checklist (see `RELEASE-CHECKLIST.md`) completed
5. ✅ Docker images built and pushed to registry
6. ✅ Benchmarks reviewed and documented

See [RELEASE-CHECKLIST.md](RELEASE-CHECKLIST.md) for full details.

---

## CPU-Safe Checks (Always-On, Auto-Gate)

### 1. Linting & Code Style

**Tool:** `clang-format`  
**Command:** `clang-format --dry-run -Werror src/**/*.{h,cpp}`  
**Why:** Enforces consistent code formatting; no logic required

```bash
# Check formatting
clang-format --dry-run src/**/*.cpp | grep -c "^---" && echo "FAIL" || echo "PASS"
```

### 2. Build Configuration

**Tool:** CMake  
**Command:** `cmake -B build -DBUILD_TESTS=ON`  
**Why:** Verifies CMake setup is correct; no compilation needed

```bash
# Just configuration, no build
cmake -B build -DBUILD_TESTS=ON 2>&1 | grep -i "error"
```

### 3. Unit Tests (Small, Deterministic)

**Tool:** GTest (via CMake)  
**Command:** `ctest --test-dir build -L unit -V`  
**Tests:**
- VaR/CVaR monotonicity (e.g., VaR ≤ CVaR)
- Warning state determinism (same inputs → same state)
- Arithmetic correctness (mean, std dev)
- Bounds checking (no NaN/Inf)

**Why:** Small inputs, no randomness, no GPU, reproducible

Example test:
```cpp
TEST(RiskMetrics, CVaR_GreaterThanVaR) {
    std::vector<float> returns = {...};
    float var = compute_var(returns, 0.95);
    float cvar = compute_cvar(returns, 0.95);
    ASSERT_GE(cvar, var);  // CVaR >= VaR always
}
```

### 4. Integration Tests (E2E, CPU-Safe Paths)

**Tool:** GTest or custom scripts  
**Command:** `ctest --test-dir build -L integration -V`  
**Tests:**
- Config JSON → experiment folder (no GPU)
- Artifact validation (manifest.json, config.json, metrics.json)
- Python script execution (validate_experiment.py)

**Why:** Tests the full pipeline without GPU (using CPU fallbacks for sampling)

### 5. Documentation Build

**Tool:** Sphinx (reStructuredText/Markdown)  
**Command:** `sphinx-build -b html docs/ docs/_build/html`  
**Why:** Ensures documentation is syntactically correct; no logic required

```bash
# Quick check without full build
python -m sphinx --version
sphinx-build -b html docs/ docs/_build/ 2>&1 | grep "error" && echo "FAIL" || echo "PASS"
```

### 6. Python Linting

**Tool:** `pylint` or `flake8`  
**Command:** `pylint app/ scripts/ || true` (don't fail on lint errors in CI)  
**Why:** Catches obvious Python mistakes (undefined variables, style issues)

```bash
pylint app/streamlit_black_swan_dashboard.py --exit-zero
```

### 7. Artifact Validation

**Tool:** Custom script (validate_experiment.py)  
**Command:** `python scripts/validate_experiment.py data/output/experiments/*/`  
**What it checks:**
- All required JSON files exist (manifest.json, config.json, metrics.json, validation.json)
- JSON parses without errors
- Array lengths match (e.g., quantiles.csv has same number of rows as metrics)

**Why:** Sanity check for test artifacts; no GPU needed

---

## GPU Checks (Manual, On-Demand)

### 1. CUDA Compilation

**Tool:** NVIDIA CUDA Compiler (nvcc)  
**Command:** `cmake --build build` (with CUDA kernels enabled)  
**Why:** Verifies GPU code compiles; requires CUDA toolkit

**Build time:** 5–10 minutes

### 2. GPU Unit Tests

**Tool:** GTest (on GPU)  
**Command:** `ctest --test-dir build -L gpu -V`  
**Tests:**
- Student-t sampling: sample mean ≈ 0, variance ≈ σ²
- Gaussian sampling: moments match theory
- No NaN/Inf in GPU output

**Why:** Validates GPU kernel correctness; requires GPU

**Duration:** 2–3 minutes

### 3. GPU vs CPU Validation

**Tool:** Comparison test (GPU vs host reference)  
**Command:** `ctest --test-dir build -L gpu-cpu-validation -V`  
**Tests:**
- Same 1M sample, GPU vs CPU: tail stats within 0.1% (CVaR, quantiles)
- Distribution moments: mean, std dev, skewness match

**Why:** Ensures GPU results are trustworthy; requires GPU

**Duration:** 3–5 minutes

### 4. Benchmark Suite

**Tool:** Custom script (benchmarks/run_benchmark_suite.sh)  
**Command:** See RELEASE-CHECKLIST.md  
**Benchmarks:**
- Gaussian sampling: 10M samples → throughput (samples/sec)
- Student-t sampling: 10M samples → throughput + latency
- CVaR computation: 10M samples → latency

**Why:** Tracks performance over time; requires GPU

**Duration:** 5–10 minutes

### 5. Full E2E Experiment

**Tool:** CLI (experiment_run)  
**Command:** `./build/examples/experiment_run configs/experiment_student_t_cvar.json`  
**What it does:**
- Reads config
- Calls GPU samplers (Student-t)
- Computes risk metrics
- Writes experiment folder
- Validates artifacts

**Why:** Comprehensive validation of entire pipeline; requires GPU

**Duration:** 3–5 minutes

---

## GitHub Actions Workflow Examples (TEMPLATE REFERENCE ONLY)

**IMPORTANT:** These are **REFERENCE TEMPLATES** for illustration. Actual CI should use:
- Shell scripts in `scripts/ci-*.sh` (easier to debug locally)
- Or explicit `docker` commands (reproducible, easy to test)
- NOT committed GitHub Actions YAML (prevents accidental CI breakage)

### Template: CPU Safety Workflow

```bash
#!/bin/bash
# scripts/ci-run-cpu-checks.sh (EXAMPLE SCRIPT)

set -e  # Exit on error

echo "=== TailWarp CPU Safety Checks ==="

# 1. Linting
echo "1. Checking code formatting..."
clang-format --dry-run -Werror src/**/*.cpp || echo "Format check failed"

# 2. CMake configuration
echo "2. Configuring CMake..."
cmake -B build -DBUILD_TESTS=ON

# 3. Build
echo "3. Building..."
cmake --build build -j$(nproc)

# 4. Unit tests
echo "4. Running unit tests..."
ctest --test-dir build -L unit -V --timeout 60

# 5. Integration tests
echo "5. Running integration tests..."
ctest --test-dir build -L integration -V --timeout 120

# 6. Documentation
echo "6. Building documentation..."
sphinx-build -b html docs/ docs/_build/ 2>&1 | tail -20

# 7. Artifact validation
echo "7. Validating artifacts..."
python scripts/validate_experiment.py data/output/experiments/*/ || echo "Artifact check failed"

echo "=== CPU Safety Checks Complete ==="
```

**Run locally:**
```bash
bash scripts/ci-run-cpu-checks.sh
```

### Template: GPU Validation Script

```bash
#!/bin/bash
# scripts/ci-run-gpu-checks.sh (EXAMPLE SCRIPT — MANUAL INVOCATION)

set -e

echo "=== TailWarp GPU Validation Checks ==="

# Requires GPU and CUDA toolkit

# 1. CUDA Build
echo "1. Building CUDA kernels..."
cmake -B build -DBUILD_TESTS=ON -DCMAKE_BUILD_TYPE=Release
cmake --build build -j$(nproc)

# 2. GPU unit tests
echo "2. Running GPU unit tests..."
ctest --test-dir build -L gpu -V --timeout 180

# 3. GPU vs CPU validation
echo "3. Validating GPU vs CPU..."
ctest --test-dir build -L gpu-cpu-validation -V --timeout 300

# 4. Benchmark suite
echo "4. Running benchmark suite..."
./benchmarks/run_benchmark_suite.sh

# 5. Full E2E experiment
echo "5. Running full E2E experiment..."
./build/examples/experiment_run configs/experiment_student_t_cvar.json

echo "=== GPU Validation Checks Complete ==="
```

**Run on GPU machine (manually):**
```bash
bash scripts/ci-run-gpu-checks.sh
```

---

## Artifact Collection (For Releases & Benchmarks)

### Experiment Artifacts

After running an experiment, the `data/output/experiments/` folder contains:

```
data/output/experiments/2026-05-26T12-34-56Z__student_t_cvar__10M/
  manifest.json          # Metadata (date, version, config hash)
  config.json            # Input config (distribution, samples, etc.)
  environment.json       # Build info (compiler, CUDA version, CPU model)
  build.json             # CMake flags, build time
  metrics.json           # VaR, CVaR, mean, std, skew, kurtosis
  validation.json        # Validation checklist (levels 0-4)
  performance.json       # Timing: kernel latency, throughput
  summary.md             # Human-readable summary
  artifacts/
    quantiles.csv        # Percentiles (0%, 1%, ..., 99%, 100%)
    histogram.csv        # Histogram bins + counts
```

### How to Archive Artifacts

**For CI (GitHub Actions):**

```yaml
# Template reference (not actual YAML)
- name: Archive experiment artifacts
  uses: actions/upload-artifact@v3
  with:
    name: experiment-results-${{ github.run_id }}
    path: data/output/experiments/*/
    retention-days: 30
```

**For releases:**

```bash
# Collect artifacts into release bundle
mkdir -p release-artifacts/
cp -r data/output/experiments/*/ release-artifacts/
cp RESULTS.md release-artifacts/
cp benchmarks/results/baselines/*.json release-artifacts/
tar -czf tailwarp-release-v0.2.0-artifacts.tar.gz release-artifacts/
```

---

## Troubleshooting CI Failures

### CPU Check Failures

| Failure | Root Cause | Fix |
|---------|-----------|-----|
| CMake config fails | Missing dependency | `apt-get install cmake` |
| Unit test fails | Code bug | Debug locally: `ctest -L unit -V --output-on-failure` |
| Docs build fails | ReStructuredText syntax | Check `docs/*.md` for markdown issues |
| Artifact validation fails | Missing JSON fields | Run `validate_experiment.py` locally |

### GPU Check Failures

| Failure | Root Cause | Fix |
|---------|-----------|-----|
| CUDA compilation fails | Incompatible GPU arch | Check compute capability: `nvidia-smi` → adjust `-DCMAKE_CUDA_ARCHITECTURES` |
| GPU test timeout | Long kernel execution | Reduce sample size in test config |
| GPU vs CPU mismatch | Numerical precision | Relax tolerance in comparison test (e.g., 0.5% instead of 0.1%) |
| Out of memory | 10M samples too large | Reduce in benchmark; or increase GPU memory |

---

## Summary: CPU vs GPU Decision Tree

```
Does the check require GPU?
├─ NO (linting, CMake config, small unit tests)
│  └─ RUN IN EVERY COMMIT (auto-gate, fast, cheap)
│
├─ YES (GPU kernels, large sampling, benchmarks)
│  └─ RUN MANUALLY (on-demand, before releases)
│
└─ MAYBE (integration tests with CPU fallback)
   └─ RUN IN AUTO-GATE (CPU path); GPU path manual
```

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker)
- [CMake Testing](https://cmake.org/cmake/help/latest/command/ctest.html)
- [TailWarp Docker Guide](../../docker/README.md)
- [TailWarp Release Checklist](RELEASE-CHECKLIST.md)

---

**Document Status:** Draft (S2-06)  
**Next Review:** After S2-06 implementation  
**Owner:** @artaasd95  
