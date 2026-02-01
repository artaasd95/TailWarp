#ifndef TAILWARP_SURVIVAL_PROBABILITY_H
#define TAILWARP_SURVIVAL_PROBABILITY_H

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <cmath>
#include <vector>

/**
 * @file survival_probability.h
 * @brief Survival Probability Risk Metric Implementation
 * 
 * This module implements the Survival Probability metric, which measures the 
 * likelihood that a financial entity remains solvent and operational over a 
 * specified time horizon.
 * 
 * Mathematical Foundation:
 * - Survival Probability: S(t) = P(τ > t), complement of probability of ruin
 * - Hazard-Based Formulation: S(t) = exp(-∫₀ᵗ γ(s)ds)
 * - Structural Barrier Model: S(t) = N(-A_t/2 + log(d)/A_t) - d·N(-A_t/2 - log(d)/A_t)
 * 
 * Where:
 *   - τ: Random time of failure
 *   - γ(t): Hazard rate (instantaneous risk of failure)
 *   - d: Distance to default (V₀/B)
 *   - A_t²: Cumulative variance = σ²·t + λ²
 *   - N: Standard normal CDF
 */

namespace tailwarp {
namespace risk_metrics {

/**
 * @enum SurvivalModelType
 * @brief Types of survival probability models
 */
enum class SurvivalModelType {
    HAZARD_INTEGRATED,      ///< Integrate hazard rate over time
    STRUCTURAL_BARRIER,     ///< Asset value vs barrier crossing (Merton-style)
    INFORMATION_RATIO,      ///< Normal CDF of Information Ratio
    HEAVY_TAILED,          ///< Power-law tail (Lindy Effect)
    RUIN_THEORY            ///< Cramér-Lundberg with filtered updates
};

/**
 * @struct SurvivalProbabilityParameters
 * @brief Parameters required for survival probability calculation
 */
struct SurvivalProbabilityParameters {
    SurvivalModelType model_type;    // Which survival model to use
    
    // Common parameters (used across models)
    float time_horizon;              // t: Time period in years (or trading days)
    float current_level;             // Current value (asset value, capital, or signal)
    float barrier_level;             // Absorbing barrier (default threshold, zero capital)
    
    // Volatility and dynamics
    float volatility;                // σ: Annualized volatility
    float mean_return;               // μ: Expected drift/return
    float jump_intensity;            // λ: Jump intensity parameter (for jump-diffusion)
    
    // For Information Ratio model
    float mean_residual_return;      // E[α]: Mean excess/residual return
    float residual_volatility;       // σ_α: Residual volatility
    
    // For heavy-tailed (Lindy) model
    float tail_exponent;             // α: Power-law tail exponent
    
    // For ruin theory (Cramér-Lundberg)
    float claim_frequency;           // λ_claims: Frequency of loss events
    float average_claim_size;        // μ_claims: Average magnitude of losses
    float premium_inflow;            // c: Premium or profit inflow rate
    
    // Filtering/updates
    bool use_filtered_estimates;     // Whether to use filtered hazard estimates
};

/**
 * @struct SurvivalProbabilityResult
 * @brief Output of survival probability calculation
 */
struct SurvivalProbabilityResult {
    float survival_probability;      // S(t) ∈ [0, 1]
    float ruin_probability;          // ψ(t) = 1 - S(t)
    float hazard_rate;               // γ(t): Instantaneous intensity
    float cumulative_hazard;         // ∫₀ᵗ γ(s)ds
    float distance_to_barrier;       // d or relative distance metric
    float expected_time_to_ruin;     // Conditional expectation of τ
    bool is_sustainable;             // Whether S(t) exceeds confidence threshold
    float confidence_margin;         // Margin above survival threshold
};

/**
 * @class SurvivalProbabilityMetric
 * @brief CPU/GPU Survival Probability metric calculator
 * 
 * Provides both CPU and GPU implementations for calculating Survival Probability
 * under multiple modeling paradigms (hazard-based, structural barrier, etc.).
 */
class SurvivalProbabilityMetric {
public:
    SurvivalProbabilityMetric();
    ~SurvivalProbabilityMetric();
    
    /**
     * @brief Calculate Survival Probability on CPU
     * @param params Survival probability parameters
     * @return SurvivalProbabilityResult containing survival metrics
     */
    SurvivalProbabilityResult calculate_cpu(const SurvivalProbabilityParameters& params) const;
    
    /**
     * @brief Calculate Survival Probability on GPU (CUDA)
     * @param params Survival probability parameters
     * @return SurvivalProbabilityResult containing survival metrics
     */
    SurvivalProbabilityResult calculate_gpu(const SurvivalProbabilityParameters& params) const;
    
    /**
     * @brief Batch calculate Survival Probability for multiple scenarios on GPU
     * @param params_array Array of survival probability parameters
     * @param count Number of scenarios
     * @return Vector of SurvivalProbabilityResult
     */
    std::vector<SurvivalProbabilityResult> calculate_gpu_batch(
        const SurvivalProbabilityParameters* params_array,
        size_t count) const;
    
    /**
     * @brief Compute cumulative hazard for integrated hazard model
     * @param mean_return μ: Expected drift
     * @param volatility σ: Volatility
     * @param time_horizon t: Time period
     * @return Cumulative hazard ∫₀ᵗ γ(s)ds
     */
    float compute_cumulative_hazard(float mean_return, 
                                    float volatility, 
                                    float time_horizon) const;
    
    /**
     * @brief Compute structural barrier survival (Merton-style)
     * @param distance_to_default d: V₀/B ratio
     * @param volatility σ: Asset volatility
     * @param time_horizon t: Time horizon
     * @return S(t) probability
     */
    float compute_structural_survival(float distance_to_default,
                                      float volatility,
                                      float time_horizon) const;
    
    /**
     * @brief Validate sustainability condition
     * @param mean_return μ: Average return
     * @param drift_premium Premium above barrier
     * @return true if drift can sustain against volatility
     */
    bool validate_sustainability_condition(float mean_return,
                                          float drift_premium) const;
};

// CUDA kernel declarations
namespace cuda_kernels {

/**
 * @brief CUDA kernel for batch survival probability calculation
 */
__global__ void survival_probability_kernel(
    const SurvivalProbabilityParameters* d_params,
    SurvivalProbabilityResult* d_results,
    size_t count);

} // namespace cuda_kernels

} // namespace risk_metrics
} // namespace tailwarp

#endif // TAILWARP_SURVIVAL_PROBABILITY_H
