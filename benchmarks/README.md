# Benchmarks

Performance evaluation suite for CUDA kernels.

## Structure

- `configs/` - Benchmark configurations
- `baselines/` - Reference performance numbers
- `results/` - Benchmark outputs (timestamped)

## Running Benchmarks

```bash
# Run full benchmark suite
./scripts/run_benchmarks.sh

# Run specific kernel benchmark
./build/benchmark_student_t
```

## Performance Targets (RTX 3060)

| Kernel | Target Throughput | Memory Budget |
|--------|------------------|---------------|
| Student-t sampler | > 200M samples/sec | < 1 GB |
| CVaR (10M samples) | < 10 ms | - |
| SPD exp/log | < 5 ms (batch of 1000) | - |

Regression threshold: ±5% acceptable, >10% requires investigation.

