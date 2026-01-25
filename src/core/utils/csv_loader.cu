#include "csv_loader.h"
#include <fstream>
#include <sstream>
#include <iostream>
#include <iomanip>
#include <stdexcept>
#include <algorithm>

namespace tailwarp {
namespace utils {

// ============================================================================
// CSVData Implementation
// ============================================================================

template<typename T>
CSVData<T>::~CSVData() {
    freeGPU();
}

template<typename T>
CSVData<T>::CSVData(CSVData&& other) noexcept
    : cpu_data(std::move(other.cpu_data)),
      d_data(other.d_data),
      rows(other.rows),
      cols(other.cols),
      gpu_rows(other.gpu_rows),
      gpu_cols(other.gpu_cols),
      column_names(std::move(other.column_names)) {
    other.d_data = nullptr;
    other.rows = 0;
    other.cols = 0;
    other.gpu_rows = 0;
    other.gpu_cols = 0;
}

template<typename T>
CSVData<T>& CSVData<T>::operator=(CSVData&& other) noexcept {
    if (this != &other) {
        freeGPU();
        cpu_data = std::move(other.cpu_data);
        d_data = other.d_data;
        rows = other.rows;
        cols = other.cols;
        gpu_rows = other.gpu_rows;
        gpu_cols = other.gpu_cols;
        column_names = std::move(other.column_names);
        other.d_data = nullptr;
        other.rows = 0;
        other.cols = 0;
        other.gpu_rows = 0;
        other.gpu_cols = 0;
    }
    return *this;
}

template<typename T>
cudaError_t CSVData<T>::toGPU(size_t chunk_start, size_t chunk_rows) {
    // Free existing GPU memory
    freeGPU();
    
    if (cpu_data.empty()) {
        return cudaSuccess;
    }
    
    // Determine chunk size
    size_t actual_rows = (chunk_rows == 0) ? (rows - chunk_start) : 
                         std::min(chunk_rows, rows - chunk_start);
    
    if (chunk_start >= rows) {
        return cudaErrorInvalidValue;
    }
    
    // Flatten data for GPU transfer
    std::vector<T> flat_data;
    flat_data.reserve(actual_rows * cols);
    
    for (size_t i = chunk_start; i < chunk_start + actual_rows; ++i) {
        flat_data.insert(flat_data.end(), 
                        cpu_data[i].begin(), 
                        cpu_data[i].end());
    }
    
    // Allocate GPU memory
    size_t total_elements = actual_rows * cols;
    cudaError_t err = cudaMalloc(&d_data, total_elements * sizeof(T));
    if (err != cudaSuccess) {
        d_data = nullptr;
        return err;
    }
    
    // Copy to GPU
    err = cudaMemcpy(d_data, flat_data.data(), 
                     total_elements * sizeof(T), 
                     cudaMemcpyHostToDevice);
    if (err != cudaSuccess) {
        cudaFree(d_data);
        d_data = nullptr;
        return err;
    }
    
    // Update GPU tracking
    gpu_rows = actual_rows;
    gpu_cols = cols;
    
    return cudaSuccess;
}

template<typename T>
void CSVData<T>::freeGPU() {
    if (d_data != nullptr) {
        cudaFree(d_data);
        d_data = nullptr;
        gpu_rows = 0;
        gpu_cols = 0;
    }
}

template<typename T>
void CSVData<T>::display(size_t max_rows, size_t max_cols) const {
    std::cout << "\n=== CSV Data Summary ===" << std::endl;
    std::cout << "Dimensions: " << rows << " rows x " << cols << " columns" << std::endl;
    
    if (!column_names.empty()) {
        std::cout << "\nColumn names: ";
        for (size_t i = 0; i < std::min(max_cols, column_names.size()); ++i) {
            std::cout << column_names[i];
            if (i < std::min(max_cols, column_names.size()) - 1) {
                std::cout << ", ";
            }
        }
        if (column_names.size() > max_cols) {
            std::cout << " ... (+" << (column_names.size() - max_cols) << " more)";
        }
        std::cout << std::endl;
    }
    
    std::cout << "\nData preview (CPU):" << std::endl;
    std::cout << std::fixed << std::setprecision(4);
    
    size_t display_rows = std::min(max_rows, rows);
    size_t display_cols = std::min(max_cols, cols);
    
    for (size_t i = 0; i < display_rows; ++i) {
        std::cout << "Row " << std::setw(4) << i << ": ";
        for (size_t j = 0; j < display_cols; ++j) {
            std::cout << std::setw(10) << cpu_data[i][j] << " ";
        }
        if (cols > max_cols) {
            std::cout << "... (+" << (cols - max_cols) << " more)";
        }
        std::cout << std::endl;
    }
    
    if (rows > max_rows) {
        std::cout << "... (+" << (rows - max_rows) << " more rows)" << std::endl;
    }
    
    std::cout << "\nGPU Status: " << (d_data != nullptr ? "Allocated" : "Not allocated") << std::endl;
    std::cout << "========================\n" << std::endl;
}

template<typename T>
void CSVData<T>::displayGPU(size_t max_rows, size_t max_cols) const {
    if (d_data == nullptr) {
        std::cout << "No data on GPU" << std::endl;
        return;
    }
    
    // Copy data back from GPU
    size_t total_elements = gpu_rows * gpu_cols;
    std::vector<T> gpu_data(total_elements);
    
    cudaError_t err = cudaMemcpy(gpu_data.data(), d_data, 
                                 total_elements * sizeof(T), 
                                 cudaMemcpyDeviceToHost);
    if (err != cudaSuccess) {
        std::cout << "Error copying from GPU: " << cudaGetErrorString(err) << std::endl;
        return;
    }
    
    std::cout << "\n=== GPU Data Preview ===" << std::endl;
    std::cout << "GPU Dimensions: " << gpu_rows << " rows x " << gpu_cols << " columns" << std::endl;
    std::cout << std::fixed << std::setprecision(4);
    
    size_t display_rows = std::min(max_rows, gpu_rows);
    size_t display_cols = std::min(max_cols, gpu_cols);
    
    for (size_t i = 0; i < display_rows; ++i) {
        std::cout << "Row " << std::setw(4) << i << ": ";
        for (size_t j = 0; j < display_cols; ++j) {
            std::cout << std::setw(10) << gpu_data[i * gpu_cols + j] << " ";
        }
        if (gpu_cols > max_cols) {
            std::cout << "... (+" << (gpu_cols - max_cols) << " more)";
        }
        std::cout << std::endl;
    }
    
    if (gpu_rows > max_rows) {
        std::cout << "... (+" << (gpu_rows - max_rows) << " more rows)" << std::endl;
    }
    std::cout << "========================\n" << std::endl;
}

// ============================================================================
// CSVLoader Implementation
// ============================================================================

CSVData<float> CSVLoader::loadFloat(const std::string& filepath, 
                                     const CSVLoaderConfig& config) {
    return loadImpl<float>(filepath, config);
}

CSVData<double> CSVLoader::loadDouble(const std::string& filepath, 
                                       const CSVLoaderConfig& config) {
    return loadImpl<double>(filepath, config);
}

std::pair<size_t, size_t> CSVLoader::getFileDimensions(
    const std::string& filepath,
    bool has_header,
    char delimiter) {
    
    std::ifstream file(filepath);
    if (!file.is_open()) {
        throw std::runtime_error("Cannot open file: " + filepath);
    }
    
    size_t rows = 0;
    size_t cols = 0;
    std::string line;
    
    // Skip header if needed
    if (has_header && std::getline(file, line)) {
        // Count columns from header
        std::stringstream ss(line);
        std::string cell;
        while (std::getline(ss, cell, delimiter)) {
            ++cols;
        }
    }
    
    // Count data rows
    while (std::getline(file, line)) {
        if (line.empty()) continue;
        
        if (cols == 0) {
            // Count columns from first data row
            std::stringstream ss(line);
            std::string cell;
            while (std::getline(ss, cell, delimiter)) {
                ++cols;
            }
        }
        ++rows;
    }
    
    return {rows, cols};
}

template<typename T>
CSVData<T> CSVLoader::loadImpl(const std::string& filepath, 
                               const CSVLoaderConfig& config) {
    CSVData<T> data;
    
    std::ifstream file(filepath);
    if (!file.is_open()) {
        throw std::runtime_error("Cannot open file: " + filepath);
    }
    
    std::string line;
    size_t current_row = 0;
    
    // Skip initial rows
    for (size_t i = 0; i < config.skip_rows; ++i) {
        if (!std::getline(file, line)) {
            throw std::runtime_error("File has fewer rows than skip_rows");
        }
    }
    
    // Read header
    if (config.has_header && std::getline(file, line)) {
        std::stringstream ss(line);
        std::string cell;
        while (std::getline(ss, cell, config.delimiter)) {
            // Trim whitespace
            cell.erase(0, cell.find_first_not_of(" \t\r\n"));
            cell.erase(cell.find_last_not_of(" \t\r\n") + 1);
            data.column_names.push_back(cell);
        }
        data.cols = data.column_names.size();
    }
    
    // Read data rows
    while (std::getline(file, line)) {
        if (line.empty()) continue;
        
        // Check chunk size limit
        if (config.chunk_size > 0 && current_row >= config.chunk_size) {
            break;
        }
        
        std::stringstream ss(line);
        std::string cell;
        std::vector<T> row_data;
        
        while (std::getline(ss, cell, config.delimiter)) {
            try {
                if constexpr (std::is_same_v<T, float>) {
                    row_data.push_back(std::stof(cell));
                } else {
                    row_data.push_back(std::stod(cell));
                }
            } catch (const std::exception& e) {
                throw std::runtime_error("Error parsing value '" + cell + 
                                       "' at row " + std::to_string(current_row) + 
                                       ": " + e.what());
            }
        }
        
        if (!row_data.empty()) {
            if (data.cols == 0) {
                data.cols = row_data.size();
            } else if (row_data.size() != data.cols) {
                throw std::runtime_error("Inconsistent number of columns at row " + 
                                       std::to_string(current_row) + 
                                       ": expected " + std::to_string(data.cols) + 
                                       ", got " + std::to_string(row_data.size()));
            }
            data.cpu_data.push_back(std::move(row_data));
            ++current_row;
        }
    }
    
    data.rows = data.cpu_data.size();
    
    std::cout << "Loaded " << data.rows << " rows x " << data.cols 
              << " columns from " << filepath << std::endl;
    
    return data;
}

// Explicit template instantiations
template class CSVData<float>;
template class CSVData<double>;

} // namespace utils
} // namespace tailwarp
