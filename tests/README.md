# Tests

Unit tests and validation suite.

## Structure

- `unit/` - Individual kernel/function tests
- `integration/` - End-to-end pipeline tests
- `validation/` - Statistical validation (GPU vs CPU)
- `fixtures/` - Test data and expected outputs

## Running Tests

```bash
# Build and run all tests
make test

# Run specific test suite
./build/tests/unit_tests
./build/tests/validation_tests
```

## Validation Levels

- Level 0: Sanity (no NaN/Inf)
- Level 1: Unit tests (correctness on small inputs)
- Level 2: Invariants (monotonicity, bounds)
- Level 3: Statistical (moments, quantiles vs reference)
- Level 4: End-to-end (full experiment reproducibility)

