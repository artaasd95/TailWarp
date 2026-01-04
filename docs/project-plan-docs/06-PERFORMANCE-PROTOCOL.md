# Performance Protocol (Benchmarking & Regression Detection)

This guide defines **how to measure, record, and track performance** to prevent regressions and guide optimization.

---

## Purpose

Performance is a first-class concern in TailWarp. Every module should have:
- A **baseline** (initial performance measurement)
- A **budget** (acceptable performance range)
- **Regression detection** (alerts when performance degrades)

---

## What to Measure

### 1. Kernel-Level Metrics
- **Execution time** (milliseconds)
- **Throughput** (scenarios/sec or elements/sec)
- **Memory bandwidth** (GB/s)
- **Occupancy** (% of theoretical max)
- **Register usage** (per thread)

### 2. End-to-End Metrics
- **Total runtime** (data load → simulation → metrics → output)
- **Host-to-device transfer time**
- **Device-to-host transfer time**
- **VRAM usage** (peak and average)

### 3. Scaling Metrics
- **Performance vs N** (scenarios)
- **Performance vs batch size**
- **Performance vs number of assets/instruments**

---

## How to Measure

### Using CUDA Events (Kernel Timing)

```cpp
cudaEvent_t start, stop;
cudaEventCreate(&start);
cudaEventCreate(&stop);

cudaEventRecord(start);
my_kernel<<<grid, block>>>(...);
cudaEventRecord(stop);

cudaEventSynchronize(stop);
float milliseconds = 0;
cudaEventElapsedTime(&milliseconds, start, stop);

// Compute throughput
float scenarios_per_sec = (N_scenarios / milliseconds) * 1000.0f;
```

### Using nvprof / Nsight Compute (Detailed Profiling)

```bash
# Profile a run
nsys profile --stats=true ./tailwarp_run config.json

# Analyze kernel performance
ncu --set full ./tailwarp_run config.json
```

### Using Host Timers (End-to-End)

```cpp
auto start = std::chrono::high_resolution_clock::now();
// ... run entire pipeline ...
auto end = std::chrono::high_resolution_clock::now();
auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
```

---

## Baseline Protocol (First Measurement)

When adding a new module or kernel:

1. **Choose a standard workload**:
   - Example: 10M scenarios, single asset, float precision
   
2. **Run multiple times** (at least 3) to account for variance:
   - Discard first run (warmup)
   - Record mean and std dev of remaining runs

3. **Record in experiment artifact**:
   ```json
   {
     "performance": {
       "kernel_time_ms": 45.2,
       "throughput_scenarios_per_sec": 221238938,
       "vram_usage_mb": 512,
       "hardware": "RTX 3060",
       "build": "Release, -O3, sm_86"
     }
   }
   ```

4. **Set a budget**:
   - Example: "This kernel should achieve > 200M scenarios/sec on RTX 3060"

---

## Regression Detection Protocol

Before merging changes that touch performance-critical code:

1. **Run the benchmark suite** (standard workloads)
2. **Compare to baseline**:
   - Acceptable: within ±5% of baseline
   - Warning: 5–10% slower
   - Regression: >10% slower (investigate before merging)
3. **Document if intentional**:
   - Example: "10% slower but now supports double precision"

---

## Benchmark Suite (Standard Workloads)

Define a small set of **always-run benchmarks**:

### Benchmark 1: Gaussian Sampler
- N = 10M scenarios
- Single asset
- Float precision
- Target: > 500M scenarios/sec

### Benchmark 2: Student-t Sampler
- N = 10M scenarios
- Single asset, ν=4
- Float precision
- Target: > 200M scenarios/sec

### Benchmark 3: VaR/CVaR Calculation
- Input: 10M samples
- Compute VaR@95, VaR@99, CVaR@99
- Target: < 10ms

### Benchmark 4: End-to-End (Gaussian → VaR)
- Load config, generate 10M Gaussian scenarios, compute VaR/CVaR, write output
- Target: < 5 seconds total

---

## Performance Budget (RTX 3060 Targets)

Based on hardware specs:
- **Memory bandwidth**: ~360 GB/s
- **Compute**: ~13 TFLOPS (FP32)
- **VRAM**: 12 GB

### Rough guidelines:
- **Memory-bound kernels**: Aim for 50–80% of peak bandwidth
- **Compute-bound kernels**: Aim for 30–50% of peak FLOPS (accounting for overhead)
- **VRAM usage**: Stay under 10 GB to leave headroom

---

## Optimization Workflow

When performance is below budget:

### 1. Profile
- Use `ncu` or `nsys` to identify bottlenecks
- Check: memory-bound or compute-bound?

### 2. Optimize
- **Memory-bound**: Coalesce accesses, use shared memory, reduce transfers
- **Compute-bound**: Reduce divergence, use fast math, improve occupancy

### 3. Measure Again
- Re-run benchmark
- Verify improvement

### 4. Document
- Record optimization in commit message
- Update performance baseline if significantly improved

---

## Performance Artifacts (What to Save)

For each experiment, include a `performance.json`:

```json
{
  "kernel_timings": {
    "rng_kernel_ms": 12.3,
    "distribution_kernel_ms": 45.2,
    "risk_metric_kernel_ms": 8.7
  },
  "throughput": {
    "scenarios_per_sec": 221238938,
    "elements_per_sec": 2212389380
  },
  "memory": {
    "vram_usage_mb": 512,
    "host_to_device_mb": 40,
    "device_to_host_mb": 0.5
  },
  "hardware": {
    "gpu": "NVIDIA GeForce RTX 3060",
    "compute_capability": "8.6",
    "driver": "535.104.05",
    "cuda_runtime": "12.2"
  },
  "build": {
    "type": "Release",
    "flags": "-O3 --use_fast_math",
    "arch": "sm_86"
  }
}
```

---

## Common Performance Pitfalls

- **No warmup**: First run is often slower due to cold caches
- **Insufficient repetitions**: Single run can be noisy
- **Debug builds**: Always benchmark in Release mode
- **Synchronization overhead**: Excessive `cudaDeviceSynchronize()` calls
- **Small workloads**: Kernel launch overhead dominates
- **Uncoalesced memory access**: Kills bandwidth
- **High register pressure**: Reduces occupancy

---

## Performance Review Checklist

Before calling a module "done":

```
[ ] Baseline performance measured (3+ runs, warmup discarded)
[ ] Performance budget defined (target scenarios/sec or time)
[ ] Performance meets or exceeds budget
[ ] Performance artifact (performance.json) saved
[ ] Profiling done to understand bottlenecks
[ ] No obvious optimization opportunities left (or documented as future work)
[ ] Regression test added to benchmark suite
```

---

## Example: Benchmarking Student-t Sampler

### Workload:
- N = 10M scenarios
- ν = 4
- Float precision
- RTX 3060

### Measurement:
```
Run 1 (warmup): 48.2 ms
Run 2: 45.1 ms
Run 3: 45.3 ms
Run 4: 45.0 ms

Mean: 45.1 ms
Std dev: 0.15 ms
Throughput: 221.7M scenarios/sec
VRAM: 512 MB
```

### Budget:
- Target: > 200M scenarios/sec ✅
- VRAM: < 1 GB ✅

### Baseline recorded:
- Saved to `data/output/experiments/.../performance.json`
- Added to benchmark suite

### Regression threshold:
- Warn if < 210M scenarios/sec
- Fail if < 200M scenarios/sec

---

## When to Re-Benchmark

Re-benchmark when:
- Code changes affect performance-critical paths
- Build flags or compiler version changes
- Hardware or driver updates
- Adding a new optimization
- Preparing for publication (verify numbers are still accurate)

---

## Long-Term Performance Tracking

Consider maintaining a **performance dashboard** (simple CSV or plot):

| Date       | Module        | Workload | Throughput (M/s) | Git Hash |
|------------|---------------|----------|------------------|----------|
| 2026-01-04 | Gaussian      | 10M      | 520              | abc123   |
| 2026-01-04 | Student-t     | 10M      | 221              | abc123   |
| 2026-01-10 | Student-t     | 10M      | 245              | def456   |

This makes regressions and improvements visible over time.

