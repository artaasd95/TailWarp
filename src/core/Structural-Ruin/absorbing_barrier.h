#ifndef TAILWARP_ABSORBING_BARRIER_H
#define TAILWARP_ABSORBING_BARRIER_H

#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <cmath>
#include <vector>

/**
 * @file absorbing_barrier.h
 * @brief Absorbing Barrier (Ruin State) Metric Implementation
 * 
 * This module implements the Absorbing Barrier concept, treating ruin as a "hard constraint"
 * or "point of no return." Once crossed, the operation terminates permanently with zero 
 * recovery probability.
 * 
 * Mathematical Foundations:
 * 1. Stopping Time: τ = inf{t > 0; X_t < L}
 * 2. Cramér-Lundberg Model: U(t) = u + ct - S(t)
 * 3. Markov Chain Absorption: p_{i,i} = 1 (once in absorbing state, cannot exit)
 * 4. Force of Mortality: μ(τ) = -d/dτ log(S(τ))
 * 
 * Key Concepts:
 * - Path Dependence: Focuses on sequential probability (time) vs. ensemble probability
 * - Distance to Ruin: How many CVaR-scale losses before absorption
 * - Survival Trajectory: Remaining life expectancy using Lindy Effect
 * - Ergodicity Breakdown: Detection of non-ergodic states where single extreme events matter more
 */

namespace tailwarp {
namespace risk_metrics {

/**
 * @struct AbsorbingBarrierParameters
 * @brief Parameters for Absorbing Barrier calculation
 */
struct AbsorbingBarrierParameters {
    float initial_capital;      // u: Starting capital/resource level
    float inflow_rate;          // c: Rate of premium/revenue/profit generation
    float barrier_level;        // L: Ruin threshold (typically 0, can be any critical minimum)
    float current_value;        // X_t: Current portfolio/system value
    float cvar_scale;          // CVaR magnitude (loss scale) for distance measurement
    float time_horizon;        // T: Time period for trajectory analysis (in periods/steps)
    float loss_frequency;      // λ: Average frequency of loss events
    float average_loss;        // μ_loss: Average magnitude of loss per event
};

/**
 * @struct AbsorbingBarrierResult
 * @brief Output of Absorbing Barrier calculation
 */
struct AbsorbingBarrierResult {
    float distance_to_barrier;      // Current surplus: U(t) = current_value - barrier_level
    float distance_in_cvar_units;   // Distance measured as multiples of CVaR losses
    float stopping_time_estimate;   // τ: Estimated stopping time (periods until barrier hit)
    float hazard_rate;              // μ(τ): Force of mortality at current state
    float survival_probability;     // S(τ): Probability of survival over horizon
    float lindy_expectancy;         // Remaining expected life using Lindy Effect
    bool is_ergodic;               // Whether system is in ergodic vs non-ergodic regime
    float ergodicity_metric;       // Score indicating ergodicity breakdown (0=ergodic, 1=non-ergodic)
    bool net_profit_valid;         // c > λ * μ_loss (sufficient inflow to cover average losses)
    float surplus_trajectory;      // Expected surplus at horizon: u + c*T - λ*μ_loss*T
};

/**
 * @class AbsorbingBarrier
 * @brief CPU/GPU Absorbing Barrier metric calculator
 * 
 * Implements barrier monitoring, stopping time estimation, hazard rate calculation,
 * and Lindy-based survival trajectory analysis.
 */
class AbsorbingBarrier {
public:
    AbsorbingBarrier();
    ~AbsorbingBarrier();
    
    /**
     * @brief Calculate Absorbing Barrier metrics on CPU
     * @param params Absorbing Barrier parameters
     * @return AbsorbingBarrierResult containing barrier distance, hazard rate, and survival metrics
     */
    AbsorbingBarrierResult calculate_cpu(const AbsorbingBarrierParameters& params) const;
    
    /**
     * @brief Calculate Absorbing Barrier metrics on GPU (CUDA)
     * @param params Absorbing Barrier parameters
     * @return AbsorbingBarrierResult containing barrier distance, hazard rate, and survival metrics
     */
    AbsorbingBarrierResult calculate_gpu(const AbsorbingBarrierParameters& params) const;
    
    /**
     * @brief Batch calculate Absorbing Barrier for multiple scenarios on GPU
     * @param params_array Array of Absorbing Barrier parameters
     * @param count Number of scenarios
     * @return Vector of AbsorbingBarrierResult
     */
    std::vector<AbsorbingBarrierResult> calculate_gpu_batch(
        const AbsorbingBarrierParameters* params_array, 
        size_t count) const;
    
    /**
     * @brief Check if system can generate sufficient profit to offset losses
     * @param inflow_rate c: Rate of revenue/premium
     * @param loss_frequency λ: Frequency of losses
     * @param average_loss μ_loss: Average loss magnitude
     * @return true if c > λ * μ_loss (sustainable)
     */
    bool validate_net_profit_condition(float inflow_rate, 
                                       float loss_frequency, 
                                       float average_loss) const;
    
    /**
     * @brief Estimate stopping time (periods until barrier hit)
     * @param current_distance Current distance to barrier
     * @param drift Rate of drift away from barrier (can be negative for hazardous systems)
     * @param volatility Volatility of the process
     * @return Estimated time to hit barrier
     */
    float estimate_stopping_time(float current_distance, 
                                 float drift, 
                                 float volatility) const;
    
    /**
     * @brief Calculate Lindy expectancy (Taleb's concept of remaining life)
     * @param age Current time distance from absorption (life so far)
     * @param confidence_factor Adjustment for uncertainty
     * @return Expected remaining life using Lindy Effect
     */
    float calculate_lindy_expectancy(float age, float confidence_factor = 1.0f) const;
};

// CUDA kernel declarations
namespace cuda_kernels {

/**
 * @brief CUDA kernel for Absorbing Barrier calculation
 * 
 * Each thread processes one scenario independently.
 * Computes:
 *   1. Current distance to barrier
 *   2. Distance in CVaR units
 *   3. Stopping time estimate
 *   4. Hazard rate (force of mortality)
 *   5. Survival probability
 *   6. Lindy expectancy
 *   7. Ergodicity detection
 */
__global__ void absorbing_barrier_kernel(const AbsorbingBarrierParameters* d_params,
                                         AbsorbingBarrierResult* d_results,
                                         size_t count);

/**
 * @brief Device function to compute stopping time
 * 
 * τ = inf{t > 0; X_t < L}
 * Estimated using Brownian motion first-passage time approximation
 */
__device__ inline float compute_stopping_time(float current_distance, 
                                              float drift, 
                                              float volatility);

/**
 * @brief Device function to compute hazard rate (force of mortality)
 * 
 * μ(τ) = -d/dτ log(S(τ))
 * Measures instantaneous risk of hitting barrier at time τ
 */
__device__ inline float compute_hazard_rate(float stopping_time, 
                                           float current_distance,
                                           float volatility);

/**
 * @brief Device function to compute survival probability
 * 
 * S(τ) = 1 - Φ(-stopping_time / (2 * volatility))
 * Probability of surviving to time τ without hitting barrier
 */
__device__ inline float compute_survival_probability(float stopping_time);

/**
 * @brief Device function to detect ergodicity breakdown
 * 
 * Compares tail impact vs. diffusion impact:
 * If tail risk dominates (non-ergodic), single extreme event > series of small losses
 */
__device__ inline float compute_ergodicity_metric(float cvar_scale, 
                                                 float volatility,
                                                 float loss_frequency,
                                                 float average_loss);

} // namespace cuda_kernels

} // namespace risk_metrics
} // namespace tailwarp

#endif // TAILWARP_ABSORBING_BARRIER_H
