# pybind11 module configuration, imported in every module's CMakeLists.txt
# inspiration from https://github.com/memsharded/pybind11-example

# this script is called from a sub-directory, hence the additional ../
set(BUILDOUT_BIN_DIR ../../bin)


include(CheckCXXCompilerFlag)

# Detect python version from buildout recipe script
find_file(PYTHON_SCRIPT NAMES python python-script.py PATHS ${BUILDOUT_BIN_DIR} NO_DEFAULT_PATH)
if(NOT EXISTS ${PYTHON_SCRIPT})
    message(FATAL_ERROR "No python script found in ${BUILDOUT_BIN_DIR}. Please run buildout in project root")
endif()
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
add_library(${CMAKE_PROJECT_NAME} SHARED ${CPP_FILES})

# Don't add a 'lib' prefix to the shared library
set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES PREFIX "")

if (WIN32)
    if (MSVC)
        # /bigobj is needed for bigger binding projects due to the limit to 64k
        # addressable sections. /MP enables multithreaded builds (relevant when
        # there are many files).
        set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES COMPILE_FLAGS "/MP /bigobj ")

        if (NOT ${U_CMAKE_BUILD_TYPE} MATCHES DEBUG)
            # Enforce size-based optimization and link time code generation on MSVC
            # (~30% smaller binaries in experiments).
            set_target_properties(${CMAKE_PROJECT_NAME} APPEND_STRING PROPERTY COMPILE_FLAGS "/Os /GL ")
            set_target_properties(${CMAKE_PROJECT_NAME} APPEND_STRING PROPERTY LINK_FLAGS "/LTCG ")
        endif()
    endif()

    # .PYD file extension on Windows
    set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES SUFFIX ".pyd")

    # Link against the Python shared library
    target_link_libraries(${CMAKE_PROJECT_NAME} ${PYTHON_LIBRARY})
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
    set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES SUFFIX ".so")

    # Strip unnecessary sections of the binary on Linux/Mac OS
    if(APPLE)
        set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES MACOSX_RPATH ".")
        set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES LINK_FLAGS "-undefined dynamic_lookup ")
        if (NOT ${U_CMAKE_BUILD_TYPE} MATCHES DEBUG)
            add_custom_command(TARGET ${CMAKE_PROJECT_NAME} POST_BUILD COMMAND strip -u -r ${PROJECT_BINARY_DIR}/${CMAKE_PROJECT_NAME}.so)
        endif()
    else()
        if (NOT ${U_CMAKE_BUILD_TYPE} MATCHES DEBUG)
            add_custom_command(TARGET ${CMAKE_PROJECT_NAME} POST_BUILD COMMAND strip ${PROJECT_BINARY_DIR}/${CMAKE_PROJECT_NAME}.so)
        endif()
    endif()
endif()
