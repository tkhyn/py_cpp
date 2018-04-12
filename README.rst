py_cpp
======


Template project for a Python 3 application with C/C++ modules.

Features:

- dependency management using buildout_ for Python and conan_ for C/C++ modules
- automated C/C++ builds using CMake_
- testing frameworks for Python and C/C++, all the tests are built and run
  from one command
- automated inline documentation generation using sphinx-apidoc_ for the
  Python code and doxygen_ for the C/C++ code


Requirements
------------

- Python_ 3 (latest version recommended)
- a C/C++ compiler (the one used to compile your Python executable and
  libraries)
- CMake_ 3.X (latest verion recommended)
- doxygen_ to generate C/C++ documentation

You do not need to install conan_ on your machine as it will be automatically
installed locally if you follow the steps below.


Quick start
-----------

First, you'll need to download or clone this repository, and edit
``LICENSE.rst`` and ``setup.py`` to your liking (replace author, url, etc.), and
probably remove this ``README.rst`` file.

Then, you can open a command prompt in the root directory and start by
bootstrapping buildout_::

   $ python bootstrap.py

.. warning::

   Make sure ``python`` is associated to a recent Python 3 interpreter on your
   machine!

This creates a ``bin`` directory with a ``buildout`` script, that we're going
to invoke straight away::

   $ bin/buildout

This in turn downloads and installs conan_ and all its dependencies locally and
creates some scripts in the ``bin`` directory:

- ``bin/conan`` is the C/C++ dependencies manager and will be invoked by CMake_
- ``bin/tests`` will launch the test suite
- ``bin/sphinx-builder`` launches the documentation generation
- ``bin/run`` will simply ... run the application
- ``bin/python`` will be used to launch a useful Python_ interpreter where all
  your Python dependencies and C/C++ modules will be available


Project structure
-----------------

Here is an overview of the project structure::

   py_cpp/                  # project directory
      bin/                  # buildout scripts
      doc/                  # sphinx documentation

      py_cpp/               # main package directory
         .cmake/            # CMake main scripts for all packages
         maths/             # an example C/C++ module
            src/            # the C/C++ source files
            tests/          # the Catch tests for the C/C++ package
            bindings.cpp    # the pybind11 bindings (glue between Python and C)
            CMakeLists.txt  # CMake script
            conanfile.txt   # conan dependencies management for C/C++
         [*].py             # pure Python modules

      tests/                # Python unit test directory
        .cpp/               # C/C++ test executables
        conftest.py         # py.test configuration file
        test_cpp.py         # tests all the C++ packages
        test_*.py           # your Python unit tests

      bootstrap.py          # buildout bootstrap script, don't change!
      buildout.cfg          # buildout dependencies management for python
      LICENSE.rst           # replace with your license
      MANIFEST.in           # python package file inclusions/exlusions
      README.rst            # this file!
      setup.cfg             # python package misc. configuration options
      setup.py              # python package build/installation script

Basically, the Python package is contained within the ``py_cpp`` directory, that
you can of course rename according to your needs.

Within that directory, you can find pure python modules or packages, but also
C/C++ modules. The C/C++ modules can then be easily separated from the project
if they become large enough.

The C/C++ modules generation is automatically configured with CMake, and the
built binaries are placed into the ``py_cpp`` directory. This way, if a C/C++
module is named ``maths``, you may import it in a Python module with::

    from py_cpp import maths


Graphical User Interface
------------------------

Adding a GUI is relatively simple. If you check out the ``wx`` branch of this
repository, you will find out how the minimal console application can be turned
into a GUI with the help of wxPython_ and wxFormBuilder_.


Testing
-------

You can launch the whole test suite (including the C/C++ tests) by typing::

   bin/tests

The file ``tests/test_cpp.py`` generates the Python tests that call the C/C++
test executables which are built when the test session starts.

You can of course test and debug the C/C++ modules independently.

The test executables for C/C++ modules are automatically placed into the
``tests/.cpp`` directory.

If you need coverage information (for Python code only), use::

   bin/tests --cov


Documentation
-------------

The documentation relies mainly on sphinx_. sphinx-apidoc_ is used to generate
the documentation from Python docstrings, while doxygen_ does the same on the
C/C++ side. breathe_ is used to include the doxygen_ documentation into the
sphinx_ main documentation.

To generate the documentation for the whole project, simply use::

   bin/sphinx-build --apidoc

If you do not need to regenerate the documentation from the docstrings, you can
remove ``code=True``::

   bin/sphinx-build

To add custom documentation, simply add some *.rst files in the ``doc`` folder
and follow the sphinx_ documentation for more information on directives and
syntax.


.. _Python: https://www.python.org
.. _buildout: http://www.buildout.org/en/stable/
.. _conan: https://www.conan.io/
.. _CMake: https://cmake.org
.. _sphinx: http://www.sphinx-doc.org
.. _sphinx-apidoc: http://www.sphinx-doc.org/en/stable/man/sphinx-apidoc.html
.. _doxygen: http://www.doxygen.org/
.. _breathe: http://breathe.readthedocs.io/en/stable/
.. _wxPython: https://www.wxpython.org/
.. _wxFormBuilder: http://wxformbuilder.org
