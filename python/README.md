# TailWarp Python package

## Install (CPU mode)

From the repository root:

```bash
pip install .
```

Import works without a CUDA toolkit:

```python
from tailwarp import TailWarpClient

client = TailWarpClient()
result = client.compute_cvar([-0.1, -0.05, 0.0, 0.02], alpha=0.95)
print(result.value, result.method, result.device)
```

## Optional extras

```bash
# Documents CUDA-native wheel path (extension built separately via CMake)
pip install ".[cuda]"

# Dashboard dependencies
pip install ".[dashboard]"
```

## Native extension (optional)

Build host-only pybind11 module (no GPU required for `compute_cvar`):

```bash
cmake -B build -DBUILD_PYTHON=ON -DBUILD_TESTS=OFF
cmake --build build --target _native
# Copy or install _native*.so into python/tailwarp/ for local dev
```

When `_native` is missing, all public methods use the NumPy CPU fallback.

## API contract

See [docs/python-api-contract.md](../docs/python-api-contract.md).
