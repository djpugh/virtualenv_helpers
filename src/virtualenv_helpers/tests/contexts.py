import tempfile
import warnings
import os
import shutil
import sys


class TemporaryDirectory(object):
    def __init__(self, change_directory=True, *args, **kwargs):
        self.path = os.path.abspath(tempfile.mkdtemp(*args, **kwargs))
        self._change_directory = change_directory
        self._current_directory = None

    def __del__(self):
        self.delete_temporary_directory()

    def __enter__(self):
        if self._change_directory:
            self._current_directory = os.getcwd()
            os.chdir(self.path)
            self.path = os.getcwd()
        elif 'darwin' in sys.platform:
            # Mac seems to link /private/var/... to
            # /var/... for temporary folders, so lets
            # check what the cwd is in that folder
            cwd = os.getcwd()
            os.chdir(self.path)
            self.path = os.getcwd()
            os.chdir(cwd)
        return self

    def __exit__(self, *args, **kwargs):
        if self._change_directory and self._current_directory is not None:
            # Only set if current directory set and we have changed
            os.chdir(self._current_directory)
        self.delete_temporary_directory()

    def delete_temporary_directory(self):
        if not os.path.exists(self.path):
            return
        try:
            shutil.rmtree(self.path)
        except Exception:
            if os.path.exists(self.path):
                warnings.warn('Unable to delete temporary directory', RuntimeWarning)


class TemporaryEnvironment(object):

    def __init__(self, **kwargs):
        self._original_env = None
        self._kwargs = kwargs

    def __enter__(self):
        self._original_env = os.environ.copy()
        os.environ.update(self._kwargs)
        return self

    def __exit__(self, *args, **kwargs):
        if self._original_env is not None:
            os.environ.clear()
            os.environ.update(self._original_env)


class Quiet(object):

    def __init__(self, stdout=True, stderr=True, debug=True):
        if debug and sys.gettrace() is not None:
            # Check if in the debugger and only supress if not
            self.__supress_stdout = False
            self.__supress_stderr = False
        else:
            self.__supress_stdout = stdout
            self.__supress_stderr = stderr

    def __enter__(self):
        if self.__supress_stdout:
            self.__old_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
        if self.__supress_stderr:
            self.__old_stderr = sys.stderr
            sys.stderr = open(os.devnull, 'w')

    def __exit__(self, *args, **kwargs):
        if self.__supress_stdout:
            sys.stdout.seek(0)
            sys.stdout = self.__old_stdout
        if self.__supress_stderr:
            sys.stderr.seek(0)
            sys.stderr = self.__old_stderr
