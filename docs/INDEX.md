# TailWarp Documentation Index

Complete navigation for all TailWarp documentation.

---

## 🚀 Start Here (New to the Repo?)

1. **Read the main project plan**: `../project-plan-init.md`
2. **Read the first-week guide**: `project-plan-docs/00-START-HERE.md`
3. **Skim the quick reference**: `project-plan-docs/QUICK-REFERENCE.md`

---

## 📚 Core Specifications

These define the "rules of the game" for TailWarp:

| Document | Purpose |
|----------|---------|
| **`EXPERIMENTS.md`** | Experiment structure, provenance, reproducibility standards |
| **`VALIDATION.md`** | Validation levels (0–4), correctness criteria, reference implementations |

---

## 🛠️ Operational Guides

Step-by-step guides for common tasks:

| Document | When to Use |
|----------|-------------|
| **`project-plan-docs/00-START-HERE.md`** | First week, core workflow, quick answers |
| **`project-plan-docs/01-RD-PHASES.md`** | Planning next steps, understanding roadmap |
| **`project-plan-docs/02-CHECKLISTS.md`** | Every time you add a module or commit code |
| **`project-plan-docs/03-ADD-A-MODULE.md`** | Integrating new kernels, metrics, data sources |
| **`project-plan-docs/04-RESEARCH-WORKFLOW.md`** | Designing and running experiments |
| **`project-plan-docs/05-EXPERIMENT-REVIEW.md`** | Deciding if results are trustworthy/publishable |
| **`project-plan-docs/06-PERFORMANCE-PROTOCOL.md`** | Benchmarking and preventing regressions |

---

## 📖 Reference Materials

| Document | Purpose |
|----------|---------|
| **`project-plan-docs/QUICK-REFERENCE.md`** | One-page summary of everything (print this!) |
| **`project-plan-docs/README.md`** | Navigation hub for project-plan-docs |
| **`project-plan-docs/SUMMARY.md`** | Explains how all the docs fit together |

---

## 🎯 Navigation by Task

### "I want to start working on TailWarp"
→ `project-plan-docs/00-START-HERE.md`

### "I want to add a new distribution (e.g., Student-t)"
→ `project-plan-docs/03-ADD-A-MODULE.md`  
→ Use checklist from `project-plan-docs/02-CHECKLISTS.md`

### "I want to answer a research question"
→ `project-plan-docs/04-RESEARCH-WORKFLOW.md`

### "I want to know what to build next"
→ `project-plan-docs/01-RD-PHASES.md`

### "I want to verify my code is correct"
→ `VALIDATION.md`  
→ Use checklist from `project-plan-docs/02-CHECKLISTS.md`

### "I want to check performance"
→ `project-plan-docs/06-PERFORMANCE-PROTOCOL.md`

### "I want to review experiment results"
→ `project-plan-docs/05-EXPERIMENT-REVIEW.md`

### "I need a quick reference"
→ `project-plan-docs/QUICK-REFERENCE.md`

---

## 📝 Research Outputs

| Location | Contents |
|----------|----------|
| **`research_notes/`** | Research findings, experiment summaries, paper drafts (start with `research_notes/INDEX.md`) |
| **`../data/output/experiments/`** | All experiment runs (timestamped folders) |

---

## 🔄 The Core Workflow

```
┌─────────────────────────────────────────────────────────┐
│  1. Formulate   →  2. Implement  →  3. Validate         │
│       ↑                                    ↓             │
│  5. Record      ←  4. Benchmark  ←─────────┘             │
└─────────────────────────────────────────────────────────┘
```

- **Step 1**: `project-plan-docs/04-RESEARCH-WORKFLOW.md`
- **Step 2**: `project-plan-docs/03-ADD-A-MODULE.md`
- **Step 3**: `VALIDATION.md` + `project-plan-docs/02-CHECKLISTS.md`
- **Step 4**: `project-plan-docs/06-PERFORMANCE-PROTOCOL.md`
- **Step 5**: `EXPERIMENTS.md`

---

## 💡 Key Principles

1. **Research-first**: Correctness and reproducibility over speed
2. **Incremental**: Build on stable foundations
3. **Measurable**: Validate and benchmark everything
4. **Traceable**: Produce experiment artifacts
5. **Reproducible**: Capture provenance (git hash, config, hardware)

---

## 🆘 Common Questions

### "Where do I start?"
Read `project-plan-docs/00-START-HERE.md`

### "What's the folder structure?"
See `../project-plan-init.md` Section 7

### "How do I know if my code is correct?"
Read `VALIDATION.md` (levels 0–4)

### "How do I run an experiment?"
Read `project-plan-docs/04-RESEARCH-WORKFLOW.md`

### "What should I build next?"
Read `project-plan-docs/01-RD-PHASES.md`

### "Is my performance OK?"
Read `project-plan-docs/06-PERFORMANCE-PROTOCOL.md`

### "Are my results publishable?"
Read `project-plan-docs/05-EXPERIMENT-REVIEW.md`

---

## 📦 Complete File Tree

```
docs/
├── INDEX.md (this file)
├── EXPERIMENTS.md
├── VALIDATION.md
├── project-plan-docs/
│   ├── README.md
│   ├── SUMMARY.md
│   ├── QUICK-REFERENCE.md
│   ├── 00-START-HERE.md
│   ├── 01-RD-PHASES.md
│   ├── 02-CHECKLISTS.md
│   ├── 03-ADD-A-MODULE.md
│   ├── 04-RESEARCH-WORKFLOW.md
│   ├── 05-EXPERIMENT-REVIEW.md
│   └── 06-PERFORMANCE-PROTOCOL.md
└── research_notes/
    ├── README.md
    └── INDEX.md
```

---

## 🔧 Maintaining This Documentation

These docs are **living documents**. Update them as you learn:

- Found a pitfall? Add it to the relevant guide
- Better workflow? Update the guide
- New checklist needed? Add to `project-plan-docs/02-CHECKLISTS.md`

**Principle**: Document hard-won lessons so others (or future you) don't repeat them.

---

## 📊 Documentation Maturity

| Component | Status |
|-----------|--------|
| Core specs (EXPERIMENTS, VALIDATION) | ✅ Complete |
| Operational guides | ✅ Complete |
| Checklists | ✅ Complete |
| Phase roadmap | ✅ Complete |
| Quick reference | ✅ Complete |
| Research notes | 🔄 Grows with project |

---

**Remember**: This documentation is infrastructure. Maintain it like you maintain code.

Start with `project-plan-docs/00-START-HERE.md` and follow the guides. You've got this! 🚀

