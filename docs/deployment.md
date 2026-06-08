# TailWarp deployment guide

Operators can run TailWarp without reading C++ source.

## Python package (CPU)

```bash
pip install .
python -c "from tailwarp import TailWarpClient; print(TailWarpClient().compute_cvar([-0.1, 0.0], 0.9))"
```

## Docker — CPU image

```bash
docker build -f docker/Dockerfile.cpu -t tailwarp:cpu .
docker run --rm tailwarp:cpu
```

Slim image (`python:3.11-slim`); target &lt;300MB. No GPU required.

## Docker — CUDA image

```bash
docker build -f docker/Dockerfile.cuda -t tailwarp:cuda --build-arg CUDA_VERSION=12.2 .
docker run --rm --gpus all tailwarp:cuda ./build/examples/experiment_run configs/experiment_student_t_cvar.json
```

Requires NVIDIA Container Toolkit (`nvidia-docker2` or `nvidia-container-toolkit`).

Interactive shell:

```bash
docker run -it --rm --gpus all tailwarp:cuda bash
```

## Environment variables

| Variable | Default | Effect |
|----------|---------|--------|
| `TAILWARP_PREFER_CUDA` | `0` | Hint for future GPU dispatch on `TailWarpClient` |
| `CUDA_VISIBLE_DEVICES` | — | Standard NVIDIA device selection in CUDA containers |

## CUDA-not-found → CPU fallback

- `pip install tailwarp` never requires the CUDA toolkit.
- If `_native` extension is absent, all API methods use NumPy CPU reference.
- Dashboard and Black Swan replay read precomputed artifacts; live recompute uses `TailWarpClient` (CPU-safe).

## Black Swan dashboard

```bash
pip install ".[dashboard]"
streamlit run app/streamlit_black_swan_dashboard.py
```

## Release artifacts

Tag push or `workflow_dispatch` on [.github/workflows/release.yml](../.github/workflows/release.yml) builds:

- Python wheel (`dist/*.whl`)
- CPU Docker smoke
- CUDA image (build-only; may skip on hosts without NVIDIA builder support)

## GPU validation (manual)

```bash
# workflow_dispatch
gh workflow run gpu-smoke.yml
```

See [Tech-Debt.md](../Tech-Debt.md) TD-TW-03 when no GPU runner is available.
