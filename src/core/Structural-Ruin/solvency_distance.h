#ifndef TAILWARP_SOLVENCY_DISTANCE_H
#define TAILWARP_SOLVENCY_DISTANCE_H

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <cmath>
#include <vector>

/**
 * @file solvency_distance.h
 * @brief Solvency Distance (Distance to Ruin) Metric Implementation
 * 
 * This module implements the Solvency Distance metric, which measures how close a financial
 * entity or strategy is to an unrecoverable state (absorbing barrier). Rather than calculating
 * abstract probabilities, it translates risk into a concrete budget-like metric.
 * 
 * Mathematical Foundation:
 * Solvency Distance = Current Capital (u) / CVaR-scale Loss
 * 
 * Key Concepts:
 * - Structural Survival: Focuses on boundary conditions rather than ensemble averages
 * - CVaR as Unit: Uses tail risk (CVaR) as the measurement unit instead of standard deviation
 * - Non-Ergodic Framework: Prioritizes path-dependent survival over probabilistic outcomes
 * - Budgeting for Catastrophe: Answers "How many extreme hits can we take?"
 * 
 * Philosophy:
 * In fat-tailed environments, standard deviation is often deceptive. This metric ignores
 * day-to-day noise and instead measures the buffer against catastrophic collapse using
 * the scale of extreme events (CVaR). If Solvency Distance = 3, the portfolio can survive
 * three consecutive average tail events before hitting the absorbing barrier.
 */

namespace tailwarp {
namespace risk_metrics {

/**
 * @struct SolvencyDistanceParameters
 * @brief Input parameters for Solvency Distance calculation
 */
struct SolvencyDistanceParameters {
    float current_equity;           // Current marked-to-market portfolio value
    float absorbing_barrier;        // Ruin threshold (e.g., 0, margin call level, regulatory minimum)
    float cvar_scale;              // CVaR magnitude: E[L | L >= VaR_α] - average tail loss
    float confidence_level;        // α for CVaR calculation (e.g., 0.95 or 0.99)
    
    // Optional: Additional context for enhanced analysis
    float var_threshold;           // Value at Risk at confidence level (optional)
    float current_volatility;      // Current market volatility (optional, for context)
};

/**
 * @struct SolvencyDistanceResult
 * @brief Output of Solvency Distance calculation
 */
struct SolvencyDistanceResult {
    float solvency_distance;           // Primary metric: buffer / CVaR (dimensionless count)
    float current_capital_buffer;      // u = current_equity - absorbing_barrier
    float cvar_normalized_buffer;      // Buffer expressed in CVaR units
    
    // Risk classification
    bool is_fragile;                   // True if distance < fragility_threshold
    bool is_critical;                  // True if distance < critical_threshold
    float risk_score;                  // Normalized score: 0 (critical) to 1 (safe)
    
    // Actionable thresholds
    float green_threshold;             // Safe zone: distance > green (e.g., 5)
    float yellow_threshold;            // Warning zone: yellow < distance < green (e.g., 3)
    float red_threshold;               // Critical zone: distance < red (e.g., 1)
    
    // Diagnostic information
    float distance_to_var;             // How close to VaR threshold (if provided)
    float relative_buffer_ratio;       // buffer / initial_capital (percentage)
};

/**
 * @struct SolvencyDistanceConfig
 * @brief Configuration for Solvency Distance thresholds and behavior
 */
struct SolvencyDistanceConfig {
    float green_threshold = 5.0f;      // Safe: Can absorb 5+ tail events
    float yellow_threshold = 3.0f;     // Warning: Can absorb 3-5 tail events
    float red_threshold = 1.0f;        // Critical: Can absorb < 1 tail event
    
    bool enable_dynamic_thresholds = false;  // Adjust thresholds based on volatility regime
    float volatility_scaling_factor = 1.0f;  // Scale thresholds by volatility (if enabled)
};

/**
 * @class SolvencyDistance
 * @brief CPU/GPU Solvency Distance metric calculator
 * 
 * Implements distance-to-ruin calculation using CVaR as the measurement unit.
 * Provides both single-calculation and batch-processing capabilities.
 */
class SolvencyDistance {
public:
    SolvencyDistance();
    explicit SolvencyDistance(const SolvencyDistanceConfig& config);
    ~SolvencyDistance();
    
    /**
     * @brief Calculate Solvency Distance on CPU
     * @param params Input parameters for calculation
     * @return SolvencyDistanceResult containing distance metric and risk classification
     */
    SolvencyDistanceResult calculate_cpu(const SolvencyDistanceParameters& params) const;
    
    /**
     * @brief Calculate Solvency Distance on GPU (CUDA)
     * @param params Input parameters for calculation
     * @return SolvencyDistanceResult containing distance metric and risk classification
     */
    SolvencyDistanceResult calculate_gpu(const SolvencyDistanceParameters& params) const;
    
    /**
     * @brief Batch calculate Solvency Distance for multiple scenarios on GPU
     * @param params_array Array of input parameters
     * @param count Number of scenarios
     * @return Vector of SolvencyDistanceResult
     */
    std::vector<SolvencyDistanceResult> calculate_gpu_batch(
        const SolvencyDistanceParameters* params_array,
        size_t count) const;
    
    /**
     * @brief Update configuration thresholds
     * @param config New configuration
     */
    void set_config(const SolvencyDistanceConfig& config);
    
    /**
     * @brief Get current configuration
     * @return Current configuration
     */
    SolvencyDistanceConfig get_config() const;
    
    /**
     * @brief Validate input parameters
     * @param params Parameters to validate
     * @return true if parameters are valid, false otherwise
     */
    static bool validate_parameters(const SolvencyDistanceParameters& params);
    
    /**
     * @brief Calculate CVaR from loss distribution (helper function)
     * @param losses Array of loss values
     * @param count Number of loss values
     * @param confidence_level α for CVaR (e.g., 0.95)
     * @return CVaR value (Expected Shortfall)
     */
    static float calculate_cvar_from_losses(const float* losses,
                                            size_t count,
                                            float confidence_level);

private:
    SolvencyDistanceConfig config_;
    
    // Internal helper methods
    void classify_risk(SolvencyDistanceResult& result, float distance) const;
    float calculate_risk_score(float distance) const;
};

// CUDA kernel declarations
namespace cuda_kernels {

/**
 * @brief CUDA kernel for batch Solvency Distance calculation
 * 
 * Each thread processes one scenario independently.
 * Computes:
 *   1. Current capital buffer (u)
 *   2. Solvency Distance = buffer / CVaR
 *   3. Risk classification (fragile, critical, safe)
 *   4. Actionable thresholds and scores
 */
__global__ void solvency_distance_kernel(const SolvencyDistanceParameters* d_params,
                                         SolvencyDistanceResult* d_results,
                                         const SolvencyDistanceConfig* d_config,
                                         size_t count);

/**
 * @brief Device function to compute solvency distance
 * 
 * Core calculation: distance = (current_equity - barrier) / cvar_scale
 */
__device__ inline float compute_solvency_distance(float current_equity,
                                                  float absorbing_barrier,
                                                  float cvar_scale);

/**
 * @brief Device function to classify risk level
 * 
 * Determines if portfolio is in green/yellow/red zone based on distance
 */
__device__ inline void classify_risk_level(float distance,
                                          const SolvencyDistanceConfig* config,
                                          bool& is_fragile,
                                          bool& is_critical,
                                          float& risk_score);

/**
 * @brief Device function to compute normalized risk score
 * 
 * Maps distance to [0, 1] where 0 = critical, 1 = safe
 * Uses sigmoid-like function for smooth transitions
 */
__device__ inline float compute_risk_score(float distance,
                                          float red_threshold,
                                          float green_threshold);

} // namespace cuda_kernels

} // namespace risk_metrics
} // namespace tailwarp

#endif // TAILWARP_SOLVENCY_DISTANCE_H
