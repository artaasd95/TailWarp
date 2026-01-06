# Project 2: Geometric Methods for Risk and Optimization (Riemannian manifolds)

## Goal
- Use geometric optimization to model, measure, and control risk with structures aligned to the data (e.g., SPD covariance manifold, Fisher‑Rao information geometry, hyperbolic embeddings). Apply geodesic convexity, Riemannian gradients, and manifold constraints to build robust, tail‑aware methods for pricing, sizing, hedging, and portfolio allocation.

## Where and how to start
- Identify the manifold per object:
  - Covariance/correlation matrices → SPD manifold with affine‑invariant or log‑Euclidean metric.
  - Probability distributions → statistical manifold with Fisher‑Rao metric (information geometry).
  - Hierarchical/tail structures → hyperbolic geometry (Poincaré ball) for embeddings if modeling hierarchy or tree‑like risk cascades.
- Define the optimization problem on the right geometry:
  - Position sizing under CVaR constraint → geodesic convex feasible set on returns/covariance space.
  - Hedging with correlation uncertainty → Riemannian trust region on SPD manifold.
  - Regime blending → Riemannian barycenter (Fréchet mean) of multiple covariance regimes.

## Reading list (start here)
- Statistical Consequences of Fat Tails:
  - Ch 3.10: Focus on payoff functions g(x), convexity/fragility (connect to geodesic convexity).
  - Ch 2.2.19 and Ch 13.3: CVaR vs VaR and error propagation (motivate robust objective/constraints).
  - Ch 8: κ metric (drives sample size for geometric estimators).
  - Ch 9: EVT and shadow mean (robustification for estimation under hidden tails).
  - Ch 30: Tail constraints and maximum entropy (formalize conservative feasible sets).
  - Ch 26/27/25: Heuristics for options under power laws and unique measure (anchor‑based pricing ties into robust geometric calibration).
- Geometry/Optimization references:
  - Absil, Mahony, Sepulchre: Optimization Algorithms on Matrix Manifolds (canonical).
  - Sra, Hosseini, and others: Riemannian optimization and geometry of SPD matrices.
  - Amari: Information Geometry and natural gradient; Fisher‑Rao metric.
  - Bonnabel: Stochastic Approximation on Riemannian Manifolds (SGD on manifolds).
  - Nickel & Kiela: Poincaré embeddings (hyperbolic geometry for hierarchical relations).
  - Tyler's M‑estimator and robust covariance under heavy tails.

## Specific trade/position risk calculations via geometric methods
- Position risk via scenario CVaR:
  - Generate heavy‑tailed return scenarios for the underlying; compute payoff g(x); estimate CVaR. Use κ to set N scenarios; validate tails via EVT.
- Robust covariance estimation:
  - For portfolios/hedges, estimate covariance with Tyler's M‑estimator; represent in SPD manifold (affine‑invariant metric).
  - Blend regimes via Riemannian barycenters for robustness; avoid linear mixing artifacts.
- Geodesic convex constraints:
  - Encode tail risk constraints (max CVaR, max drawdown) as feasible sets; perform Riemannian projected gradient or trust‑region steps on manifold‑constrained variables (e.g., correlation matrices).
- Hedging under correlation uncertainty:
  - Treat correlation as a point on SPD; optimize hedge ratios with Riemannian gradient descent, projecting to PD cone and maintaining manifold feasibility.
- Option pricing under power laws:
  - Use anchor price + tail index α (Ch 27) to build tail‑robust pricing heuristic; calibrate α via EVT.
  - Quantify convexity/fragility by curvature: relate benefit/harm from uncertainty to local geometry of g(x).

## Training/optimization plan
- Start with SPD manifold optimization:
  - Implement Riemannian gradient/descent/retraction for SPD (affine‑invariant or log‑Euclidean).
  - Add trust region and line search respecting manifold geodesics.
- Add robust estimators and constraints:
  - Tyler's M‑estimator; EVT‑based tail index estimation; κ‑based sample sizing.
  - Constraint handling via geodesic projections or barrier penalties (tail risk constraints).
- Integrate information geometry:
  - Use natural gradient where the parameter space is probabilistic (Fisher‑Rao metric for distribution parameters).
  - Apply mirror descent variants with geometry suited to the risk functional (e.g., entropic constraints from Ch 30).
- Optional: Hyperbolic geometry for hierarchy/tails:
  - If modeling hierarchical risk cascades, embed exposures in hyperbolic spaces; use geodesic distances to measure propagation.

## R&D roadmap and gates
- Gate A (Manifold toolkit ready):
  - SPD manifold ops implemented (exp/log, retraction, geodesic distance, projection to PD cone); unit tests verified.
- Gate B (Robust covariance + CVaR sizing pipeline):
  - End‑to‑end: robust covariance → scenario generation → g(x) → CVaR → size/hedge decision; EVT/κ integrated; artifacts reproducible.
- Gate C (Constraint enforcement):
  - Geodesic convex tail constraints enforced; optimization converges; CVaR limit respected across multiple seeds and regimes.
- Gate D (Anchor‑based tail option pricing):
  - α estimated via EVT; anchor price applied; pricing stable under sample shifts; documentation of failures vs Gaussian models.
- Gate E (Portfolio/hedge robustness):
  - Riemannian barycenters across regimes beat Euclidean baselines in drawdown and tail CVaR across stress tests.

## Implementation suggestions
- Use TailWarp (or CPU fallback) to provide:
  - Heavy‑tailed scenario generation (Student‑t, α‑stable).
  - EVT POT routines and tail index estimation.
  - Risk metric calculator (CVaR) with warp‑level sorting (GPU) or efficient CPU sort.
- Build a small geometric library:
  - SPD manifold: expm/logm, retractions (Cholesky), geodesic distance, projection to PD cone.
  - Information geometry: Fisher information matrices, natural gradient update.
- Validation:
  - Property tests (manifold operations close under composition; PD preserved).
  - Statistical tests (CVaR estimates converge with N and κ; EVT tail index stable).
  - End‑to‑end sanity (geometric methods outperform Euclidean baselines under tail stress).

## Pitfalls to avoid
- Using Euclidean averaging for covariance across regimes; prefer Riemannian barycenters.
- Ignoring EVT when calibrating α; anchor pricing needs tail validation.
- Over‑trusting sample covariance under heavy tails; adopt robust estimators.
- Treating constraints as soft without verifying ex‑post compliance; build hard projections or trust regions.

## Outputs
- Risk sizing/hedging recommendations with:
  - CVaR estimates, constraint compliance, drawdown profiles.
  - Robust covariance and regime barycenters (with geodesic distances).
  - Confidence flags from κ and EVT diagnostics.
  - Pricing and risk comparisons (power‑law anchors vs Gaussian) for specific options/trades.