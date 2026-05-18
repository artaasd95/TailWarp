// Host wrappers for risk metrics

#ifndef TAILWARP_RISK_METRICS_H
#define TAILWARP_RISK_METRICS_H

#include <vector>
#include <string>

namespace tailwarp {

// ============================================================================
// Risk Metrics Struct (Phase 1: Survival Baseline)
// ============================================================================

struct RiskMetrics {
    float var;      // Value at Risk
    float cvar;     // Conditional VaR
    float mean;
    float std_dev;
    float skewness;
    float kurtosis;
};

// ============================================================================
// Warning State Enum (S2-02)
// ============================================================================

/**
 * @enum WarningState
 * @brief Four-level warning state based on implemented Phase 1 risk primitives.
 *
 * Defined thresholds:
 * - GREEN:     All metrics healthy; proceed with planned trades
 * - YELLOW:    One metric flashing warning; optional risk reduction
 * - RED:       Multiple metrics in danger zone; mandatory risk reduction
 * - CRITICAL:  Solvency breach imminent or multiple critical metrics; emergency mode
 *
 * See docs/VALIDATION.md (S2-01 Decision Log) for full threshold definitions.
 */
enum class WarningState {
    GREEN    = 0,
    YELLOW   = 1,
    RED      = 2,
    CRITICAL = 3
};

/**
 * @struct WarningStateParams
 * @brief Input parameters for warning state computation (Phase 1 primitives only).
 *
 * All metrics must be pre-computed from implemented Phase 1 primitives:
 * - solvency_distance: Distance to ruin (in standard deviations)
 * - max_drawdown: Historical maximum drawdown (as decimal, e.g., 0.35 for 35%)
 * - gross_exposure: Total long + short notional / equity
 * - cvar_95: Conditional VaR at 95% confidence (as decimal, e.g., -0.15 for -15%)
 *
 * Thresholds are deterministic per docs/VALIDATION.md.
 */
struct WarningStateParams {
    float solvency_distance;   // Distance to ruin in σ
    float max_drawdown;        // As decimal (0 to 1)
    float gross_exposure;      // Leverage ratio
    float cvar_95;             // As decimal (negative for losses)
};

/**
 * @struct WarningStateResult
 * @brief Output from warning state computation.
 *
 * Fields:
 * - state: Overall warning state (GREEN/YELLOW/RED/CRITICAL)
 * - reason: Human-readable explanation of the state
 * - triggered_metrics: Bitmask of which metrics triggered (0=solvency, 1=drawdown, 2=exposure, 3=cvar)
 *
 * Example:
 *   WarningStateResult result = compute_warning_state(params);
 *   if (result.state == WarningState::CRITICAL) {
 *     printf("EMERGENCY: %s\n", result.reason.c_str());
 *   }
 */
struct WarningStateResult {
    WarningState state;
    std::string reason;
    int triggered_metrics;  // Bitmask: bit 0=solvency, 1=drawdown, 2=exposure, 3=cvar
};

// ============================================================================
// Host API (Phase 1: Survival Baseline)
// ============================================================================

// Historical VaR: (1-alpha) lower tail threshold on sorted returns (PnL convention).
float compute_var(const std::vector<float>& returns, float alpha = 0.95f);

// Expected shortfall / CVaR: mean of the worst (1-alpha) fraction (sorted ascending).
float compute_cvar(const std::vector<float>& returns, float alpha = 0.95f);

// Compute full risk metrics
RiskMetrics compute_risk_metrics(const std::vector<float>& returns, float alpha = 0.95f);

// ============================================================================
// Warning State Computation (S2-02)
// ============================================================================

/**
 * @fn compute_warning_state
 * @brief Deterministic warning state computation from Phase 1 primitives.
 *
 * Algorithm:
 * 1. Check each metric against green/yellow/red/critical thresholds
 * 2. If any metric is CRITICAL → return CRITICAL
 * 3. If multiple metrics are RED → return RED
 * 4. If any metric is RED → return RED
 * 5. If any metric is YELLOW → return YELLOW
 * 6. Otherwise → return GREEN
 *
 * Thresholds (defined in docs/VALIDATION.md, S2-01 Decision Log):
 *   Solvency Distance:  GREEN (>3σ), YELLOW (2-3σ), RED (1-2σ), CRITICAL (≤1σ)
 *   Max Drawdown:       GREEN (<20%), YELLOW (20-40%), RED (40-60%), CRITICAL (≥60%)
 *   Gross Exposure:     GREEN (<3x), YELLOW (3-5x), RED (5-8x), CRITICAL (≥8x)
 *   CVaR @ 95%:         GREEN (>-10%), YELLOW (-10% to -15%), RED (-15% to -25%), CRITICAL (≤-25%)
 *
 * @param params Input parameters (solvency_distance, max_drawdown, gross_exposure, cvar_95)
 * @return WarningStateResult with state, reason, and triggered_metrics bitmask
 *
 * Example usage:
 *   WarningStateParams params = {
 *     .solvency_distance = 2.5f,  // 2.5 std-devs to ruin → YELLOW
 *     .max_drawdown = 0.35f,       // 35% drawdown → YELLOW
 *     .gross_exposure = 4.0f,      // 4x leverage → YELLOW
 *     .cvar_95 = -0.12f            // -12% CVaR → YELLOW
 *   };
 *   auto result = compute_warning_state(params);
 *   // result.state == WarningState::YELLOW
 */
WarningStateResult compute_warning_state(const WarningStateParams& params);

}  // namespace tailwarp

#endif  // TAILWARP_RISK_METRICS_H

