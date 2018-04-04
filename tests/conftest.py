"""
py.test hooks

Builds c++ modules test executables before running tests
Adds a python test that runs each c++ module test executable
"""

import os
from importlib.util import spec_from_file_location, module_from_spec
from subprocess import DEVNULL, STDOUT


TEST_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.normpath(os.path.dirname(TEST_PATH))
EXEC_PATH = os.path.join(TEST_PATH, '.cpp')


# import setup module (import ..setup does not work!)
_spec = spec_from_file_location("setup", os.path.join(ROOT_PATH, 'setup.py'))
setup = module_from_spec(_spec)
_spec.loader.exec_module(setup)


class CMakeTestExtensionBuilder(setup.CMakeExtensionBuilder):

    debug = False
    build_temp = os.path.join(ROOT_PATH, 'build', 'temp.test-build')

    @staticmethod
    def get_ext_fullpath(name):
        return os.path.join(EXEC_PATH, name)

    @staticmethod
    def target(name):
        return '%s_test' % name

    @staticmethod
    def get_subprocess_kwargs():
        """
        Silence stdout/stderr when building for tests
        """
        return {
            'stdout': DEVNULL,
            'stderr': STDOUT
        }


def pytest_sessionstart(session):
    """
    Build test executables from C/C++ packages
    """

    ext_builder = CMakeTestExtensionBuilder()
    ext_builder.run()
