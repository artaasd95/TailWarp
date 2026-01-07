# Configuration Files

Experiment configurations in JSON format.

## Structure

- `research/` - Research project configs (geometric methods)
- Root level - Example configs and templates

## Config Schema

```json
{
  "experiment_name": "string",
  "n_samples": int,
  "seed": int,
  "distribution": {
    "type": "student_t|stable|gaussian",
    "params": {}
  },
  "risk_metric": {
    "type": "cvar|var",
    "alpha": float
  },
  "output_artifacts": []
}
```

