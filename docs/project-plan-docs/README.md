# TailWarp Project Plan Docs

This folder is the **operating manual** for long-term R&D in TailWarp: checklists, phase gates, and "how we work" guides.

---

## 🚀 Start here

**New to the repo?** Read these in order:

1. **`00-START-HERE.md`** — First week playbook, core workflow, quick answers
2. **`../EXPERIMENTS.md`** — How experiments are structured and tracked
3. **`../VALIDATION.md`** — How correctness is verified at multiple levels
4. **`01-RD-PHASES.md`** — Long-term roadmap with phase gates

---

## 📋 Use these guides as needed

| Guide | When to use it |
|-------|----------------|
| **`02-CHECKLISTS.md`** | Every time you add a module, kernel, or risk metric |
| **`03-ADD-A-MODULE.md`** | Step-by-step: how to integrate a new component |
| **`04-RESEARCH-WORKFLOW.md`** | When running experiments to answer a research question |
| **`05-EXPERIMENT-REVIEW.md`** | To decide if results are trustworthy/publishable |
| **`06-PERFORMANCE-PROTOCOL.md`** | To benchmark and prevent performance regressions |

---

## 🎯 Quick navigation by task

### "I want to add a new distribution (e.g., Student-t)"
1. Read `03-ADD-A-MODULE.md` (Step-by-step guide)
2. Use checklist from `02-CHECKLISTS.md` → "Adding a New Distribution Kernel"
3. Follow validation levels from `../VALIDATION.md`
4. Benchmark using `06-PERFORMANCE-PROTOCOL.md`

### "I want to answer a research question"
1. Read `04-RESEARCH-WORKFLOW.md` (How to design experiments)
2. Create experiment configs (see `../EXPERIMENTS.md`)
3. Run experiments and collect artifacts
4. Review using `05-EXPERIMENT-REVIEW.md`

### "I want to know what to build next"
1. Read `01-RD-PHASES.md` (Phase gates and priorities)
2. Check current phase "done when" criteria
3. Pick next task from priority matrix

### "I want to verify my code is correct"
1. Read `../VALIDATION.md` (Validation levels 0–4)
2. Use checklist from `02-CHECKLISTS.md`
3. Produce validation artifacts (see `../EXPERIMENTS.md`)

### "I want to check if I'm causing performance regressions"
1. Read `06-PERFORMANCE-PROTOCOL.md`
2. Run benchmark suite
3. Compare to baseline (within ±5% is acceptable)

---

## 📚 Canonical repo-wide specs (outside this folder)

- **`../EXPERIMENTS.md`** — Experiment structure, provenance, reproducibility
- **`../VALIDATION.md`** — Validation strategy, levels, reference implementations

---

## 🔄 The core research loop

```
┌─────────────────────────────────────────────────────────┐
│  1. Formulate   →  2. Implement  →  3. Validate         │
│       ↑                                    ↓             │
│  5. Record      ←  4. Benchmark  ←─────────┘             │
└─────────────────────────────────────────────────────────┘
```

**Never skip steps 3–5.** They're what make this research-grade.

---

## 💡 Philosophy

- **Research-first**: Correctness and reproducibility over speed
- **Incremental**: Each module adds to a stable foundation
- **Measurable**: All changes are validated and benchmarked
- **Traceable**: All work produces experiment artifacts
- **Long-term**: Build infrastructure that lasts

---

## 🛠️ How to maintain these docs

These docs are **living documents**. Improve them as you learn:

- Found a common pitfall? Add it to the relevant guide
- Discovered a better workflow? Update the guide
- Need a new checklist? Add it to `02-CHECKLISTS.md`
- Keep docs **simple and scannable** — avoid walls of text

**Principle**: If you had to figure something out the hard way, document it so the next person (or future you) doesn't have to.


