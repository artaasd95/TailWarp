cmake_minimum_required(VERSION 3.18)
project(TailWarp CUDA CXX)

# CUDA setup
find_package(CUDA REQUIRED)
set(CMAKE_CUDA_STANDARD 14)
set(CMAKE_CXX_STANDARD 17)

# CUDA architecture (adjust for your GPU)
set(CMAKE_CUDA_ARCHITECTURES 86)  # RTX 3060

# Include directories
include_directories(
    ${CMAKE_SOURCE_DIR}/src
    ${CUDA_INCLUDE_DIRS}
)

# CUDA kernels library
file(GLOB_RECURSE CUDA_SOURCES 
    src/core/**/*.cu
    src/core/*.cu
)

add_library(tailwarp_kernels SHARED ${CUDA_SOURCES})
target_link_libraries(tailwarp_kernels ${CUDA_LIBRARIES})

# Host wrappers library
file(GLOB_RECURSE CPP_SOURCES
    src/wrappers/*.cpp
    src/algorithms/*.cpp
)

add_library(tailwarp SHARED ${CPP_SOURCES})
target_link_libraries(tailwarp tailwarp_kernels)

# Tests (requires GTest)
option(BUILD_TESTS "Build test suite" ON)
if(BUILD_TESTS)
    find_package(GTest)
    if(GTest_FOUND)
        file(GLOB_RECURSE TEST_SOURCES tests/**/*.cpp)
        add_executable(tailwarp_tests ${TEST_SOURCES})
        target_sources(tailwarp_tests PRIVATE
            ${CMAKE_SOURCE_DIR}/src/reference/student_t_cpu.cpp
        )
        target_link_libraries(tailwarp_tests 
            tailwarp 
            tailwarp_kernels
            GTest::GTest 
            GTest::Main
        )
        enable_testing()
        add_test(NAME TailWarpTests COMMAND tailwarp_tests)
        add_test(NAME gpu_smoke COMMAND tailwarp_tests --gtest_filter=GpuSmoke.*)
        set_tests_properties(gpu_smoke PROPERTIES LABELS "gpu")
    endif()
endif()

# Optional pybind11 extension (host risk_metrics only; BUILD_PYTHON=ON)
option(BUILD_PYTHON "Build pybind11 tailwarp._native extension" OFF)
if(BUILD_PYTHON)
    find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
    find_package(pybind11 CONFIG QUIET)
    if(pybind11_FOUND)
        pybind11_add_module(_native python/bindings/risk_metrics_bindings.cpp)
        target_link_libraries(_native PRIVATE tailwarp)
        target_include_directories(_native PRIVATE ${CMAKE_SOURCE_DIR}/src)
        install(TARGETS _native LIBRARY DESTINATION tailwarp)
    endif()
endif()

# CUDA microbenchmark executables (native path; see benchmarks/README.md)
option(BUILD_BENCHMARKS "Build bench_student_t and bench_gaussian" ON)
if(BUILD_BENCHMARKS)
    add_executable(bench_student_t benchmarks/bench_student_t.cpp)
    target_include_directories(bench_student_t PRIVATE
        ${CMAKE_SOURCE_DIR}/benchmarks
        ${CMAKE_SOURCE_DIR}/src/wrappers
        ${CMAKE_SOURCE_DIR}/src)
    target_link_libraries(bench_student_t tailwarp tailwarp_kernels)

    add_executable(bench_gaussian benchmarks/bench_gaussian.cpp)
    target_include_directories(bench_gaussian PRIVATE
        ${CMAKE_SOURCE_DIR}/benchmarks
        ${CMAKE_SOURCE_DIR}/src/wrappers
        ${CMAKE_SOURCE_DIR}/src)
    target_link_libraries(bench_gaussian tailwarp tailwarp_kernels)
endif()

# Examples
add_executable(experiment_run examples/experiment_run.cpp)
target_include_directories(experiment_run PRIVATE
    ${CMAKE_SOURCE_DIR}/examples
    ${CMAKE_SOURCE_DIR}/src)
target_link_libraries(experiment_run tailwarp tailwarp_kernels)

add_executable(cvar_position_sizing examples/cvar_position_sizing.cpp)
target_include_directories(cvar_position_sizing PRIVATE
    ${CMAKE_SOURCE_DIR}/examples
    ${CMAKE_SOURCE_DIR}/src)
target_link_libraries(cvar_position_sizing tailwarp tailwarp_kernels)

# Installation
install(TARGETS tailwarp tailwarp_kernels
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

install(DIRECTORY src/wrappers/
    DESTINATION include/tailwarp
    FILES_MATCHING PATTERN "*.h"
)

