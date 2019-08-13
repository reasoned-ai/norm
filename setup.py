# -*- coding: utf-8 -*-
import io
import os
import sys
import errno
from shutil import rmtree
from setuptools import setup, Command
from distutils.command.install import install

# Package meta-data.
NAME = 'pynorm'
DESCRIPTION = 'A probabilistic logic programming library for data science'
URL = 'https://github.com/reasoned-ai/norm'
EMAIL = 'xu@reasoned.ai'
AUTHOR = 'Xu Miao'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.1.8'

with io.open('requirements.txt') as f:
    REQUIRED = [line.split('==')[0] for line in f.readlines()]

EXTRAS = {}

with io.open('README.md', encoding='utf-8') as f:
    long_description = f.read()

BASEDIR = os.path.abspath(os.path.dirname(__file__))
PACKAGES = [
    'norm',
    'norm.db',
    'norm.executable',
    'norm.grammar',
    'norm.models'
]


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(BASEDIR, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(VERSION))
        os.system('git push --tags')

        sys.exit()


class InstallCommand(install):

    def run(self):
        install.run(self)
        home_dir = os.environ.get('NORM_HOME', '~/.norm')
        try:
            os.mkdir(home_dir)
            os.mkdir(os.path.join(home_dir, 'db'))
            os.mkdir(os.path.join(home_dir, 'data'))
            os.system('cp {}/norm/db/norm.db {}/db/norm.db'.format(BASEDIR, home_dir))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
            print('\n\t\033[1;31;47m.norm\033[0m already exists, delete it first if you would like to overwrite\n')


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=PACKAGES,
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    zip_safe=False,
    include_package_data=True,
    package_data={
        'norm': ['*.py', '*.db', '*.parq', '*.csv', '*.jsonl']
    },
    license='Apache 2.0',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
        'install': InstallCommand
    },
)
