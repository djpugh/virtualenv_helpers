"""setup.py
***********
virtualenv_helpers install script
"""
import sys

from setuptools import setup
from setuptools import find_packages

import versioneer

__version__ = versioneer.get_version()
__maintainer__ = "David Pugh"
__email__ = "djpugh@gmail.com"
__description__ = """(Windows) Virtualenv helpers"""

virtualenv_console = 'create_venv'
if sys.version_info[0] > 2:
    virtualenv_console = virtualenv_console+'3'

tests_require = ['virtualenv']

kwargs = dict(
    name='virtualenv_helpers',
    packages=find_packages('src'),
    version=__version__,
    cmdclass=versioneer.get_cmdclass(),
    package_dir={'': 'src'},
    description=__description__,
    author=__maintainer__,
    requires=['virtualenv', 'pip'],
    tests_require=tests_require,
    install_requires=['setuptools'],
    author_email=__email__,
    entry_points={'console_scripts': [
        'workon = virtualenv_helpers.activate:activate',
        '{} = virtualenv_helpers.create:create'.format(virtualenv_console)]},
    keywords=[],
    classifiers=[],
    test_suite='virtualenv_helpers.tests.test_suite',
    package_data={'': ['*.txt',
                       'docs/source/*.rst',
                       'docs/man/*',
                       'docs/epub/*.epub',
                       'docs/pdf/*',
                       'docs/html/*.*',
                       'docs/html/*/*.*',
                       'docs/rst/*.*',
                       'docs/rst/*/*.*',
                       'docs/html/*/*/*.*'],
                  })


if __name__ == "__main__":
    setup(**kwargs)
