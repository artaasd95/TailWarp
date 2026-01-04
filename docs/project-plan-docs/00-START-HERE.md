# Start Here (First Week Playbook)

This repo is **research-first**: we build a GPU simulation + risk framework that can later support many papers, demos, and downstream products.

---

## What "good progress" looks like

By the end of **Week 1** you should have:
- ✅ A minimal run workflow that produces an **experiment folder** (see `../EXPERIMENTS.md`)
- ✅ At least one kernel (even a simple Gaussian sampler) that passes **basic validation** (see `../VALIDATION.md`)
- ✅ A baseline **performance number** that you can track over time (scenarios/sec + kernel time)

By the end of **Week 2** you should have:
- ✅ A complete vertical slice (data → simulation → metrics → validation → artifacts)
- ✅ Checklists integrated into your workflow (see `02-CHECKLISTS.md`)
- ✅ At least one research question answered with reproducible artifacts

---

## How to start (practical sequence)

### 1) Establish the repo conventions (no UI required)

**All work is traceable**:
- Each run writes provenance + outputs under `data/output/experiments/...`
- Every result you care about has: `manifest.json`, `config.json`, `environment.json`, `build.json`, `metrics.json`, `validation.json`, `performance.json`, `summary.md`

**All changes are measurable**:
- Add/modify a kernel → run validation checks → run performance protocol → record baseline

**Example folder after first run**:
```
data/output/experiments/2026-01-04T12-34-56Z__gaussian_varcvar__N10M__seed42/
  manifest.json
  config.json
  environment.json
  build.json
  metrics.json
  validation.json
  performance.json
  summary.md
  artifacts/
    quantiles.csv
    histogram.csv
```

### 2) Pick the initial "vertical slice"

Choose **one minimal end-to-end path**:

| Component | First Choice | Next Choice |
|-----------|--------------|-------------|
| **Model** | Gaussian returns | Student-t |
| **Metric** | VaR + CVaR | POT/EVT |
| **Asset** | Single position | Portfolio |
| **Output** | Quantiles + histogram | Full distribution |

**Why this order?**
- Gaussian has analytic validation → easiest to verify correctness
- VaR/CVaR are standard → well-understood invariants
- Single position → simplest data model

This slice is not a "product"; it is the **core research harness** that everything else builds on.

### 3) Decide your initial scope boundaries

For the **first iteration** (Phase 0–1):
- ✅ Keep instrument complexity low (returns / PnL distribution, no options yet)
- ✅ Keep the number of metrics small (2–3 max)
- ✅ Focus on: correctness + reproducibility + performance baselines
- ❌ Avoid: complex portfolios, exotic instruments, optimization, RL

**You can add these later** once the harness is solid.

---

## Core workflow (the loop you repeat forever)

```
┌─────────────────────────────────────────────────────────┐
│  1. Formulate   →  2. Implement  →  3. Validate         │
│       ↑                                    ↓             │
│  5. Record      ←  4. Benchmark  ←─────────┘             │
└─────────────────────────────────────────────────────────┘
```

1. **Formulate**: Define the research question or kernel idea  
   → See `04-RESEARCH-WORKFLOW.md`

2. **Implement**: Add kernel/module with minimal wrapper  
   → See `03-ADD-A-MODULE.md`

3. **Validate**: Run sanity + invariants + statistical checks  
   → See `../VALIDATION.md` + use checklist from `02-CHECKLISTS.md`

4. **Benchmark**: Record performance and compare to baseline  
   → See `06-PERFORMANCE-PROTOCOL.md`

5. **Record**: Write experiment artifacts + summary  
   → See `../EXPERIMENTS.md`

**Never skip steps 3–5**. They're what make this "research-grade" instead of "demo code."

---

## Quick answers to common questions

### "If we want to research something, what should we do?"

1. Write the question as a **testable claim**:
   - ✅ Good: "Student-t with ν=4 increases 99% CVaR by 20–30% vs Gaussian under same volatility"
   - ❌ Bad: "Test Student-t"

2. Design an **experiment matrix** (what to vary, what to hold constant)

3. Create **configs** for each run

4. Run experiments and **collect artifacts**

5. Write a **research note** summarizing findings

→ Full guide: `04-RESEARCH-WORKFLOW.md`

### "If we want to add a new module, what should we do?"

1. Define **purpose, inputs, outputs** (write it down first)

2. Implement **core logic** (kernel + wrapper)

3. Add **validation tests** (use checklist from `02-CHECKLISTS.md`)

4. **Benchmark** and record baseline

5. Create an **experiment config** that exercises the module

6. **Document** the module (parameters, references, validation approach)

→ Full guide: `03-ADD-A-MODULE.md`

### "If we want to test an idea, what's the checklist?"

Use the **"Implementing a Research Idea"** checklist from `02-CHECKLISTS.md`:
- [ ] Research question stated clearly
- [ ] Experiment design defined
- [ ] Baseline comparison chosen
- [ ] Code implemented and validated
- [ ] Artifacts produced
- [ ] Results summarized
- [ ] Reproducibility confirmed

### "How do we know if results are good enough to share?"

Use the **experiment review levels** from `05-EXPERIMENT-REVIEW.md`:
- **Level 1**: Internal sanity (quick checks during dev)
- **Level 2**: Research-grade internal (trustworthy for decisions)
- **Level 3**: Publication-ready (can be shared externally)

---

## First week checklist

```
[ ] Read this file (00-START-HERE.md)
[ ] Read ../EXPERIMENTS.md and ../VALIDATION.md
[ ] Skim 01-RD-PHASES.md to understand the roadmap
[ ] Set up build environment (CMake, CUDA, compiler)
[ ] Implement a minimal Gaussian sampler kernel
[ ] Run sanity checks (no NaN/Inf)
[ ] Compare GPU output to CPU reference
[ ] Measure baseline performance (scenarios/sec)
[ ] Produce first experiment folder with all artifacts
[ ] Review using 05-EXPERIMENT-REVIEW.md (aim for Level 1)
```

Once this is done, you have a **working research harness**. Everything else is adding modules to it.

---

## What to read next

- **If you're about to add a kernel**: Read `03-ADD-A-MODULE.md`
- **If you're starting a research project**: Read `04-RESEARCH-WORKFLOW.md`
- **If you're unsure what to build next**: Read `01-RD-PHASES.md`
- **If you need a checklist**: Open `02-CHECKLISTS.md`

---

## Remember

- **Research-first** means correctness and reproducibility over speed of iteration
- **No UI required** means all workflows are script/CLI-based (for now)
- **Long-term** means we build infrastructure that lasts, not quick demos
- **Incremental** means each module adds to a stable foundation

Start small, validate thoroughly, document everything. The rest will follow.


