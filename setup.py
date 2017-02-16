#!/usr/bin/env python
import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "ATRAP",
    version = "0.0.1",
    author = "Henning Ulfarsson",
    author_email = "henningu@ru.is",
    url = "https://github.com/PermutaTriangle/ATRAP",
    install_requires = read("requirements.txt").splitlines(),
    packages = find_packages(),
    long_description = read("README.md"),
)
