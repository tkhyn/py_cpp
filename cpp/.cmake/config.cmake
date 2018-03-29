# Default C++ module configuration, imported in every module's CMakeLists.txt

# Set a default build configuration if none is specified. 'MinSizeRel' produces the smallest binaries
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    message(STATUS "Setting build type to 'MinSizeRel' as none was specified.")
    set(CMAKE_BUILD_TYPE MinSizeRel CACHE STRING "Choose the type of build." FORCE)
    set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release"
        "MinSizeRel" "RelWithDebInfo")
endif()
string(TOUPPER "${CMAKE_BUILD_TYPE}" U_CMAKE_BUILD_TYPE)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})

# when including files in the same directory we have to use ../.cmake
# as the current working directory is the module's directory, where the
# CMakeLists.txt file lies

# run conan from cmake
include(../.cmake/conan.cmake)
conan_cmake_run(
    CONANFILE conanfile.txt
    BASIC_SETUP
    BUILD missing
    CONAN_COMMAND ../../../bin/conan
)

# pybind11 configuration
include(../.cmake/pybind11.cmake)

# post-build steps
include(../.cmake/postbuild.cmake)
