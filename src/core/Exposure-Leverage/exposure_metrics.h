#ifndef TAILWARP_EXPOSURE_METRICS_H
#define TAILWARP_EXPOSURE_METRICS_H

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <cmath>
#include <vector>

/**
 * @file exposure_metrics.h
 * @brief Exposure and Leverage Risk Metrics Implementation
 * 
 * This module implements fundamental exposure and leverage metrics that measure
 * how strongly capital is committed to the market and how amplified market movements
 * affect portfolio equity.
 * 
 * Exposure is a first-order risk driver because losses scale approximately linearly
 * with position size. These metrics ensure capital commitment remains within survivable
 * limits.
 * 
 * Metrics Included:
 * 1. Gross Exposure: Total capital deployed across all positions (sum of absolute weights)
 * 2. Net Exposure: Directional bias of the portfolio (algebraic sum of weights)
 * 3. Leverage Ratio: Market exposure controlled per unit of capital buffer
 * 4. Concentration Risk: Unevenness of capital or risk distribution
 * 
 * Mathematical Foundation:
 * - Gross Exposure = Σ|w_i|
 * - Net Exposure = Σw_i
 * - Leverage = Total Notional / Equity
 * - Concentration = measure of weight/risk clustering
 */

namespace tailwarp {
namespace risk_metrics {

/**
 * @struct ExposureParameters
 * @brief Input parameters for Exposure metrics calculation
 */
struct ExposureParameters {
    const float* position_weights;   // Portfolio weights (w_i = notional_i / equity)
    size_t num_positions;            // Number of positions
    const float* position_notionals; // Optional: absolute notional values
    float total_equity;              // Portfolio equity (for leverage calculation)
};

/**
 * @struct ExposureResult
 * @brief Output of Exposure metrics calculation
 */
struct ExposureResult {
    float gross_exposure;            // Sum of |w_i|
    float net_exposure;              // Sum of w_i
    float leverage_ratio;            // Total notional / equity
    
    // Additional metrics
    size_t num_long_positions;       // Count of long positions
    size_t num_short_positions;      // Count of short positions
    float long_exposure;             // Sum of positive w_i
    float short_exposure;            // Sum of negative w_i (as absolute value)
};

/**
 * @struct ConcentrationParameters
 * @brief Input parameters for Concentration Risk calculation
 */
struct ConcentrationParameters {
    const float* position_weights;   // Portfolio weights
    size_t num_positions;            // Number of positions
    size_t top_n;                    // Number of top positions to analyze
    const float* position_betas;     // Optional: asset betas for PCTR calculation
    bool calculate_pctr;             // If true, calculate PCTR concentration
};

/**
 * @struct ConcentrationResult
 * @brief Output of Concentration Risk calculation
 */
struct ConcentrationResult {
    float top_n_concentration;       // Sum of top N absolute weights
    float herfindahl_index;          // Sum of squared weights
    float* top_n_weights;            // Array of top N weights (sorted)
    size_t* top_n_indices;           // Indices of top N positions
    
    // PCTR metrics (if calculated)
    float* pctr_values;              // Percentage contribution to risk per position
    float max_pctr;                  // Maximum single position contribution
    size_t max_pctr_index;           // Index of most risky position
    float top_n_pctr;                // Sum of top N PCTR values
};

/**
 * @class ExposureMetrics
 * @brief Calculator for portfolio exposure and leverage metrics
 * 
 * Provides both CPU and CUDA implementations for computing:
 * - Gross and Net Exposure
 * - Leverage Ratio
 * - Long/Short decomposition
 */
class ExposureMetrics {
public:
    ExposureMetrics() = default;
    ~ExposureMetrics() = default;

    /**
     * @brief Compute exposure metrics on CPU
     * @param params Input parameters
     * @return ExposureResult structure with computed metrics
     */
    ExposureResult compute_cpu(const ExposureParameters& params);

    /**
     * @brief Compute exposure metrics on GPU
     * @param params Input parameters
     * @return ExposureResult structure with computed metrics
     */
    ExposureResult compute_gpu(const ExposureParameters& params);

    /**
     * @brief Batch compute exposure metrics for multiple portfolios on GPU
     * @param params_batch Array of parameter structures
     * @param batch_size Number of portfolios
     * @return Vector of results for each portfolio
     */
    std::vector<ExposureResult> compute_batch_gpu(
        const ExposureParameters* params_batch,
        size_t batch_size
    );
};

/**
 * @class ConcentrationRisk
 * @brief Calculator for portfolio concentration metrics
 * 
 * Measures how unevenly capital or risk is distributed across positions.
 * High concentration indicates dependence on a small subset of positions,
 * reducing diversification benefits and increasing fragility.
 */
class ConcentrationRisk {
public:
    ConcentrationRisk() = default;
    ~ConcentrationRisk();

    /**
     * @brief Compute concentration metrics on CPU
     * @param params Input parameters
     * @return ConcentrationResult structure with computed metrics
     */
    ConcentrationResult compute_cpu(const ConcentrationParameters& params);

    /**
     * @brief Compute concentration metrics on GPU
     * @param params Input parameters
     * @return ConcentrationResult structure with computed metrics
     */
    ConcentrationResult compute_gpu(const ConcentrationParameters& params);

    /**
     * @brief Free memory allocated in ConcentrationResult
     * @param result Result structure to clean up
     */
    static void free_result(ConcentrationResult& result);

private:
    float* d_temp_storage_ = nullptr;
    size_t temp_storage_bytes_ = 0;
};

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * @brief Compute simple leverage ratio
 * @param total_notional Total notional exposure
 * @param equity Portfolio equity
 * @return Leverage ratio
 */
inline float compute_leverage_ratio(float total_notional, float equity) {
    if (equity <= 0.0f) return 0.0f;
    return total_notional / equity;
}

/**
 * @brief Compute gearing (alternative leverage measure)
 * Normalizes 100% long / 100% short as G=1
 * @param gross_exposure Sum of absolute weights
 * @return Gearing value
 */
inline float compute_gearing(float gross_exposure) {
    return 0.5f * gross_exposure;
}

} // namespace risk_metrics
} // namespace tailwarp

#endif // TAILWARP_EXPOSURE_METRICS_H
