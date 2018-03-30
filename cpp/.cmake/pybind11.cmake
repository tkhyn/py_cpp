# pybind11 module configuration

# Lookup buildout python executable, PYTHON_EXECUTABLE is then used within pybind11
# to detect python version and libraries
find_file(PYTHON_EXECUTABLE NAMES python python.exe PATHS ${BUILDOUT_BIN_DIR} NO_DEFAULT_PATH)
if(NOT EXISTS ${PYTHON_EXECUTABLE})
    message(FATAL_ERROR "No python interpreter found in ${BUILDOUT_BIN_DIR}. Please run buildout in project root")
endif()

# Look up pybind11 from conan path
find_package(pybind11 REQUIRED)

# Python interpreter version extraction
set(PYTHON_VERSION "${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR}.${PYTHON_VERSION_PATCH}")
message("-- Using Python ${PYTHON_VERSION}  libraries")

# adding python module
pybind11_add_module(${CMAKE_PROJECT_NAME}
        ${SRC_FILES}
        bindings.cpp
)
