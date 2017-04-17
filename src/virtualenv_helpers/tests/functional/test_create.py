"""test_virtualenv_helpers/create.py
**************************************
Provides unit tests for virtualenv_helpers/create.py
"""

import unittest
import os
import sys
import glob

import pkg_resources
try:
    import virtualenv
except ImportError:
    virtualenv = False

from virtualenv_helpers.tests.contexts import TemporaryDirectory
from virtualenv_helpers.tests.contexts import TemporaryEnvironment
from virtualenv_helpers.tests.contexts import Quiet

from virtualenv_helpers.create import create
from virtualenv_helpers.create import install_default_wheels

VERBOSITY = 2


class CreateTestCase(unittest.TestCase):
    @unittest.skipIf(not virtualenv, 'Test requires virtualenv')
    def test_install_default_wheels(self):
        if sys.platform.startswith('win32'):
            lib_path = ('Lib', 'site-packages')
        else:
            lib_path = ('lib', 'python*', 'site-packages')
        wheel_dir = pkg_resources.resource_filename('virtualenv_helpers.tests.functional', 'test_wheels')
        with TemporaryEnvironment(VENV_DEFAULT_WHEELS_DIR=wheel_dir), TemporaryDirectory() as t, Quiet():
            current_version = '{}.{}'.format(sys.version_info.major, sys.version_info.minor)
            virtualenv.create_environment(t.path)
            self.assertFalse(len(glob.glob(os.path.join(os.path.join(t.path, *lib_path), 'test_package'))))
            install_default_wheels(current_version, t.path)
            self.assertTrue(len(glob.glob(os.path.join(os.path.join(t.path, *lib_path), 'test_package*'))))

    def test_create(self):
        with TemporaryDirectory() as virtualenv_dir, Quiet():
            with TemporaryEnvironment(VENV_DIR=virtualenv_dir.path):
                current_version = '{}.{}'.format(sys.version_info.major, sys.version_info.minor)
                create(['test_virtual_env'])
                self.assertTrue(os.path.exists(os.path.join(virtualenv_dir.path, 'test_virtual_env-{}'.format(current_version))))


if __name__ == "__main__":
    # Run tests
    unittest.main()
