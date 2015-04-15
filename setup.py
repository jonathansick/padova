#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup, find_packages
import os
import codecs


PACKAGENAME = 'padova'
DESCRIPTION = 'Helpers for using Padova isochrones.'
LONG_DESCRIPTION = ''
AUTHOR = 'Jonathan Sick'
AUTHOR_EMAIL = 'jonathansick@mac.com'
LICENSE = 'MIT'
URL = 'http://github.com/jonathansick/padova'


def read(filename):
    full_filename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        filename)
    return unicode(codecs.open(full_filename, encoding='utf-8').read())

long_description = '\n\n'.join([read('README.rst'),
                                read('CHANGES.rst')])


setup(
    name=PACKAGENAME,
    # Versions should comply with PEP440.
    # (http://www.python.org/dev/peps/pep-0440)
    version='0.1.2',
    description=DESCRIPTION,
    long_description=long_description,
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='astronomy stellarpopulations',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['requests',
                      'numpy',
                      'astropy',
                      'pytoml'],
    tests_require=['pytest',
                   'pytest-pep8',
                   'pytest-cov'],

    package_data={
        'padova': ['data/settings/cmd_2_6.toml'],
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
