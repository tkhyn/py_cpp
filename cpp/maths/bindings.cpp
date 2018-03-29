#include <pybind11/pybind11.h>

#include "main.h"


// The pybind11 definition
namespace py = pybind11;

PYBIND11_MODULE(maths, m) {
    m.doc() = "math module";
    m.def("add", &add);
    m.def("sub", &sub);
}
