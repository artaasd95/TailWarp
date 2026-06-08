# TailWarp Docker Configuration (S2-06)

## Overview

This directory contains Docker configurations that separate **CPU-only demo** from **GPU-accelerated CUDA benchmarks**.

- **Dockerfile.cpu**: Slim CPU image (`pip install tailwarp`, &lt;300MB target)
- **Dockerfile.demo**: Dashboard image (Streamlit; heavier than cpu)
- **Dockerfile.cuda**: Multi-stage GPU runtime for benchmarks and examples
- **docker-compose.example.yml**: Template showing how to orchestrate both services (example only, not used in CI)

---

## Quick Start

### CPU package smoke (No GPU Required)

```bash
docker build -f docker/Dockerfile.cpu -t tailwarp:cpu .
docker run --rm tailwarp:cpu
```

### CPU Demo dashboard

```bash
docker build -f docker/Dockerfile.demo -t tailwarp:demo .
docker run -it --rm -p 8501:8501 tailwarp:demo streamlit run app/streamlit_black_swan_dashboard.py
```

Then open http://localhost:8501 in your browser.

### CUDA Benchmark (GPU Required)

Build and run the CUDA benchmark image:

```bash
docker build -f docker/Dockerfile.cuda -t tailwarp:cuda .
docker run --rm --gpus all tailwarp:cuda ./build/examples/experiment_run configs/experiment_student_t_cvar.json
```

**Prerequisites:**
- NVIDIA GPU with compute capability 8.6+ (RTX 30-series or newer)
- NVIDIA Container Toolkit installed: https://github.com/NVIDIA/nvidia-docker
- Docker daemon configured with GPU support

---

## Design Rationale

### Separation of Concerns

| Aspect | CPU Demo | CUDA Benchmark |
|--------|----------|-----------------|
| **Purpose** | Documentation, visualization, development | Performance measurement, validation |
| **Size** | ~500 MB (slim Python base) | ~8-10 GB (CUDA 12.2 + cuDNN) |
| **Hardware** | CPU only (x86/ARM) | GPU required (NVIDIA 8.6+) |
| **Build Time** | < 1 minute | 5-10 minutes (CUDA compilation) |
| **CI Safety** | ✅ Can run on any CI runner | ⚠️ Requires GPU-equipped CI agent |
| **Use Case** | Local dev, docs build, quick test | Benchmarking, regression testing, release validation |

### Why Two Images?

1. **Cost**: GPU CI runners are expensive. CPU-safe checks (linting, unit tests, docs) should run on cheap CPU runners.
2. **Speed**: Don't download 8 GB CUDA images for every CI run if only documentation is being updated.
3. **Flexibility**: Developers can use the slim CPU image locally without GPU; benchmarking uses CUDA image on dedicated machines.
4. **Clarity**: Separating concerns makes it obvious which tests require GPU (manual approval needed) vs auto-gated CI.

---

## Building

### CPU Demo

```bash
docker build -f docker/Dockerfile.demo -t tailwarp:demo .
```

**Build time:** ~30–60 seconds  
**Image size:** ~500 MB  
**Dependencies:** Python 3.10, CMake, standard build tools

### CUDA Benchmark

```bash
# Build with default CUDA 12.2
docker build -f docker/Dockerfile.cuda -t tailwarp:cuda .

# Or specify custom CUDA version
docker build --build-arg CUDA_VERSION=11.8 -f docker/Dockerfile.cuda -t tailwarp:cuda-11.8 .
```

**Build time:** 5–10 minutes (heavy CUDA compilation)  
**Image size:** 8–10 GB  
**Dependencies:** NVIDIA CUDA toolkit, cuDNN, CMake, C++17 compiler

---

## Running

### CPU Demo — Streamlit Dashboard

```bash
docker run -it --rm -p 8501:8501 tailwarp:demo
```

Access at http://localhost:8501

Override default command:
```bash
docker run -it --rm tailwarp:demo bash
docker run -it --rm tailwarp:demo pytest tests/unit/ -v
docker run -it --rm tailwarp:demo sphinx-build -b html docs/ docs/_build/html
```

### CPU Demo — Unit Tests

```bash
docker run --rm tailwarp:demo pytest tests/unit/ -v
```

### CUDA Benchmark — Run Experiment

```bash
docker run --rm --gpus all tailwarp:cuda ./build/examples/experiment_run configs/experiment_student_t_cvar.json
```

Save results to host machine:
```bash
docker run --rm --gpus all \
  -v $(pwd)/benchmarks/results:/app/data/output \
  tailwarp:cuda \
  ./build/examples/experiment_run configs/experiment_student_t_cvar.json
```

Shell access for debugging:
```bash
docker run -it --rm --gpus all tailwarp:cuda bash
```

### GPU Availability

Check GPU access in container:
```bash
docker run --rm --gpus all tailwarp:cuda nvidia-smi
```

Expected output: List of NVIDIA GPUs visible inside container.

---

## Docker Compose (Template Example)

**NOTE:** `docker-compose.example.yml` is a reference template, NOT a live CI file.

If you want to use Docker Compose locally for orchestration:

```bash
# Copy and customize the example
cp docker/docker-compose.example.yml docker-compose.override.yml

# Edit docker-compose.override.yml for your environment
# (e.g., GPU runtime, volume paths, port bindings)

# Start services
docker-compose -f docker-compose.override.yml up

# Stop services
docker-compose -f docker-compose.override.yml down
```

**Why not use docker-compose.yml directly in CI?**
- CI jobs should have explicit, reproducible commands (not hidden in compose files).
- GPU availability varies per CI agent; compose would need environment-specific overrides (fragile).
- For explicit control, see [.github/workflows/](../.github/workflows/) (GitHub Actions templates).

---

## CI / CD Integration (S2-06)

See the [CI Plan](../docs/project-plan-docs/CI-PLAN.md) for details on:
- Which checks are CPU-safe (always-on CI)
- Which checks require GPU (manual approval)
- How Docker images are pushed to registries
- Release checklist integration

---

## Environment Variables

### CPU Demo
- `STREAMLIT_SERVER_PORT` (default: 8501) — Port for Streamlit server
- `STREAMLIT_SERVER_ADDRESS` (default: 0.0.0.0) — Bind address

### CUDA Benchmark
- `CUDA_VISIBLE_DEVICES` (default: 0) — Which GPU to use (e.g., "0,1" for two GPUs)
- `NVIDIA_VISIBLE_DEVICES` (default: all) — GPU visibility mode

---

## Troubleshooting

### GPU Not Visible

```bash
# Check if Docker has GPU support
docker run --rm --gpus all ubuntu nvidia-smi

# If this fails:
# 1. Install NVIDIA Container Toolkit
# 2. Restart Docker daemon
# 3. Verify /etc/docker/daemon.json has "nvidia" runtime configured
```

### Build Timeout (CUDA Image)

If the CUDA build times out:
```bash
# Use BuildKit for better caching
DOCKER_BUILDKIT=1 docker build -f docker/Dockerfile.cuda -t tailwarp:cuda .
```

### Out of Disk Space

CUDA images are large (~8-10 GB):
```bash
# Prune unused images
docker image prune -a --filter "until=24h"

# Check disk usage
docker system df
```

---

## Versioning & Tagging

Tag images for reproducibility:

```bash
# Tag with commit hash (reproducible)
docker build -f docker/Dockerfile.demo -t tailwarp:demo-$(git rev-parse --short HEAD) .

# Tag with version
docker build -f docker/Dockerfile.cuda -t tailwarp:cuda-v0.2.0 .

# For registry (e.g., GitHub Container Registry)
docker tag tailwarp:demo ghcr.io/artaasd95/tailwarp:demo-latest
docker push ghcr.io/artaasd95/tailwarp:demo-latest
```

---

## References

- [Docker Documentation](https://docs.docker.com/)
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker)
- [CUDA in Docker](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/)
- [TailWarp S2-06 Issue](https://github.com/artaasd95/TailWarp/issues/13)

---

**Maintained by:** @artaasd95  
**Last Updated:** 2026-05-26 (S2-06)  
