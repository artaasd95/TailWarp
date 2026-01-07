#!/bin/bash
# Build TailWarp CUDA kernels and tests

set -e

BUILD_DIR="build"
mkdir -p $BUILD_DIR

echo "Building CUDA kernels..."
# TODO: Add nvcc compilation commands
# nvcc -o $BUILD_DIR/libtailwarp.so \
#   src/core/**/*.cu \
#   -arch=sm_86 \
#   -O3 \
#   -shared \
#   -Xcompiler -fPIC

echo "Building tests..."
# TODO: Add test compilation
# g++ -o $BUILD_DIR/unit_tests tests/unit/*.cpp -lgtest -lcuda

echo "Build complete."

