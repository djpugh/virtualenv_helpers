"""
find.py
*******
Find the virtual environment path based on either
name/path or recursive searching of the path or from the VENV_DIR
environmental variable directory.
"""
import os


def get_virtualenv_dir():
    """Get the virtual environment from the environmental variables"""
    default_env_dir = os.path.join(os.path.expanduser('~'), 'virtualenvs')
    return os.environ.get('VENV_DIR', default_env_dir)


def recursive_check(check_function, python_version, max_levels=None):
    """
    Recursively check a path to see if a virtual environment exists

    Args:
        check_function: the function to use to check if a virtual environment exists
        python_version: python version string

    Keyword Args:
        max_levels: integer number of levels to check (if None, checks to the system root)
    """
    venv_path = None
    matching_path = None
    if os.path.exists(get_virtualenv_dir()):
        # Check if the virtualenv dir exists
        current_dir = os.getcwd()
        can_rise = True
        levels_checked = 0
        while can_rise:
            # Search over higher paths than this one
            if not len(os.path.split(current_dir)[-1]):
                # No more splitting
                break
            levels_checked += 1
            if max_levels is not None:
                can_rise = max_levels > levels_checked
            venv_path, matching_path = check_function(python_version, current_dir)
            if venv_path is not None:
                break
            current_dir = os.path.split(current_dir)[0]
    return venv_path, matching_path


def find_venv_dir_env(python_version, current_dir):
    """
    Find a virtual environment in the virtual environment dir set using the
    VENV_DIR environment variable (defaults to ~/virtualenvs)

    Args:
        python_version: python version string
        current_dir: the current directory being checked
    """
    test_dir = os.path.split(current_dir)[-1]
    if python_version is None:
        test_venv_dir_path = os.path.join(get_virtualenv_dir(), test_dir)
    else:
        test_venv_dir_path = os.path.join(get_virtualenv_dir(), '{}-{}'.format(test_dir, python_version))
    if os.path.exists(test_venv_dir_path):
        return test_venv_dir_path, current_dir
    return None, None


def find_local_env(python_version, current_dir=None, **kwargs):
    """
    Find a virtual environment in the local directory, expected to be called
    .venv

    Args:
        python_version: python version string
        current_dir: the current directory being checked
    """
    venv_name = '.venv'
    if python_version is not None:
        version_venv_name = '{}-{}'.format(venv_name, python_version)
    if current_dir is None:
        current_dir = os.getcwd()
    if python_version is not None:
        test_venv_dir_path = os.path.join(current_dir, version_venv_name)
        if os.path.exists(test_venv_dir_path):
            return test_venv_dir_path, current_dir
    test_venv_dir_path = os.path.join(current_dir, venv_name)
    if os.path.exists(test_venv_dir_path):
        return test_venv_dir_path, current_dir
    return None, None


def find_recursive_path_venv(python_version, max_levels=None):
    """
    Recursively check for a virtual environment in the virtual environment dir
    set using the VENV_DIR environment variable (defaults to ~/virtualenvs)

    Args:
        python_version: python version string

    Keyword Args:
        max_levels: integer number of levels to check (if None, checks to the system root)
    """
    return recursive_check(find_venv_dir_env, python_version, max_levels)


def find_recursive_path_local_env(python_version, max_levels=None):
    """
    Recursively check for a local virtual environment folder (.venv)

    Args:
        python_version: python version string

    Keyword Args:
        max_levels: integer number of levels to check (if None, checks to the system root)
    """
    return recursive_check(find_local_env, python_version, max_levels)


def find_virtualenv(python_version, max_levels=None):
    """
    Find a virual environment directory for the current (or higher) path
    Args:
        python_version: python version string

    Keyword Args:
        max_levels: integer number of levels to check (if None, checks to the system root)
    """
    venv_dir = None
    matching_path = None
    for function in [find_local_env, find_recursive_path_venv, find_recursive_path_local_env]:
        if venv_dir is None:
            venv_dir, matching_path = function(python_version, max_levels=max_levels)
        if venv_dir is None:
            venv_dir, matching_path = function(None, max_levels=max_levels)
    return venv_dir, matching_path


def check_input_path(virtualenv_path, python_version):
    """
    Check if the specified path exists
    Args:
        virtualenv_path: specified path to a virtual environment (may not
                         include the python version)
        python_version: python version string
    """
    if virtualenv_path is None:
        return None
    version_path = '{}-{}'.format(virtualenv_path, python_version)
    if os.path.exists(version_path):
        return os.path.abspath(version_path)
    elif os.path.exists(virtualenv_path):
        return os.path.abspath(virtualenv_path)
    elif os.path.exists(os.path.join(get_virtualenv_dir(), virtualenv_path)):
        return os.path.join(get_virtualenv_dir(), virtualenv_path)
    elif os.path.exists(os.path.join(get_virtualenv_dir(), version_path)):
        return os.path.join(get_virtualenv_dir(), version_path)
    return None


def get_virtualenv_path(python_version, virtualenv_path=None, max_levels=None):
    """
    Get the virtual environment path either by checking if it exists or searching
    for it.
    Args:
        python_version: python version string

    Keyword Args:
        virtualenv_path: specified path to a virtual environment (may not
                         include the python version)
        max_levels: integer number of levels to check (if None, checks to the system root)

    """
    if virtualenv_path is not None:
        matching_path = None
        virtualenv_path = check_input_path(virtualenv_path, python_version)
    else:
        virtualenv_path, matching_path = find_virtualenv(python_version, max_levels)
    return virtualenv_path, matching_path
