# RunPod execution — TailWarp

GPU benchmark execution and results collection for RunPod pods.

## Quick start

```bash
tmux new -s bench
bash runpod/setup.sh
bash runpod/run_benchmarks.sh
bash runpod/collect_results.sh
```

## Files

| File | Purpose |
|------|---------|
| `run_benchmarks.sh` | Build + run `benchmarks/run_benchmarks.py` |
| `collect_results.sh` | Archive and FTP-upload results |
| `setup.sh` | Install deps and build |
| `config.json` | Benchmark matrix config |

Set FTP credentials per `storage/README.md` before collecting results.
