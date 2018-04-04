import os
import unittest
import subprocess


from tests.conftest import CMakeTestExtensionBuilder, EXEC_PATH


attrs = {}

for ext in CMakeTestExtensionBuilder.extensions:
    method_name = 'test_%s_module' % ext.name

    def tm(self):
        subprocess.check_call(
            os.path.join(EXEC_PATH, CMakeTestExtensionBuilder.target(ext.name))
        )

    tm.__name__ = method_name
    tm.__qualname__ = 'CppTests.' + method_name
    tm.__doc__ = 'Generic test function for %s C/C++ module' % ext.name

    attrs[method_name] = tm
    # setattr(CppTests, method_name, test_method)


CppTests = type('CppTests', (unittest.TestCase,), attrs)
