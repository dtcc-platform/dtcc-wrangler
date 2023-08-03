# Project configuration
cmake_minimum_required(VERSION 3.15)
project(${SKBUILD_PROJECT_NAME} VERSION ${SKBUILD_PROJECT_VERSION})

# Set compiler flags
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Set installation directory
set(CMAKE_INSTALL_PREFIX ${CMAKE_SOURCE_DIR}/src)
set(CMAKE_SKIP_INSTALL_ALL_DEPENDENCY true)

# Add clang tools
include(cmake/clang-cxx-dev-tools.cmake)
include(cmake/FindLibGEOS.cmake)

# Find packages
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake")
find_package(pybind11 CONFIG REQUIRED)
find_package(LibGEOS REQUIRED)

# Set include directories
include_directories(${CMAKE_SOURCE_DIR}/src/cpp/include)
include_directories(${CMAKE_SOURCE_DIR}/src/cpp/include/model)
include_directories(${CMAKE_SOURCE_DIR}/src/cpp/external)
include_directories(${LIBGEOS_INCLUDE_DIRS})

# Set installation directory
set(CMAKE_INSTALL_PREFIX ${CMAKE_SOURCE_DIR}/src)
set(CMAKE_SKIP_INSTALL_ALL_DEPENDENCY true)

set(BINDINGS _dtcc_wrangler)

# # Add Python bindings
# pybind11_add_module(${BINDINGS} MODULE ${CMAKE_SOURCE_DIR}/src/cpp/dtcc_wrangler.cpp)
# target_compile_definitions(${BINDINGS} PRIVATE VERSION_INFO=${PROJECT_VERSION})
# target_link_libraries(${BINDINGS} PRIVATE ${LIBGEOS_LIBRARIES})

# install(TARGETS ${BINDINGS} DESTINATION dtcc_wrangler)

# Add tests
# ADD_SUBDIRECTORY(tests/cpp)
