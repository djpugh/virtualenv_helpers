"""
create a virtual environment for a repository, either in a local folder or
the default virtual environment directory (which can be overridden using
VIRTUALENV_DIR environment variable)
"""
import os
import sys
import subprocess
import glob
import argparse

import pkg_resources

# from . import __version__
__version__ = 'abc'

default_env_dir = os.path.join(os.path.expanduser('~'), 'virtualenvs')
virtualenv_dir = os.environ.get('VENV_DIR', default_env_dir)
is_windows = sys.platform.startswith('win')

if is_windows:
    SCRIPT_DIR = 'Scripts'
    PIP = 'pip.exe'
    PYTHON = 'python.exe'
else:
    SCRIPT_DIR = 'bin'
    PIP = 'pip'
    PYTHON = 'python'


def parse_options(args=None):
    parser = argparse.ArgumentParser(description="Create a virtual environment for the current directory")
    parser.add_argument(dest='name', metavar='Name', type=str, nargs='?', help='Name of the virtualenv', default=None)
    parser.add_argument('-l', '--local', action="store_true", dest='local', help="Create the virtualenv folder locally - .venv")
    parser.add_argument('-d', '--directory', dest='virtualenv_dir', help="Directory to store the virtualenvironment directory", default=virtualenv_dir)
    parser.add_argument('-p', '--py-version', '--python-version', dest='py_version', help="Create a virtualenv environment for a specific python version", default=None, nargs='+', action='append')
    parser.add_argument('-3', '--py3', '--py3.5', dest='py35', help="Create a virtualenv for python 2.7", default=False, action="store_true")
    parser.add_argument('-2', '--py2', '--py2.7', dest='py27', help="Create a virtualenv for python 3.5", default=False, action="store_true")
    parser.add_argument('--py3.6', '--py36', dest='py36', help="Create a virtualenv for python 3.6", default=False, action="store_true")
    parser.add_argument('--ignore-current-version', dest='ignore_current_version', help="Do not create a virtual environment for the current python version", default=False, action="store_true")
    parser.add_argument('-V', '--version', action="version", version="%(prog)s {}".format(__version__))
    # Help message parsing
    show_help = False
    if args is None and ('-h' in sys.argv or '--help' in sys.argv):
        show_help = True
    elif args is not None and ('-h' in args or '--help' in args):
        show_help = True
    if show_help:
        # Call for virtualenv help
        try:
            output = subprocess.check_output(['virtualenv', '-h'])
        except:
            print('virtualenv not found, please make sure it is installed')
            raise SystemExit(1)
        # Parse the args and catch the system exit
        try:
            options, unknown = parser.parse_known_args(args)
        except SystemExit as e:
            print('\nvirtualenv options can also be passed in, these are:')
            print('\n'.join(output.split('Options:')[-1].splitlines()[2:]))
            raise e
    return options, unknown


def get_python_versions(options):
    python_versions = []
    current_version = sys.version_info
    if not options.ignore_current_version:
        python_versions.append('{}.{}'.format(current_version.major, current_version.minor))
    if options.py35:
        python_versions.append('3.5')
    if options.py27:
        python_versions.append('2.7')
    if options.py36:
        python_versions.append('3.6')
    if options.py_version is not None:
        versions = []
        for ver in options.py_version:
            versions += ver  # This is always a list due to nargs='+' so can extend the versions list
        # Check the versions are correct
        python_versions += [ver.lower().lstrip('py').lstrip('thon') for ver in versions]  # Split lstrip in case of py2.7 or python2.7
    # Remove duplicate versions
    return list(set(python_versions))


def get_python_executable(version):
    executable = None
    if is_windows:
        if sys.version_info.major == 2:
            import _winreg as winreg
        else:
            import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Python\\PythonCore\\{}\\InstallPath".format(version), 0, winreg.KEY_READ) as key:
                path = winreg.QueryValue(key, None)
                executable = '{}python.exe'.format(path)
        except WindowsError:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "Software\\Python\\PythonCore\\{}\\InstallPath".format(version), 0, winreg.KEY_READ) as key:
                    path = winreg.QueryValue(key, None)
                    executable = '{}python.exe'.format(path)
            except WindowsError:
                pass
        if executable is None:
            raise ValueError('Executable for Python {} not found in the registry'.format(version))
    else:
        executable = 'python{}'.format(version)
    return executable


def install_windows_wheels(version, version_virtualenv_dir):
    pip = os.path.join(version_virtualenv_dir, 'Scripts', 'pip.exe')
    wheel_dir = pkg_resources.resource_filename('virtualenv_helpers', 'wheels')
    cpy_version = '-cp{}'.format(version.replace('.', ''))
    py_version = '-py{}'.format(version.split('.')[0])
    py_version2 = '.py{}-'.format(version.split('.')[0])
    wheels = [u for u in glob.glob(os.path.join(wheel_dir, '*.whl')) if 'numpy' not in u and (cpy_version in os.path.split(u)[-1] or py_version in os.path.split(u)[-1] or py_version2 in os.path.split(u)[-1])]
    exes = [u for u in glob.glob(os.path.join(wheel_dir, '*.exe')) if 'numpy' not in u and (cpy_version in os.path.split(u)[-1] or py_version in os.path.split(u)[-1] or py_version2 in os.path.split(u)[-1])]
    argv = [pip, 'install']
    opts = ['--find-links='+wheel_dir, '--prefix='+version_virtualenv_dir, '-U']
    numpy = [u for u in glob.glob(os.path.join(wheel_dir, 'numpy*.whl')) if (cpy_version in os.path.split(u)[-1] or py_version in os.path.split(u)[-1] or py_version2 in os.path.split(u)[-1])]
    if len(numpy):
        numpy = numpy[0]
        subprocess.call(argv+[numpy]+opts, stdout=sys.stdout, stderr=sys.stderr)
    for wheel in wheels:
        subprocess.call(argv+[wheel]+opts, stdout=sys.stdout, stderr=sys.stderr)
    easy_install = os.path.join(version_virtualenv_dir, 'Scripts', 'easy_install.exe')
    # Use easy_install to install any exe files
    for exe in exes:
        subprocess.call([easy_install, '--prefix', version_virtualenv_dir, exe], stdout=sys.stdout, stderr=sys.stderr)
    pkg_resources.cleanup_resources()


def install_module_as_develop(version_virtualenv_dir):
    if os.path.exists('setup.py'):
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.join(version_virtualenv_dir, 'Lib', 'site-packages')
        subprocess.call([os.path.join(version_virtualenv_dir, SCRIPT_DIR, PYTHON), 'setup.py', 'develop', '--prefix',
                         version_virtualenv_dir],
                        env=env, stdout=sys.stdout, stderr=sys.stderr)


def create(args=None):
    options, unknown = parse_options(args)
    # Handle versions to create for
    python_versions = get_python_versions(options)
    # Unknown args to virtualenv
    argv = ['virtualenv']
    if options.name is None:
        options.name = os.path.split(os.getcwd())[-1]
    if options.local:
        virtualenv_dir = os.path.join(os.getcwd(), '.venv')
    else:
        virtualenv_dir = os.path.join(options.virtualenv_dir, options.name)
    argv += unknown
    for version in python_versions:
        executable = get_python_executable(version)
        # Needs to have the path to the python executable for that version - get it's location from the registry
        version_virtualenv_dir = '{}-{}'.format(virtualenv_dir, version)
        print(argv + [version_virtualenv_dir, '--python', executable])
        subprocess.call(argv + [version_virtualenv_dir, '--python', executable], stdout=sys.stdout, stderr=sys.stderr)
        if is_windows and options.windows_wheels and version_virtualenv_dir:
            # Install into target dir
            install_windows_wheels(version, version_virtualenv_dir)
        # Find the setup.py and run develop if possible
        install_module_as_develop(version_virtualenv_dir)
