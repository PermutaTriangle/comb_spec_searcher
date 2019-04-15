#!/usr/bin/env python
import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="comb_spec_searcher",
    version="0.0.1",
    author="Permuta Triangle",
    author_email="christianbean@ru.is",
    description="A library for performing combinatorial exploration.",
    license="BSD-3",
    keywords="enumerative combinatorics combinatorial specification counting",
    url="https://github.com/PermutaTriangle/comb_spec_searcher",
    project_urls={
        'Source': 'https://github.com/PermutaTriangle/comb_spec_searcher',
        'Tracker': 'https://github.com/PermutaTriangle/comb_spec_searcher/issues'
    },




    maintainer="Christian Bean",
    maintainer_email="christianbean@ru.is",
    install_requires=read("requirements.txt").splitlines(),
    packages=find_packages(),
    long_description=read("README.md"),
)
