# Simple Makefile for TailWarp (alternative to CMake)

NVCC = nvcc
CXX = g++

CUDA_ARCH = sm_86  # RTX 3060, adjust for your GPU
CUDA_FLAGS = -arch=$(CUDA_ARCH) -O3 --use_fast_math -Xcompiler -fPIC
CXX_FLAGS = -O3 -std=c++17 -fPIC

BUILD_DIR = build
SRC_DIR = src

# CUDA sources
CUDA_SRC = $(shell find $(SRC_DIR)/core -name "*.cu")
CUDA_OBJ = $(patsubst $(SRC_DIR)/%.cu,$(BUILD_DIR)/%.o,$(CUDA_SRC))

all: $(BUILD_DIR)/libtailwarp.so

$(BUILD_DIR)/libtailwarp.so: $(CUDA_OBJ)
	@mkdir -p $(dir $@)
	$(NVCC) $(CUDA_FLAGS) -shared -o $@ $^

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cu
	@mkdir -p $(dir $@)
	$(NVCC) $(CUDA_FLAGS) -c -o $@ $<

clean:
	rm -rf $(BUILD_DIR)

test:
	@echo "TODO: Compile and run tests"

.PHONY: all clean test

