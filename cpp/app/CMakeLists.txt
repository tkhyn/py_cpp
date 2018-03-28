cmake_minimum_required(VERSION 2.8)
project(app)

# Set a default build configuration if none is specified. 'MinSizeRel' produces the smallest binaries
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    message(STATUS "Setting build type to 'MinSizeRel' as none was specified.")
    set(CMAKE_BUILD_TYPE MinSizeRel CACHE STRING "Choose the type of build." FORCE)
    set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release"
        "MinSizeRel" "RelWithDebInfo")
endif()
string(TOUPPER "${CMAKE_BUILD_TYPE}" U_CMAKE_BUILD_TYPE)

# Check for conanbuildinfo.cmake file
if(EXISTS ${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
    include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
    conan_basic_setup()
else()
    message(FATAL_ERROR "The file conanbuildinfo.cmake doesn't exist, please "
                        "run conan install .. -s build_type=${CMAKE_BUILD_TYPE} "
                        "--install-folder=${CMAKE_BINARY_DIR}")
endif()

include_directories(SYSTEM ${CONAN_INCLUDE_DIRS})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})

include(CheckCXXCompilerFlag)

# Detect python version from buildout recipe script
find_file(PYTHON_SCRIPT NAMES python python-script.py PATHS ../../bin NO_DEFAULT_PATH)
file(STRINGS ${PYTHON_SCRIPT} PYTHON_EXEC LIMIT_COUNT 1)
string(REGEX REPLACE "[#!\"]" "" PYTHON_EXEC ${PYTHON_EXEC})

# run python --version from the environment interpreter
execute_process(COMMAND ${PYTHON_EXEC} --version OUTPUT_VARIABLE PYTHON_VERSION)
string(REGEX REPLACE "[a-zA-Z\ \n]" "" PYTHON_VERSION ${PYTHON_VERSION})
message("-- Using Python ${PYTHON_VERSION}")

# Now we can look for the libraries
find_package(PythonLibs ${PYTHON_VERSION} EXACT REQUIRED)
find_package(PythonInterp ${PYTHON_VERSION} EXACT REQUIRED)


if (CMAKE_CXX_COMPILER_ID MATCHES "Clang" OR CMAKE_CXX_COMPILER_ID MATCHES "GNU")
    CHECK_CXX_COMPILER_FLAG("-std=c++14" HAS_CPP14_FLAG)
    CHECK_CXX_COMPILER_FLAG("-std=c++11" HAS_CPP11_FLAG)

    if (HAS_CPP14_FLAG)
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14")
    elseif (HAS_CPP11_FLAG)
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
    else()
        message(FATAL_ERROR "Unsupported compiler -- at least C++11 support is needed!")
    endif()

    # Enable link time optimization and set the default symbol
    # visibility to hidden (very important to obtain small binaries)
    if (NOT ${U_CMAKE_BUILD_TYPE} MATCHES DEBUG)
        # Default symbol visibility
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fvisibility=hidden")

        # Check for Link Time Optimization support
        CHECK_CXX_COMPILER_FLAG("-flto" HAS_LTO_FLAG)
        if (HAS_LTO_FLAG)
            set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -flto")
        endif()
    endif()
endif()

# Include path for Python header files
include_directories(${PYTHON_INCLUDE_DIR})

# Include path for pybind11 header files -- this may need to be changed depending on your setup
include_directories(${PROJECT_SOURCE_DIR}/pybind11/include)

# Create the binding library
add_library(app SHARED
    main.cpp
    # ... extra files go here ...
)

# Don't add a 'lib' prefix to the shared library
set_target_properties(app PROPERTIES PREFIX "")

if (WIN32)
    if (MSVC)
        # /bigobj is needed for bigger binding projects due to the limit to 64k
        # addressable sections. /MP enables multithreaded builds (relevant when
        # there are many files).
        set_target_properties(app PROPERTIES COMPILE_FLAGS "/MP /bigobj ")

        if (NOT ${U_CMAKE_BUILD_TYPE} MATCHES DEBUG)
            # Enforce size-based optimization and link time code generation on MSVC
            # (~30% smaller binaries in experiments).
            set_target_properties(app APPEND_STRING PROPERTY COMPILE_FLAGS "/Os /GL ")
            set_target_properties(app APPEND_STRING PROPERTY LINK_FLAGS "/LTCG ")
        endif()
    endif()

    # .PYD file extension on Windows
    set_target_properties(app PROPERTIES SUFFIX ".pyd")

    # Link against the Python shared library
    target_link_libraries(app ${PYTHON_LIBRARY})
elseif (UNIX)
    # It's quite common to have multiple copies of the same Python version
    # installed on one's system. E.g.: one copy from the OS and another copy
    # that's statically linked into an application like Blender or Maya.
    # If we link our plugin library against the OS Python here and import it
    # into Blender or Maya later on, this will cause segfaults when multiple
    # conflicting Python instances are active at the same time (even when they
    # are of the same version).

    # Windows is not affected by this issue since it handles DLL imports
    # differently. The solution for Linux and Mac OS is simple: we just don't
    # link against the Python library. The resulting shared library will have
    # missing symbols, but that's perfectly fine -- they will be resolved at
    # import time.

    # .SO file extension on Linux/Mac OS
    set_target_properties(app PROPERTIES SUFFIX ".so")

    # Strip unnecessary sections of the binary on Linux/Mac OS
    if(APPLE)
        set_target_properties(app PROPERTIES MACOSX_RPATH ".")
        set_target_properties(app PROPERTIES LINK_FLAGS "-undefined dynamic_lookup ")
        if (NOT ${U_CMAKE_BUILD_TYPE} MATCHES DEBUG)
            add_custom_command(TARGET app POST_BUILD COMMAND strip -u -r ${PROJECT_BINARY_DIR}/app.so)
        endif()
    else()
        if (NOT ${U_CMAKE_BUILD_TYPE} MATCHES DEBUG)
            add_custom_command(TARGET app POST_BUILD COMMAND strip ${PROJECT_BINARY_DIR}/app.so)
        endif()
    endif()
endif()
