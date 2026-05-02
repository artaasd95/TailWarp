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
        target_link_libraries(tailwarp_tests 
            tailwarp 
            tailwarp_kernels
            GTest::GTest 
            GTest::Main
        )
        enable_testing()
        add_test(NAME TailWarpTests COMMAND tailwarp_tests)
    endif()
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

