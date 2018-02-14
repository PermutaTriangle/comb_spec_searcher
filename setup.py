#!/usr/bin/env python
import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="comb_spec_searcher",
    version="0.0.1",
    author="Henning Ulfarsson",
    maintainer="Christian Nathaniel Bean",
    maintainer_email="christianbean@ru.is",
    author_email="henningu@ru.is",
    url="https://github.com/PermutaTriangle/comb_spec_searcher",
    description="Combinatorial specification searcher",
    install_requires=read("requirements.txt").splitlines(),
    packages=find_packages(),
    long_description=read("README.md"),
)
