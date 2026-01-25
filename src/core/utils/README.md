# Core Utilities

This directory contains utility functions and helpers for the TailWarp project.

## CSV Loader

`csv_loader.h/cu` - A utility for loading CSV files with GPU support and chunking capabilities.

### Features

- Load CSV files into CPU memory
- Transfer data to GPU with optional chunking
- Support for both float and double precision
- Display data preview (CPU and GPU)
- Configurable CSV parsing (delimiter, header, skip rows)
- Memory-efficient chunked loading for large files

### Usage Example

```cpp
#include "csv_loader.h"

using namespace tailwarp::utils;

// Basic usage - load entire file
CSVData<float> data = CSVLoader::loadFloat("data/input/sample_returns.csv");
data.display();  // Show data preview

// Transfer to GPU
cudaError_t err = data.toGPU();
if (err == cudaSuccess) {
    data.displayGPU();  // Show GPU data
}

// Chunked loading
CSVLoaderConfig config;
config.chunk_size = 10000;  // Load only 10k rows
config.has_header = true;
config.delimiter = ',';

CSVData<double> chunked = CSVLoader::loadDouble("large_file.csv", config);

// Transfer specific chunk to GPU
chunked.toGPU(0, 1000);  // Transfer first 1000 rows

// Clean up
data.freeGPU();
```

### Configuration Options

- `chunk_size`: Number of rows to load (0 = load all)
- `has_header`: Whether CSV has a header row
- `delimiter`: CSV delimiter character
- `skip_rows`: Number of initial rows to skip

### API Reference

#### CSVLoader

- `loadFloat()`: Load CSV as float precision
- `loadDouble()`: Load CSV as double precision
- `getFileDimensions()`: Get file size without loading

#### CSVData<T>

- `toGPU()`: Transfer data to GPU (supports chunking)
- `freeGPU()`: Free GPU memory
- `display()`: Show CPU data preview
- `displayGPU()`: Show GPU data preview

## Other Utilities

- `sorting.cu` - GPU sorting algorithms
