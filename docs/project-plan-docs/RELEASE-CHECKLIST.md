# TailWarp Release Checklist (S2-06)

**Purpose:** Pre-production validation before publishing a release (e.g., v0.2.0)  
**Status:** Template Checklist (S2-06)  
**Date:** 2026-05-26  
**Owner:** @artaasd95  

---

## Pre-Release: 1-2 Weeks Before

### [ ] Phase 1: Preparation

- [ ] Verify all feature branches are merged to `develop`
- [ ] Update VERSION file: bump version number (e.g., 0.1.9 → 0.2.0)
- [ ] Update CHANGELOG.md with release notes:
  - [ ] New features (e.g., Warning State framework from S2-02)
  - [ ] Bug fixes
  - [ ] Breaking changes (if any)
  - [ ] Known limitations
- [ ] Review [RESULTS.md](../../RESULTS.md) — update performance numbers if changed
- [ ] Update [docs/VALIDATION.md](../VALIDATION.md) — confirm all validation levels met
- [ ] Check [docs/project-plan-docs/07-RISK-SIMPLE-PLAN.md](07-RISK-SIMPLE-PLAN.md) — align roadmap with release scope
- [ ] Create release branch: `git checkout -b release/v0.2.0`

### [ ] Phase 2: Documentation Audit

- [ ] README.md:
  - [ ] No broken links (run link checker: `markdown-link-check README.md`)
  - [ ] "Implemented today" section matches RESULTS.md
  - [ ] "Planned / partial" sections clearly marked as out-of-scope
  - [ ] Quick Start example works end-to-end
  
- [ ] Code docstrings:
  - [ ] No overclaiming (e.g., "robust covariance" not in Phase 1 docs)
  - [ ] Check `src/wrappers/risk_metrics.h` header comments
  - [ ] Check `src/core/` module READMEs
  
- [ ] Experiment artifacts:
  - [ ] Sample experiment folder matches [docs/EXPERIMENTS.md](../EXPERIMENTS.md) schema
  - [ ] `validation.json` lists evidence for levels 0–4
  - [ ] `summary.md` is human-readable

---

## Release Week: CPU-Safe Checks (5 Days Before)

### [ ] Phase 3: Auto-Gate Validation (CPU-Safe)

Run all CPU safety checks (see [CI-PLAN.md](CI-PLAN.md)):

```bash
# Option A: Run locally
bash scripts/ci-run-cpu-checks.sh

# Option B: Trigger in GitHub Actions (if configured)
# Visit: https://github.com/artaasd95/TailWarp/actions
# Click "CPU Safety Checks (Template)" → Run workflow
```

**Acceptance Criteria:** All checks pass ✅

- [ ] Linting (clang-format) passes
- [ ] CMake configuration succeeds
- [ ] Unit tests pass (all levels 0–2)
- [ ] Integration tests pass (E2E without GPU)
- [ ] Documentation builds without warnings
- [ ] Python linting succeeds (app/*, scripts/*)
- [ ] Artifact validation passes (manifest, JSON schema)

**If any fail:** Fix, commit, and re-run before proceeding.

---

## Release Day: GPU Validation (1-2 Days Before)

### [ ] Phase 4: Manual GPU Validation (On-Demand, GPU Machine)

**Prerequisites:**
- [ ] Access to GPU-equipped machine (NVIDIA RTX 3060 or better)
- [ ] CUDA 11.0+ and cuDNN installed
- [ ] Docker with GPU support configured (see [docker/README.md](../../docker/README.md))

**Run GPU validation suite:**

```bash
# Option A: Docker (reproducible, isolated)
docker build -f docker/Dockerfile.cuda -t tailwarp:cuda .
docker run --rm --gpus all tailwarp:cuda bash -c "
  ctest --test-dir build -L gpu -V && \
  ctest --test-dir build -L gpu-cpu-validation -V && \
  ./benchmarks/run_benchmark_suite.sh && \
  ./build/examples/experiment_run configs/experiment_student_t_cvar.json
"

# Option B: Local build (if you prefer)
bash scripts/ci-run-gpu-checks.sh
```

**Acceptance Criteria:** All checks pass ✅

- [ ] CUDA kernels compile without warnings/errors
- [ ] GPU unit tests pass (Student-t, Gaussian, warning state)
- [ ] GPU vs CPU validation passes (tail stats match within 0.1%)
- [ ] Benchmark suite completes (throughput/latency recorded)
- [ ] Full E2E experiment runs successfully
- [ ] Experiment artifacts validate (validation.json level 4)
- [ ] Performance matches or exceeds baseline (see [RESULTS.md](../../RESULTS.md))

**Record Results:**

```bash
# Capture benchmark output
./benchmarks/run_benchmark_suite.sh | tee benchmarks/results/v0.2.0-benchmark.log

# Save GPU test results
ctest --test-dir build -L gpu -V 2>&1 | tee benchmarks/results/v0.2.0-gpu-tests.log

# Collect experiment artifacts
cp -r data/output/experiments/2026-05-26T*/ benchmarks/results/sample_v0.2.0/
```

**If any fail:** Investigate, fix, re-run. Do NOT release without GPU validation passing.

---

## Release Documentation: 1 Day Before

### [ ] Phase 5: Artifact Packaging

Prepare release artifacts:

```bash
# Create release directory
mkdir -p release-v0.2.0/

# Copy key documents
cp RESULTS.md release-v0.2.0/
cp CHANGELOG.md release-v0.2.0/
cp README.md release-v0.2.0/
cp docs/VALIDATION.md release-v0.2.0/

# Copy benchmark results
cp benchmarks/results/v0.2.0-benchmark.log release-v0.2.0/
cp benchmarks/results/v0.2.0-gpu-tests.log release-v0.2.0/
cp -r benchmarks/results/sample_v0.2.0/ release-v0.2.0/artifacts/

# Copy Docker build scripts (reference)
cp docker/Dockerfile.* release-v0.2.0/docker/
cp docker/README.md release-v0.2.0/docker/

# Package
tar -czf tailwarp-release-v0.2.0-artifacts.tar.gz release-v0.2.0/
ls -lh tailwarp-release-v0.2.0-artifacts.tar.gz
```

**Checklist:**

- [ ] RESULTS.md copied to release artifacts
- [ ] CHANGELOG.md with v0.2.0 section
- [ ] Benchmark logs included
- [ ] Sample experiment folder from S2-02 validation included
- [ ] Docker templates (Dockerfile.demo, Dockerfile.cuda) included
- [ ] CI plan (docs/project-plan-docs/CI-PLAN.md) included
- [ ] Tarball created and tested (extract and verify)

---

## Release Publication: Release Day

### [ ] Phase 6: GitHub Release

**On GitHub:**

- [ ] Create a new Release:
  - Go to: https://github.com/artaasd95/TailWarp/releases/new
  - Tag: `v0.2.0`
  - Branch: `main` (after merge from release branch)
  - Title: "TailWarp v0.2.0 — Black Swan Defense with Warning States"
  - Description (copy from CHANGELOG.md, add links):
  
  ```markdown
  # TailWarp v0.2.0: Black Swan Defense Calibration
  
  **Release Date:** May 26, 2026
  
  ## Highlights
  - ✅ **S2-01**: Black Swan Defense scope locked; claims separated from results (RESULTS.md)
  - ✅ **S2-02**: TailWarpWarningState framework (green/yellow/red/critical thresholds)
  - ✅ **S2-06**: Docker separation (CPU demo vs CUDA benchmarks)
  
  ## Changes
  See [CHANGELOG.md](CHANGELOG.md) for detailed changelog.
  
  ## Performance (GPU: RTX 3060)
  - Gaussian sampling: 4.3B samples/sec (63x CPU speedup)
  - Student-t sampling: 3.2B samples/sec (68x CPU speedup)
  - Full E2E latency: ~50-100 ms for 10M samples
  
  See [RESULTS.md](RESULTS.md) for full results table.
  
  ## Validation Evidence
  - ✅ All CPU safety checks passing
  - ✅ GPU unit tests: Student-t moments match theory
  - ✅ GPU vs CPU: tail stats match within 0.1%
  - ✅ Warning state: all 4 thresholds deterministic + tested
  
  See [docs/VALIDATION.md](docs/VALIDATION.md) for validation levels.
  
  ## Installation
  
  ### CPU Demo (No GPU Required)
  ```bash
  docker build -f docker/Dockerfile.demo -t tailwarp:demo .
  docker run -it --rm -p 8501:8501 tailwarp:demo
  ```
  
  ### GPU Benchmarks (NVIDIA GPU Required)
  ```bash
  docker build -f docker/Dockerfile.cuda -t tailwarp:cuda .
  docker run --rm --gpus all tailwarp:cuda ./build/examples/experiment_run ...
  ```
  
  See [docker/README.md](docker/README.md) for detailed setup.
  
  ## Known Limitations
  - Univariate distributions only (multivariate in Phase 2)
  - SPD manifold covariance: stubs only (Phase 2–3)
  - EVT/POT tail diagnostics: partial (Phase 2)
  
  See [docs/project-plan-docs/07-RISK-SIMPLE-PLAN.md](docs/project-plan-docs/07-RISK-SIMPLE-PLAN.md) for roadmap.
  ```

- [ ] Attach release artifacts:
  - `tailwarp-release-v0.2.0-artifacts.tar.gz` (benchmark results, sample artifacts)
  - `RESULTS.md` (performance baseline)
  - Optional: pre-built Docker images (if registry push is automated)

---

### [ ] Phase 7: Docker Image Push (Optional, If Registry Configured)

If using GitHub Container Registry or Docker Hub:

```bash
# Build demo image
docker build -f docker/Dockerfile.demo -t ghcr.io/artaasd95/tailwarp:demo-v0.2.0 .
docker tag ghcr.io/artaasd95/tailwarp:demo-v0.2.0 ghcr.io/artaasd95/tailwarp:demo-latest
docker push ghcr.io/artaasd95/tailwarp:demo-v0.2.0
docker push ghcr.io/artaasd95/tailwarp:demo-latest

# Build CUDA image (on GPU machine)
docker build -f docker/Dockerfile.cuda -t ghcr.io/artaasd95/tailwarp:cuda-v0.2.0 .
docker tag ghcr.io/artaasd95/tailwarp:cuda-v0.2.0 ghcr.io/artaasd95/tailwarp:cuda-latest
docker push ghcr.io/artaasd95/tailwarp:cuda-v0.2.0
docker push ghcr.io/artaasd95/tailwarp:cuda-latest
```

**Checklist:**

- [ ] Demo image built and tagged `demo-v0.2.0` and `demo-latest`
- [ ] CUDA image built on GPU machine, tagged `cuda-v0.2.0` and `cuda-latest`
- [ ] Both images pushed to registry
- [ ] Registry URLs updated in docker/README.md
- [ ] Pull commands tested from fresh machine

---

### [ ] Phase 8: Merge & Tag

Back on GitHub:

```bash
# Ensure release branch is up to date
git checkout release/v0.2.0
git pull origin release/v0.2.0

# Merge to main
git checkout main
git pull origin main
git merge --no-ff release/v0.2.0 -m "Release v0.2.0: Black Swan Defense"

# Create tag
git tag -a v0.2.0 -m "Release v0.2.0: Black Swan Defense calibration"

# Push
git push origin main
git push origin v0.2.0

# Delete release branch
git branch -d release/v0.2.0
git push origin --delete release/v0.2.0
```

**Checklist:**

- [ ] `main` branch has latest release commit
- [ ] Git tag `v0.2.0` created and pushed
- [ ] GitHub shows release in "Releases" tab
- [ ] Release artifacts are downloadable

---

## Post-Release: Follow-Up

### [ ] Phase 9: Announcement & Monitoring

- [ ] Update project website / wiki (if exists) with v0.2.0 info
- [ ] Announce in relevant channels (e.g., GitHub Discussions, email to stakeholders)
- [ ] Monitor for bug reports or issues filed against v0.2.0
- [ ] Keep release branch for hotfixes (v0.2.1 if needed)
- [ ] Begin next sprint planning (S2-03+)

**Checklist:**

- [ ] Release announcement posted
- [ ] Stakeholders notified
- [ ] v0.2.0 branch/tag protected (if applicable)
- [ ] v0.2.1 hotfix plan ready (if needed)

---

## Rollback Plan (If Release Fails)

**If GPU validation fails after release:**

1. Immediately unpublish (delete) the release from GitHub
2. Revert tags: `git push origin --delete v0.2.0`
3. Revert merge: `git revert -m 1 <merge-commit-sha>`
4. Investigate root cause (see [CI-PLAN.md](CI-PLAN.md) troubleshooting)
5. Fix, re-test, re-release as v0.2.0-rc1 (release candidate)

**If Docker images are broken:**

1. Remove affected images from registry: `docker rmi ghcr.io/artaasd95/tailwarp:cuda-v0.2.0`
2. Rebuild and test locally before re-pushing
3. Update release notes: "Docker images updated; re-pulled"

---

## Release Checklist Template (Copy This for Future Releases)

```markdown
# Release v0.X.0 Checklist

## Preparation (1-2 weeks before)
- [ ] Version bumped (VERSION file, CHANGELOG.md)
- [ ] Features merged to `develop`
- [ ] RESULTS.md updated with new performance numbers
- [ ] docs/VALIDATION.md reviewed and updated
- [ ] Release branch created: `release/v0.X.0`

## CPU Validation (5 days before)
- [ ] bash scripts/ci-run-cpu-checks.sh PASSED
- [ ] All auto-gate checks passing

## GPU Validation (1-2 days before)
- [ ] bash scripts/ci-run-gpu-checks.sh PASSED
- [ ] GPU unit tests passing
- [ ] GPU vs CPU validation passing
- [ ] Benchmark suite complete; results recorded

## Documentation (1 day before)
- [ ] Release artifacts packaged (RESULTS.md, benchmarks, Docker files)
- [ ] Tarball created and verified

## Publication (Release day)
- [ ] GitHub release created with artifacts
- [ ] Docker images built and pushed (if applicable)
- [ ] Release tagged and merged to `main`
- [ ] Release announced

## Post-Release
- [ ] Bug reports monitored
- [ ] Next sprint planning begun
```

---

## Links & References

- **RESULTS.md:** [../../RESULTS.md](../../RESULTS.md) — Performance baselines & claims
- **VALIDATION.md:** [../VALIDATION.md](../VALIDATION.md) — Validation evidence & levels
- **CI Plan:** [CI-PLAN.md](CI-PLAN.md) — CPU vs GPU check details
- **Docker Guide:** [../../docker/README.md](../../docker/README.md) — Building & running images
- **Roadmap:** [07-RISK-SIMPLE-PLAN.md](07-RISK-SIMPLE-PLAN.md) — Feature scope & phases
- **Changelog:** [../../CHANGELOG.md](../../CHANGELOG.md) — Version history (to be created)

---

**Owner:** @artaasd95  
**Document Status:** Draft (S2-06)  
**Next Update:** After first release (v0.2.0)  
