#include <pybind11/pybind11.h>

#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}


// The pybind11 definition
namespace py = pybind11;

PYBIND11_MODULE(app, m) {
    m.doc() = "app's main module";
    m.def("main", &main);
}
