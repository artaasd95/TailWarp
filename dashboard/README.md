# Black Swan dashboard

Streamlit UI for Black Swan benchmark bundles lives under [`app/`](../app/):

```bash
pip install -r app/requirements-black-swan-dashboard.txt
streamlit run app/streamlit_black_swan_dashboard.py
```

## Run selection

The sidebar **Run** dropdown lists every subdirectory of `benchmarks/results/` that contains `results.json`. Use **Custom bundle path** to point at another folder (for example a CUDA reproduction bundle once generated).

Artifacts are produced by:

```bash
python benchmarks/run_black_swan_benchmark.py --config benchmarks/configs/black_swan_replay.json
```

See [benchmarks/README.md](../benchmarks/README.md) and [docs/VALIDATION.md](../docs/VALIDATION.md) for the artifact contract.
