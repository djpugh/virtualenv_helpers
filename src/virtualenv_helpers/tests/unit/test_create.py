"""test_virtualenv_helpers/create.py
**************************************
Provides unit tests for virtualenv_helpers/create.py
"""

import unittest
import sys
import argparse

from virtualenv_helpers.tests.contexts import TemporaryEnvironment


import virtualenv_helpers.create as create
from virtualenv_helpers.create import parse_options
from virtualenv_helpers.create import create_parser
from virtualenv_helpers.create import get_python_versions
from virtualenv_helpers.create import get_python_executable


class CreateTestCase(unittest.TestCase):

    def setUp(self):
        create.is_windows = sys.platform.startswith('win')

    def tearDown(self):
        create.is_windows = sys.platform.startswith('win')

    def test_parse_options_version(self):
        options, unknown = parse_options(['-p', 'Python2.1'])
        self.assertIsNone(options.name)
        self.assertEqual(options.python_versions, [['Python2.1']])
        options, unknown = parse_options(['--py-version', '2.1'])
        self.assertIsNone(options.name)
        self.assertEqual(options.python_versions, [['2.1']])

    def test_create_parser(self):
        parser = create_parser()
        self.assertIsInstance(parser, argparse.ArgumentParser)
        self.assertEqual(parser.description, 'Create a virtual environment for the current directory')

    def test_parse_options_local(self):
        options, unknown = parse_options(['-l'])
        self.assertIsNone(options.name)
        self.assertTrue(options.local)
        options, unknown = parse_options(['--local'])
        self.assertIsNone(options.name)
        self.assertTrue(options.local)

    def test_parse_options_directory(self):
        with TemporaryEnvironment(VENV_DIR='abc'):
            options, unknown = parse_options([])
            self.assertIsNone(options.name)
            self.assertEqual(options.virtualenv_dir, 'abc')
        options, unknown = parse_options(['-d', 'def'])
        self.assertIsNone(options.name)
        self.assertEqual(options.virtualenv_dir, 'def')
        options, unknown = parse_options(['--directory', 'ghi'])
        self.assertIsNone(options.name)
        self.assertEqual(options.virtualenv_dir, 'ghi')

    def test_parse_options_py3(self):
        options, unknown = parse_options([])
        self.assertIsNone(options.name)
        self.assertFalse(options.py35)
        options, unknown = parse_options(['-3'])
        self.assertIsNone(options.name)
        self.assertTrue(options.py35)
        options, unknown = parse_options(['--py3'])
        self.assertIsNone(options.name)
        self.assertTrue(options.py35)
        options, unknown = parse_options(['--py3.5'])
        self.assertIsNone(options.name)
        self.assertTrue(options.py35)

    def test_parse_options_py36(self):
        options, unknown = parse_options([])
        self.assertIsNone(options.name)
        self.assertFalse(options.py36)
        options, unknown = parse_options(['--py3.6'])
        self.assertIsNone(options.name)
        self.assertTrue(options.py36)
        options, unknown = parse_options(['--py36'])
        self.assertIsNone(options.name)
        self.assertTrue(options.py36)

    def test_parse_options_py2(self):
        options, unknown = parse_options([])
        self.assertIsNone(options.name)
        self.assertFalse(options.py27)
        options, unknown = parse_options(['-2'])
        self.assertIsNone(options.name)
        self.assertTrue(options.py27)
        options, unknown = parse_options(['--py2'])
        self.assertIsNone(options.name)
        self.assertTrue(options.py27)
        options, unknown = parse_options(['--py2.7'])
        self.assertIsNone(options.name)
        self.assertTrue(options.py27)

    def test_parse_options_wheels(self):
        options, unknown = parse_options([])
        self.assertIsNone(options.name)
        self.assertFalse(options.default_wheels)
        options, unknown = parse_options(['-w'])
        self.assertIsNone(options.name)
        self.assertTrue(options.default_wheels)
        options, unknown = parse_options(['--wheels'])
        self.assertIsNone(options.name)
        self.assertTrue(options.default_wheels)

    def test_parse_options_ignore_current_version(self):
        options, unknown = parse_options([])
        self.assertIsNone(options.name)
        self.assertFalse(options.py27)
        options, unknown = parse_options(['--ignore-current-version'])
        self.assertIsNone(options.name)
        self.assertTrue(options.ignore_current_version)

    def test_get_python_versions_no_versions(self):
        versions = get_python_versions(argparse.Namespace(python_versions=[],
                                                          py35=False,
                                                          py27=False,
                                                          py36=False,
                                                          ignore_current_version=False))
        current_version = sys.version_info
        self.assertEqual(len(versions), 1)
        self.assertEqual(versions[0], '{}.{}'.format(current_version.major, current_version.minor))

    def test_get_python_versions_ignore_current_version(self):
        versions = get_python_versions(argparse.Namespace(python_versions=[],
                                                          py35=False,
                                                          py27=False,
                                                          py36=False,
                                                          ignore_current_version=True))
        self.assertEqual(len(versions), 0)

    def test_get_python_versions_py35(self):
        versions = get_python_versions(argparse.Namespace(python_versions=[],
                                                          py35=True,
                                                          py27=False,
                                                          py36=False,
                                                          ignore_current_version=True))
        self.assertEqual(len(versions), 1)
        self.assertEqual(versions[0], '3.5')

    def test_get_python_versions_py36(self):
        versions = get_python_versions(argparse.Namespace(python_versions=[],
                                                          py35=False,
                                                          py27=False,
                                                          py36=True,
                                                          ignore_current_version=True))
        self.assertEqual(len(versions), 1)
        self.assertEqual(versions[0], '3.6')

    def test_get_python_versions_py27(self):
        versions = get_python_versions(argparse.Namespace(python_versions=[],
                                                          py35=False,
                                                          py27=True,
                                                          py36=False,
                                                          ignore_current_version=True))
        self.assertEqual(len(versions), 1)
        self.assertEqual(versions[0], '2.7')

    def test_get_python_versions_command_line(self):
        versions = get_python_versions(argparse.Namespace(python_versions=[['2.4'], ['python1.7'], ['py3.1']],
                                                          py35=False,
                                                          py27=False,
                                                          py36=False,
                                                          ignore_current_version=True))
        self.assertEqual(len(versions), 3)
        self.assertIn('2.4', versions)
        self.assertIn('1.7', versions)
        self.assertIn('3.1', versions)

    @unittest.skipIf(not sys.platform.startswith('win'), 'Test requires windows and winreg module')
    def test_get_python_executable_windows(self):
        current_version = sys.version_info
        version_info = '{}.{}'.format(current_version.major, current_version.minor)
        executable = get_python_executable(version_info)
        self.assertIn('python.exe', executable)

    def test_get_python_executable_nix(self):
        create.is_windows = False
        self.assertEqual(get_python_executable('2.7'), 'python2.7')


if __name__ == "__main__":
    unittest.main()
