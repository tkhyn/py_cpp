cmake_minimum_required(VERSION 2.8)
project(app)

# add all C++ files here
set(CPP_FILES main.cpp)

# general configuration
include(../config.cmake)

# run conan from cmake
include(../conan.cmake)
conan_cmake_run(CONANFILE conanfile.txt
                BASIC_SETUP
                BUILD missing)

# pybind11 configuration
include(../pybind11.cmake)
