"""setup.py
***********
virtualenv_helpers install script
"""

from setuptools import setup


kwargs = dict(
    name='test_package',
    version='0.1.0',
    py_modules=['test_module'])


if __name__ == "__main__":
    setup(**kwargs)
