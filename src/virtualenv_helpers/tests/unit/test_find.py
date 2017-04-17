"""test_virtualenv_helpers/find.py
**********************************
Provides unit tests for virtualenv_helpers/find.py
"""

import unittest
import os

from virtualenv_helpers.tests.contexts import TemporaryEnvironment
from virtualenv_helpers.tests.contexts import TemporaryDirectory

from virtualenv_helpers.find import recursive_check
from virtualenv_helpers.find import get_virtualenv_dir
from virtualenv_helpers.find import find_venv_dir_env
from virtualenv_helpers.find import find_local_env
from virtualenv_helpers.find import find_recursive_path_venv
from virtualenv_helpers.find import find_recursive_path_local_env
from virtualenv_helpers.find import find_virtualenv
from virtualenv_helpers.find import check_input_path
from virtualenv_helpers.find import get_virtualenv_path


class FindTestCase(unittest.TestCase):

    def test_recursive_check(self):

        with TemporaryDirectory() as t:
            os.makedirs('abc/def/ghi')
            os.chdir('abc/def/ghi')

            def check_function(version, current_directory):
                match = current_directory == os.path.join(t.path, 'abc', 'def')
                if match:
                    return match, 'abcdefghi'
                else:
                    return None, None
            venv_path, matching_path = recursive_check(check_function, '2.3', None)
            self.assertTrue(venv_path)
            self.assertEqual(matching_path, 'abcdefghi')

    def test_find_venv_dir_env(self):
        with TemporaryDirectory() as t, TemporaryDirectory(change_directory=False) as virtualenv_dir:
            with TemporaryEnvironment(VENV_DIR=virtualenv_dir.path):
                os.mkdir(os.path.join(virtualenv_dir.path, 'def-2.7'))
                os.makedirs(os.path.join('abc', 'def'))
                os.chdir(os.path.join('abc', 'def'))
                path, matching = find_venv_dir_env('2.7', os.getcwd())
                self.assertEqual(path, os.path.join(virtualenv_dir.path, 'def-2.7'))
                self.assertEqual(matching, os.path.join(t.path, 'abc', 'def'))

    def test_find_venv_dir_env_none(self):
        with TemporaryDirectory(), TemporaryDirectory(change_directory=False) as virtualenv_dir:
            with TemporaryEnvironment(VENV_DIR=virtualenv_dir.path):
                os.mkdir(os.path.join(virtualenv_dir.path, 'abc-2.7'))
                os.makedirs(os.path.join('ghi', 'def'))
                os.chdir(os.path.join('ghi', 'def'))
                path, matching = find_venv_dir_env('2.7', os.getcwd())
                self.assertIsNone(path)
                self.assertIsNone(matching)

    def test_find_local_env(self):
        with TemporaryDirectory() as t:
            os.makedirs(os.path.join('abc', '.venv'))
            os.chdir('abc')
            path, matching = find_local_env('2.7')
            self.assertEqual(path, os.path.join(t.path, 'abc', '.venv'))
            self.assertEqual(matching, os.path.join(t.path, 'abc'))

    def test_find_local_env_none(self):
        with TemporaryDirectory():
            os.makedirs(os.path.join('abc', 'def'))
            os.chdir(os.path.join('abc', 'def'))
            path, matching = find_local_env('2.7')
            self.assertIsNone(path)
            self.assertIsNone(matching)

    def test_find_local_env_with_version(self):
        with TemporaryDirectory() as t:
            os.makedirs(os.path.join('abc', '.venv-2.7'))
            os.chdir('abc')
            path, matching = find_local_env('2.7')
            self.assertEqual(path, os.path.join(t.path, 'abc', '.venv-2.7'))
            self.assertEqual(matching, os.path.join(t.path, 'abc'))

    def test_find_recursive_path_venv(self):
        with TemporaryDirectory() as t, TemporaryDirectory(change_directory=False) as virtualenv_dir:
            with TemporaryEnvironment(VENV_DIR=virtualenv_dir.path):
                os.mkdir(os.path.join(virtualenv_dir.path, 'abc-2.7'))
                os.makedirs(os.path.join('abc', 'def'))
                os.chdir(os.path.join('abc', 'def'))
                path, matching = find_recursive_path_venv('2.7')
                self.assertEqual(path, os.path.join(virtualenv_dir.path, 'abc-2.7'))
                self.assertEqual(matching, os.path.join(t.path, 'abc'))

    def test_find_recursive_path_venv_none(self):
        with TemporaryDirectory(), TemporaryDirectory(change_directory=False) as virtualenv_dir:
            with TemporaryEnvironment(VENV_DIR=virtualenv_dir.path):
                os.mkdir(os.path.join(virtualenv_dir.path, 'ghi-2.7'))
                os.makedirs(os.path.join('abc', 'def'))
                os.chdir(os.path.join('abc', 'def'))
                path, matching = find_recursive_path_venv('2.7')
                self.assertIsNone(path)
                self.assertIsNone(matching)

    def test_find_recursive_path_local_env(self):
        with TemporaryDirectory() as t:
            os.makedirs(os.path.join('abc', 'def'))
            os.makedirs(os.path.join('abc', '.venv'))
            os.chdir(os.path.join('abc', 'def'))
            path, matching = find_recursive_path_local_env('2.7')
            self.assertEqual(path, os.path.join(t.path, 'abc', '.venv'))
            self.assertEqual(matching, os.path.join(t.path, 'abc'))

    def test_find_recursive_path_local_env_none(self):
        with TemporaryDirectory():
            os.makedirs(os.path.join('abc', 'def'))
            os.chdir(os.path.join('abc', 'def'))
            path, matching = find_recursive_path_local_env('2.7')
            self.assertIsNone(path)
            self.assertIsNone(matching)

    def test_find_virtualenv_local(self):
        with TemporaryDirectory() as t:
            os.makedirs(os.path.join('abc', 'def'))
            os.makedirs(os.path.join('abc', '.venv'))
            os.chdir(os.path.join('abc', 'def'))
            path, matching = find_virtualenv('2.7')
            self.assertEqual(path, os.path.join(t.path, 'abc', '.venv'))
            self.assertEqual(matching, os.path.join(t.path, 'abc'))

    def test_find_virtualenv_recursive_path_virtualenv_dir(self):
        with TemporaryDirectory() as t, TemporaryDirectory(change_directory=False) as virtualenv_dir:
            with TemporaryEnvironment(VENV_DIR=virtualenv_dir.path):
                os.mkdir(os.path.join(virtualenv_dir.path, 'abc-2.7'))
                os.makedirs(os.path.join('abc', 'def'))
                os.chdir(os.path.join('abc', 'def'))
                path, matching = find_virtualenv('2.7')
                self.assertEqual(path, os.path.join(virtualenv_dir.path, 'abc-2.7'))
                self.assertEqual(matching, os.path.join(t.path, 'abc'))

    def test_find_virtualenv_recursive_path_local_dir(self):
        with TemporaryDirectory() as t:
                os.makedirs(os.path.join('abc', 'def'))
                os.makedirs(os.path.join('abc', '.venv'))
                os.chdir(os.path.join('abc', 'def'))
                path, matching = find_virtualenv('2.7')
                self.assertEqual(path, os.path.join(t.path, 'abc', '.venv'))
                self.assertEqual(matching, os.path.join(t.path, 'abc'))

    def test_get_virtualenv_path_non_existent(self):
        with TemporaryDirectory(), TemporaryDirectory(change_directory=False) as virtualenv_dir:
            with TemporaryEnvironment(VENV_DIR=virtualenv_dir.path):
                venv, matching = get_virtualenv_path('2.7')
                self.assertIsNone(venv)
                self.assertIsNone(matching)

    def test_get_virtualenv_path_existent(self):
        with TemporaryDirectory() as t, TemporaryDirectory(change_directory=False) as virtualenv_dir:
            with TemporaryEnvironment(VENV_DIR=virtualenv_dir.path):
                os.mkdir(os.path.join(t.path, 'test_path'))
                env_path, matched_path = get_virtualenv_path('2.7', os.path.join(t.path, 'test_path'))
                self.assertEqual(os.path.join(t.path, 'test_path'), env_path)
                self.assertIsNone(matched_path)

    def test_get_virtualenv_path_virtualenv_dir(self):
        with TemporaryDirectory() as t, TemporaryDirectory(change_directory=False) as virtualenv_dir:
            with TemporaryEnvironment(VENV_DIR=virtualenv_dir.path):
                os.mkdir(os.path.join(virtualenv_dir.path, 'test_path'))
                os.mkdir('test_path')
                os.chdir('test_path')
                env_path, matched_path = get_virtualenv_path('2.7')
                self.assertEqual(os.path.join(virtualenv_dir.path, 'test_path'), env_path)
                self.assertEqual(os.path.join(t.path, 'test_path'), matched_path)

    def test_get_virtualenv_path_virtualenv_dir_version(self):
        with TemporaryDirectory() as t, TemporaryDirectory(change_directory=False) as virtualenv_dir:
            with TemporaryEnvironment(VENV_DIR=virtualenv_dir.path):
                os.mkdir(os.path.join(virtualenv_dir.path, 'test_path'))
                os.mkdir('test_path')
                os.chdir('test_path')
                env_path, matched_path = get_virtualenv_path('2.7')
                self.assertEqual(os.path.join(virtualenv_dir.path, 'test_path'), env_path)
                self.assertEqual(os.path.join(t.path, 'test_path'), matched_path)

    def test_get_virtualenv_path_virtualenv_dir_version_valid(self):
        with TemporaryDirectory() as t, TemporaryDirectory(change_directory=False) as virtualenv_dir:
            with TemporaryEnvironment(VENV_DIR=virtualenv_dir.path):
                os.mkdir(os.path.join(virtualenv_dir.path, 'test_path-2.7'))
                os.mkdir('test_path')
                os.chdir('test_path')
                env_path, matched_path = get_virtualenv_path('2.7')
                self.assertEqual(os.path.join(virtualenv_dir.path, 'test_path-2.7'), env_path)
                self.assertEqual(os.path.join(t.path, 'test_path'), matched_path)

    def test_check_input_path_none(self):
        # Max depth = 2
        with TemporaryDirectory(), TemporaryDirectory(change_directory=False) as virtualenv_dir:
            with TemporaryEnvironment(VENV_DIR=virtualenv_dir.path):
                env_path = check_input_path(None, 2)
                self.assertIsNone(env_path)
                env_path = check_input_path('3.6', 2)
                self.assertIsNone(env_path)

    def test_check_input_path_with_version(self):
        with TemporaryDirectory() as t:
            os.mkdir('.venv-2.7')
            env_path = check_input_path('.venv', '2.7')
            self.assertEqual(os.path.join(t.path, '.venv-2.7'), env_path)

    def test_check_input_path_with_version_none(self):
        with TemporaryDirectory(), TemporaryDirectory(change_directory=False) as virtualenv_dir:
            with TemporaryEnvironment(VENV_DIR=virtualenv_dir.path):
                os.mkdir('.venv-2.7')
                env_path = check_input_path('.venv', '3.6')
                self.assertIsNone(env_path)

    def test_check_input_path_without_version(self):
        with TemporaryDirectory() as t, TemporaryDirectory(change_directory=False) as virtualenv_dir:
            with TemporaryEnvironment(VENV_DIR=virtualenv_dir.path):
                os.mkdir('.venv')
                env_path = check_input_path('.venv', '2.7')
                self.assertEqual(os.path.join(t.path, '.venv'), env_path)

    def test_check_input_path_with_version_virtualenv_dir(self):
        with TemporaryDirectory(), TemporaryDirectory(change_directory=False) as virtualenv_dir:
            with TemporaryEnvironment(VENV_DIR=virtualenv_dir.path):
                os.mkdir(os.path.join(virtualenv_dir.path, 'test-2.7'))
                env_path = check_input_path('test', '2.7')
                self.assertEqual(os.path.join(virtualenv_dir.path, 'test-2.7'), env_path)

    def test_check_input_path_with_version_none_virtualenv_dir(self):
        with TemporaryDirectory(), TemporaryDirectory(change_directory=False) as virtualenv_dir:
            with TemporaryEnvironment(VENV_DIR=virtualenv_dir.path):
                os.mkdir(os.path.join(virtualenv_dir.path, 'test-2.7'))
                env_path = check_input_path('test', '3.6')
                self.assertIsNone(env_path)

    def test_check_input_path_without_version_virtualenv_dir(self):
        with TemporaryDirectory(), TemporaryDirectory(change_directory=False) as virtualenv_dir:
            with TemporaryEnvironment(VENV_DIR=virtualenv_dir.path):
                os.mkdir(os.path.join(virtualenv_dir.path, 'test-2.7'))
                env_path = check_input_path('test', '2.7')
                self.assertEqual(os.path.join(virtualenv_dir.path, 'test-2.7'), env_path)

    def test_get_virtualenv_dir(self):
        with TemporaryEnvironment(VENV_DIR='abc'):
            self.assertEqual(get_virtualenv_dir(), 'abc')

    def test_get_virtualenv_dir_default(self):
        with TemporaryEnvironment():
            os.environ.pop('VENV_DIR')
            self.assertEqual(get_virtualenv_dir(),
                             os.path.join(os.path.expanduser('~'), 'virtualenvs'))


if __name__ == "__main__":
    unittest.main()
