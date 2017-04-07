"""
editors.py
**********

Classes for specific editors to open them with the virtual environment in that folder
"""
import subprocess
import os
import glob
import json
import tempfile
import sys


class Editor(object):
    flags = []

    def start(self, folder_path, virtualenv_path=None):
        self.folder_path = folder_path
        self.virtualenv_path = virtualenv_path
        if self.executable is not None:
            subprocess.call([self.executable] + self.flags + [folder_path])

    @property
    def executable(self):
        return None


class SublimeText3(Editor):
    # Add commands for virtualenv to start with the virtualenv path
    # Works with the sublime text virtualenv plugin

    @property
    def executable(self):
        if 'win32' in sys.platform:
            path = 'C:\\Program Files\\Sublime Text 3\\subl.exe'
        else:
            try:
                path = subprocess.check_output(['which', 'sublime_text'])
            except Exception:
                # Check alternate path
                try:
                    path = subprocess.check_output(['which', 'sublime_text3'])
                except Exception:
                    pass
        if os.path.exists(path):
            return path
        else:
            return None

    @property
    def flags(self):
        flags = ['-n']
        # Create the project file if required and then update
        # Check if a .sublime-project exists in the folder path
        if len(glob.glob(os.path.join(self.folder_path, '*.sublime-project'))) == 1:
            project_file = glob.glob(os.path.join(self.folder_path, '*.sublime-project'))[0]
            project_dict = json.loads(open(project_file.read()))
            # update the paths in the folders to be absolute paths to the folder_path
            if 'folders' in project_dict.keys():
                for folder in project_dict['folders']:
                    if 'path' in folder and folder['path'][0] == '.':
                        folder['path'][0] = os.path.abspath(self.folder_path)
        else:
            default_project = {"folders": [{"path": "."}]}
            project_dict = default_project.copy()
            project_dict['folders'] = [{"path": os.path.abspath(self.folder_path)}]
        project_dict['virtualenv'] = self.virtualenv_path
        virtualenv_project_filename = '{} [{}].sublime-project'.format(os.path.split(os.path.abspath(self.folder_path))[-1],
                                                                       os.path.split(self.virtualenv_path)[-1])
        virtualenv_project_file = os.path.join(tempfile.mkdtemp(), virtualenv_project_filename)
        open(virtualenv_project_file, 'w').write(json.dumps(project_dict))
        return flags + ['--project', virtualenv_project_file]


editors = {'sublimetext3': SublimeText3()}
