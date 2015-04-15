#!/usr/bin/env python
# encoding: utf-8

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

# Set affiliated package-specific settings
PACKAGENAME = 'padova'
DESCRIPTION = 'Helpers for using Padova isochrones.'
LONG_DESCRIPTION = ''
AUTHOR = 'Jonathan Sick'
AUTHOR_EMAIL = 'jonathansick@mac.com'
LICENSE = 'MIT'
URL = 'http://github.com/jonathansick/padova'

here = path.abspath(path.dirname(__file__))


# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name=PACKAGENAME,
    # VERSION should be PEP386 compatible
    # (http://www.python.org/dev/peps/pep-0386)
    # Versions should comply with PEP440.
    version='0.1',
    description=DESCRIPTION,
    long_description=long_description,
    url=URL,
    author='AUTHOR',
    author_email='AUTHOR_EMAIL',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='astronomy stellarpopulations',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['requests', 'numpy', 'astropy', 'pytoml'],

    package_data={
        'padova': ['padova/data/settings/*.toml'],
    },

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
)
