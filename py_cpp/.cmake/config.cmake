# Default C++ module configuration, imported in every module's CMakeLists.txt

# directories
set(SRC_DIR "src")
set(TESTS_DIR "tests")


# retrieve module directory name = project name
get_filename_component(MODULE_NAME ${CMAKE_CURRENT_SOURCE_DIR} NAME)
project(${MODULE_NAME})

# this creates the __MODULE__ pre-processor definition used in bindings.cpp
add_definitions(-D__MODULE__=${CMAKE_PROJECT_NAME})

# retrieve buildout bin directory
get_filename_component(BUILDOUT_BIN_DIR ../../bin ABSOLUTE)

# include source directory
include_directories(${SRC_DIR})

# retrieves all C++ files
file(GLOB_RECURSE SRC_FILES LIST_DIRECTORIES false ${SRC_DIR}/*.cpp)


# Set a default build configuration if none is specified. 'MinSizeRel' produces
# the smallest binaries
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    message(STATUS "Setting build type to 'MinSizeRel' as none was specified.")
    set(CMAKE_BUILD_TYPE MinSizeRel CACHE STRING "Choose the type of build." FORCE)
    set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release"
        "MinSizeRel" "RelWithDebInfo")
endif()
string(TOUPPER "${CMAKE_BUILD_TYPE}" U_CMAKE_BUILD_TYPE)

if (NOT DEFINED CMAKE_LIBRARY_OUTPUT_DIRECTORY)
    set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../)
endif()
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE ${CMAKE_LIBRARY_OUTPUT_DIRECTORY})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_DEBUG ${CMAKE_LIBRARY_OUTPUT_DIRECTORY})

if(MSVC)
    set(CMAKE_MODULE_LINKER_FLAGS /MANIFEST:NO)
endif()

# when including files in the same directory we have to use ../.cmake
# as the current working directory is the module's directory, where the
# CMakeLists.txt file lies

# run conan from cmake
set(CONAN_BUILD_INFO_CMAKE "${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
if(EXISTS ${CONAN_BUILD_INFO_CMAKE})
    # standard conan installation, deps are defined in conanfile.txt
    include(${CONAN_BUILD_INFO_CMAKE})
    conan_basic_setup(
        NO_OUTPUT_DIRS
    )
else()
    # no conan build info found, run conan install
    include(../.cmake/conan.cmake)
    conan_cmake_run(
        CONANFILE conanfile.txt
        BASIC_SETUP
        BUILD missing
        CONAN_COMMAND ${BUILDOUT_BIN_DIR}/conan
        NO_OUTPUT_DIRS
    )
endif()

# pybind11 configuration
include(../.cmake/pybind11.cmake)

# tests configuration
include(../.cmake/tests.cmake)
