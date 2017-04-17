"""test_virtualenv_helpers/activate.py
**************************************
Provides unit tests for virtualenv_helpers/activate.py
"""

import unittest
import sys
import os
import argparse

from virtualenv_helpers.tests.contexts import TemporaryEnvironment


from virtualenv_helpers.activate import get_shell
from virtualenv_helpers.activate import parse_options
from virtualenv_helpers.activate import create_parser


class ActivateTestCase(unittest.TestCase):

    def test_get_shell_git_bash(self):
        if 'win32' not in sys.platform:
            raise unittest.SkipTest('Windows based test')
        with TemporaryEnvironment(SHELL=os.path.join('Test', 'test', 'test', 'test.exe')):
            shell, args, script_name = get_shell()
            self.assertEqual(shell, os.path.join('Test', 'bin', 'test.exe'))
            self.assertEqual(args, ['--init-file'])
            self.assertEqual(script_name, 'activate')

    def test_get_shell_powershell(self):
        if 'win32' not in sys.platform:
            raise unittest.SkipTest('Windows based test')
        with TemporaryEnvironment():
            try:
                os.environ.pop('SHELL')
            except Exception:
                pass
            try:
                os.environ.pop('PROMPT')
            except Exception:
                pass
            shell, args, script_name = get_shell()
            self.assertEqual(shell, 'powershell.exe')
            self.assertEqual(args, ['-NoLogo', '-NoExit', '.'])
            self.assertEqual(script_name, 'activate.ps1')

    def test_get_shell_cmd(self):
        if 'win32' not in sys.platform:
            raise unittest.SkipTest('Windows based test')
        with TemporaryEnvironment(PROMPT='True'):
            try:
                os.environ.pop('SHELL')
            except Exception:
                pass
            shell, args, script_name = get_shell()
            self.assertEqual(shell, 'cmd.exe')
            self.assertEqual(args, ['/K'])
            self.assertEqual(script_name, 'activate.bat')

    def test_get_shell_bash(self):
        if 'win' not in sys.platform:
            raise unittest.SkipTest('*nix based test')
        with TemporaryEnvironment(SHELL=os.path.join('bin', 'bash')):
                shell, args, script_name = get_shell()
                self.assertEqual(shell, os.path.join('bin', 'bash'))
                self.assertEqual(args, ['--init-file'])
                self.assertEqual(script_name, 'activate')

    def test_parse_options_defaults_editor(self):
        with TemporaryEnvironment(VENV_EDITOR='sublimetext3', VENV_EDITOR_SHOW='TRUE'):
            options, version = parse_options([])
            self.assertIsNone(options.virtualenv_path)
            self.assertIsNone(options.python_version)
            current_version = '{}.{}'.format(sys.version_info.major, sys.version_info.minor)
            self.assertEqual(version, current_version)
            self.assertTrue(options.editor is not None)
            self.assertTrue(options.show_editor)

    def test_parse_options_defaults_no_editor(self):
        with TemporaryEnvironment():
            os.environ.pop('VENV_EDITOR', None)
            os.environ.pop('VENV_EDITOR_SHOW', None)
            options, version = parse_options([])
            self.assertIsNone(options.editor)
            self.assertFalse(options.show_editor)

    def test_parse_options_defaults_wrong_editor(self):
        with TemporaryEnvironment(VENV_EDITOR='random_fail_editor_xyzdadsdasffaf', VENV_EDITOR_SHOW='TRUE'):
            options, version = parse_options([])
            self.assertIsNone(options.editor)
            self.assertFalse(options.show_editor)

    def test_parse_options_defaults_editor_no_show(self):
        with TemporaryEnvironment(VENV_EDITOR='sublimetext3', VENV_EDITOR_SHOW='False'):
            options, version = parse_options([])
            self.assertIsNone(options.virtualenv_path)
            self.assertIsNone(options.python_version)
            current_version = '{}.{}'.format(sys.version_info.major, sys.version_info.minor)
            self.assertEqual(version, current_version)
            self.assertTrue(options.editor is not None)
            self.assertTrue(options.show_editor)

    def test_parse_options_defaults_editor_meaningless_show(self):
        with TemporaryEnvironment(VENV_EDITOR='sublimetext3', VENV_EDITOR_SHOW='abc'):
            options, version = parse_options([])
            self.assertIsNone(options.virtualenv_path)
            self.assertIsNone(options.python_version)
            current_version = '{}.{}'.format(sys.version_info.major, sys.version_info.minor)
            self.assertEqual(version, current_version)
            self.assertTrue(options.editor is not None)
            self.assertTrue(options.show_editor)

    def test_parse_options_version(self):
        options, version = parse_options(['-p', 'Python2.1'])
        self.assertIsNone(options.virtualenv_path)
        self.assertEqual(options.python_version, 'Python2.1')
        self.assertEqual(version, '2.1')
        options, version = parse_options(['--py', 'Py2.1'])
        self.assertIsNone(options.virtualenv_path)
        self.assertEqual(options.python_version, 'Py2.1')
        self.assertEqual(version, '2.1')
        options, version = parse_options(['--py-version', '2.1'])
        self.assertIsNone(options.virtualenv_path)
        self.assertEqual(options.python_version, '2.1')
        self.assertEqual(version, '2.1')

    def test_parse_options_path(self):
        options, version = parse_options(['--path', 'test'])
        self.assertEqual(options.virtualenv_path, 'test')
        options, version = parse_options(['--virtualenv-path', 'test'])
        self.assertEqual(options.virtualenv_path, 'test')

    def test_create_parser(self):
        parser = create_parser()
        self.assertIsInstance(parser, argparse.ArgumentParser)
        self.assertEqual(parser.description, 'Activate a python virtual environment by searching for a local environment or looking in the VENV_DIR directory')


if __name__ == "__main__":
    unittest.main()
