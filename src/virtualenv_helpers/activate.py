"""
activate.py
***********
Activate a virtualenvironment from the command line, based on either
name/path or recursive searching of the path or from the VENV_DIR
environmental variable directory.
"""

import os
import sys
import subprocess
import argparse

from .find import get_virtualenv_path
from . import __version__
from .editors import editors

if 'win' in sys.platform:
    script_dir = 'Scripts'
else:
    script_dir = 'bin'


def create_parser():
    """Create the command line parser"""
    parser = argparse.ArgumentParser(description='Activate a python virtual environment by searching for a local environment or looking in the VENV_DIR directory')
    parser.add_argument('--path', '--virtualenv-path', dest='virtualenv_path', help='Path to the virtual environment to activate', default=None)
    parser.add_argument('path', help='Path to the virtual environment to activate', default=None, nargs='?')
    parser.add_argument('-p', '--py', '--py-version', dest='python_version', help='Python version of the virtual environment to activate', default=None)
    parser.add_argument('-e', '--editor', dest='editor', help="Editor to load with the virtual environment", default=os.environ.get('VENV_EDITOR', None))
    parser.add_argument('-s', '--show-editor', dest='show_editor', action="store_true", help="Show the editor when working on the virtual environment", default=os.environ.get('VENV_EDITOR_SHOW', None))
    parser.add_argument('-x', '--no-show-editor', dest='no_show_editor', action="store_true", help="Don't show the editor when working on the virtual environment", default=False)
    parser.add_argument('-V', '--version', action="version", version="%(prog)s {}".format(__version__))
    return parser


def parse_options(args=None):
    """
    Parse input arguments for activating the virtual environment

    Keyword Arguments:
        args: list/tuple of arguments, if None, then the command line
              arguments (sys.argv) are used
    """
    parser = create_parser()
    options = parser.parse_args(args)
    if options.path is not None and options.virtualenv_path is not None:
        parser.error('Both --path and positional argument provided for virtual environment path, only one should be used')
    if options.python_version is not None:
        python_version = options.python_version.lower().lstrip('py').lstrip('thon')
    else:
        python_version = '{}.{}'.format(sys.version_info.major, sys.version_info.minor)
    if options.editor is not None:
        options.editor = editors.get(options.editor.lower().replace(' ', ''), None)
    if options.editor is not None:
        if options.show_editor:
            if isinstance(options.show_editor, str) and options.show_editor.lower() == 'true':
                options.show_editor = True
        if options.no_show_editor:
            options.show_editor = False
    else:
        options.show_editor = False
    return options, python_version


def activate(args=None, shell=True):
    """
    Activate the virtual environment.

    Keyword Arguments:
        args: list/tuple of arguments, if None, then the command line
              arguments (sys.argv) are used:
        shell: boolean flag to open the environment in a new shell

    """
    options, python_version = parse_options(args)
    virtualenv_path, matching_path = get_virtualenv_path(options.virtualenv_path, python_version)
    if virtualenv_path is not None:
        path = os.environ.get('PATH', '').split(';')
        path = [u for u in path if 'python' not in u.lower()]
        # Add the virtualenv_path dir to the front of the path
        path = [virtualenv_path, os.path.join(virtualenv_path, script_dir)] + path
        env = os.environ.copy()
        env['PATH'] = ';'.join(path)
        shell, args, script_name = get_shell()
        print('Activating virtual environment {}. Use exit to quit the virtual environment.'.format(virtualenv_path))
        if options.show_editor and matching_path is not None:
            options.editor.start(matching_path, virtualenv_path)
        try:
            subprocess_args = [shell]+args+[os.path.join(virtualenv_path, script_dir, script_name)]
            subprocess.call(subprocess_args, env=env)
        except KeyboardInterrupt:
            pass
    else:
        print('No virtual environment found')


def get_shell():
    """Get the shell type"""
    if 'win32' in sys.platform:
        if os.getenv('SHELL') is not None:
            # Git bash
            shell = os.getenv('SHELL')
            exe = os.path.split(shell)[-1]
            path = os.path.split(os.path.split(os.path.split(shell)[0])[0])[0]
            shell = os.path.join(path, 'bin', exe)
            args = ['--init-file']
            script_name = 'activate'
        elif os.getenv('PROMPT') is None:
            # Powershell
            shell = 'powershell.exe'
            args = ['-NoLogo', '-NoExit', '.']
            script_name = 'activate.ps1'
        else:
            # Command prompt
            shell = 'cmd.exe'
            args = ['/K']
            script_name = 'activate.bat'
    else:
        # nix
        shell = os.getenv('SHELL')
        args = ['--init-file']
        script_name = 'activate'
    return shell, args, script_name
