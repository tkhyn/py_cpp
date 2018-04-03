#include <pybind11/pybind11.h>

#include "src/main.h"


// The pybind11 definition
namespace py = pybind11;

// __MODULE__ is defined by CMake
PYBIND11_MODULE(__MODULE__, m) {
    m.doc() = "math module";
    m.def("add", &add);
    m.def("sub", &sub);
}
