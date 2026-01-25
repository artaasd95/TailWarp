#ifndef CSV_LOADER_H
#define CSV_LOADER_H

#include <string>
#include <vector>
#include <cuda_runtime.h>

namespace tailwarp {
namespace utils {

/**
 * @brief Configuration for CSV loading
 */
struct CSVLoaderConfig {
    size_t chunk_size = 0;        // 0 means load entire file
    bool has_header = true;
    char delimiter = ',';
    size_t skip_rows = 0;
};

/**
 * @brief Container for CSV data with GPU support
 */
template<typename T>
class CSVData {
public:
    std::vector<std::vector<T>> cpu_data;  // CPU-side data
    T* d_data = nullptr;                    // GPU-side data (flattened)
    size_t rows = 0;
    size_t cols = 0;
    size_t gpu_rows = 0;                   // Rows currently on GPU
    size_t gpu_cols = 0;                   // Columns currently on GPU
    std::vector<std::string> column_names;
    
    CSVData() = default;
    ~CSVData();
    
    // Delete copy constructor and assignment
    CSVData(const CSVData&) = delete;
    CSVData& operator=(const CSVData&) = delete;
    
    // Move constructor and assignment
    CSVData(CSVData&& other) noexcept;
    CSVData& operator=(CSVData&& other) noexcept;
    
    /**
     * @brief Transfer data to GPU
     * @param chunk_start Starting row for chunk (0-based)
     * @param chunk_rows Number of rows to transfer (0 = all remaining)
     * @return cudaError_t error code
     */
    cudaError_t toGPU(size_t chunk_start = 0, size_t chunk_rows = 0);
    
    /**
     * @brief Free GPU memory
     */
    void freeGPU();
    
    /**
     * @brief Display data summary
     * @param max_rows Maximum rows to display
     * @param max_cols Maximum columns to display
     */
    void display(size_t max_rows = 10, size_t max_cols = 10) const;
    
    /**
     * @brief Display GPU data (copies back from GPU)
     * @param max_rows Maximum rows to display
     * @param max_cols Maximum columns to display
     */
    void displayGPU(size_t max_rows = 10, size_t max_cols = 10) const;
};

/**
 * @brief CSV Loader with chunking support
 */
class CSVLoader {
public:
    /**
     * @brief Load CSV file into memory
     * @param filepath Path to CSV file
     * @param config Loading configuration
     * @return CSVData<float> containing the loaded data
     */
    static CSVData<float> loadFloat(const std::string& filepath, 
                                     const CSVLoaderConfig& config = CSVLoaderConfig());
    
    /**
     * @brief Load CSV file into memory (double precision)
     * @param filepath Path to CSV file
     * @param config Loading configuration
     * @return CSVData<double> containing the loaded data
     */
    static CSVData<double> loadDouble(const std::string& filepath, 
                                       const CSVLoaderConfig& config = CSVLoaderConfig());
    
    /**
     * @brief Get file dimensions without loading data
     * @param filepath Path to CSV file
     * @param has_header Whether file has header row
     * @param delimiter CSV delimiter
     * @return std::pair<size_t, size_t> (rows, cols)
     */
    static std::pair<size_t, size_t> getFileDimensions(
        const std::string& filepath,
        bool has_header = true,
        char delimiter = ',');

private:
    template<typename T>
    static CSVData<T> loadImpl(const std::string& filepath, 
                               const CSVLoaderConfig& config);
};

} // namespace utils
} // namespace tailwarp

#endif // CSV_LOADER_H
