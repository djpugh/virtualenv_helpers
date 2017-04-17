"""test_virtualenv_helpers/editors.py
**************************************
Provides unit tests for virtualenv_helpers/editors.py
"""

import unittest
import sys
import os
import tempfile


from virtualenv_helpers.editors import Editor
from virtualenv_helpers.editors import SublimeText3


class EditorTestCase(unittest.TestCase):

    def setUp(self):
        self.editor = Editor()

    def tearDown(self):
        del self.editor

    def test_flags(self):
        self.assertEqual(self.editor.flags, [])

    def test_executable(self):
        self.assertIsNone(self.editor.executable)


class SublimeText3TestCase(unittest.TestCase):

    def setUp(self):
        self.sublime_text_3 = SublimeText3()

    def tearDown(self):
        del self.sublime_text_3

    @unittest.skipIf(not sys.platform.startswith('win'), 'Test requires windows')
    def test_executable_windows(self):
        self.assertIn('subl.exe', self.sublime_text_3.executable)

    @unittest.skipIf(sys.platform.startswith('win'), 'Test requires linux')
    def test_executable_nix(self):
        self.assertIn('sublime_text', self.sublime_text_3.executable)

    def test_flags(self):
        self.sublime_text_3.folder_path = os.getcwd()
        self.sublime_text_3.virtualenv_path = None
        self.assertIn('-n', self.sublime_text_3.flags)

    def test_flags_with_virtualenv_path(self):
        self.sublime_text_3.folder_path = os.getcwd()
        self.sublime_text_3.virtualenv_path = tempfile.mkdtemp()
        self.assertIn('-n', self.sublime_text_3.flags)
        self.assertIn('--project', self.sublime_text_3.flags)


if __name__ == "__main__":
    unittest.main()
