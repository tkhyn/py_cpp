# Tests for the 'maths' C module

# C/C++ functions exposed to Python should be tested this way from Python
# (rather than from the C/C++ tests, which should focus on testing the C/C++
# internal bits)


import unittest
from cpp import maths


class MathsTest(unittest.TestCase):

    def test_add(self):
        self.assertEqual(maths.add(1000, 1), 1001)

    def test_sub(self):
        self.assertEqual(maths.sub(1000, 1), 999)
