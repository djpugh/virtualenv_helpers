"""virtualenv_helpers/activate.py
**************************************
Provides unit tests for virtualenv_helpers/activate.py
"""

import unittest
import sys
import os

try:
    import virtualenv
except ImportError:
    virtualenv = False

from virtualenv_helpers.tests.contexts import TemporaryDirectory
from virtualenv_helpers.tests.contexts import TemporaryEnvironment
from virtualenv_helpers.tests.contexts import Quiet

from virtualenv_helpers.activate import activate


class ActivateTestCase(unittest.TestCase):

    @unittest.skipIf(not virtualenv, 'Test requires virtualenv')
    def test_activate_ok(self):
        # This needs a virtual environment setup to install from
        # This also creates a shell, so requires user input
        with TemporaryDirectory() as t, Quiet(), TemporaryEnvironment():
            virtualenv.create_environment(t.path)
            activate(['--path', t.path])

    def test_activate_fail(self):
        # This needs a virtual environment setup to install from
        with Quiet(), TemporaryEnvironment(), TemporaryDirectory(change_directory=False) as virtualenv_dir:
            os.environ['VIRTUALENV_DIR'] = virtualenv_dir.path
            old_path = sys.path
            activate()
            self.assertEqual(old_path, sys.path)


if __name__ == "__main__":
    # Run tests
    unittest.main()
