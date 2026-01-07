# Contributing to TailWarp

## Development Workflow

1. **Research → Implement → Validate → Benchmark → Record**
2. Never skip validation or benchmarking
3. Always produce experiment artifacts

## Adding New Features

See detailed checklists in `docs/project-plan-docs/02-CHECKLISTS.md`

### Adding a Distribution

1. Implement CUDA kernel in `src/core/distributions/`
2. Add CPU reference in `src/reference/`
3. Create wrapper in `src/wrappers/`
4. Write unit tests in `tests/unit/`
5. Add statistical validation in `tests/validation/`
6. Benchmark and record baseline

### Adding a Risk Metric

1. Implement kernel in `src/core/risk_metrics/`
2. Add CPU reference
3. Test invariants (monotonicity, bounds)
4. Compare GPU vs CPU within tolerance
5. Document output schema

## Code Standards

- **CUDA**: Compute capability 8.6+, use `--use_fast_math` for production
- **C++**: C++17, follow STL conventions
- **Comments**: Explain *why*, not *what*
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes

## Testing Requirements

Minimum for any new code:
- Level 0: Sanity checks (no NaN/Inf)
- Level 1: Unit tests pass
- Level 2: Invariants verified

For research-grade code, also include:
- Level 3: Statistical validation
- Level 4: End-to-end reproducibility

## Commit Guidelines

```
type(scope): short description

Longer explanation if needed.

Checklist:
- [ ] Tests pass
- [ ] No performance regression
- [ ] Documentation updated
```

Types: `feat`, `fix`, `test`, `docs`, `perf`, `refactor`

## Questions?

See `docs/project-plan-docs/QUICK-REFERENCE.md` for common workflows.

