# Tests for the 'main' Python module

# This is the standard way 'pure Python' modules should be tested

from io import StringIO

import unittest
from unittest.mock import patch

from py_cpp import main


class MainTest(unittest.TestCase):

    @patch('sys.stdout', new_callable=StringIO)
    def test_run(self, mock_stdout):
        # tests the console output when calling 'run'
        main.run()

        self.assertEqual(
            mock_stdout.getvalue().strip(),
            '2 + 2 = 4\n' +
            '8 - 6 = 2'
        )
