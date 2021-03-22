#! /usr/bin/env python

import os
from setuptools import find_packages
from setuptools.extension import Extension

from distutils.core import setup
from Cython.Build import cythonize

ext_modules = [
    Extension('alphabet', ['alphabet.py']),
    Extension('words', ['words.py']),
]
packages = []
for package in find_packages('/DecodeEngine'):
    folder = package.replace('.', '/')
    ext_modules.append(Extension("%s.*" % package, ["%s/*.py" % folder]))
    packages.append(package)

setup(
    name='DecodeEngine',
    ext_modules=cythonize(ext_modules),
    packages=packages
)
