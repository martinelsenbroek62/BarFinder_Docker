#! /usr/bin/env python

from setuptools import find_packages
from setuptools.extension import Extension

from distutils.core import setup
from Cython.Build import cythonize

ext_modules = []
packages = []
for package in find_packages('/app'):
    if package == 'api_collection.migrations':
        continue
    folder = package.replace('.', '/')
    ext_modules.append(Extension("%s.*" % package, ["%s/*.py" % folder]))
    packages.append(package)

setup(
    name='api_collection',
    ext_modules=cythonize(ext_modules),
    packages=find_packages('/app')
)
