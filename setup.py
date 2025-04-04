#!/usr/bin/env python
import os

from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


setup(
    name="comb_spec_searcher",
    version=get_version("comb_spec_searcher/__init__.py"),
    author="Permuta Triangle",
    author_email="permutatriangle@gmail.com",
    description="A library for performing combinatorial exploration.",
    license="BSD-3",
    keywords="enumerative combinatorics combinatorial specification counting",
    url="https://github.com/PermutaTriangle/comb_spec_searcher",
    project_urls={
        "Source": "https://github.com/PermutaTriangle/comb_spec_searcher",
        "Tracker": ("https://github.com/PermutaTriangle/comb_spec_searcher" "/issues"),
    },
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data={"comb_spec_searcher": ["py.typed"]},
    long_description=read("README.rst"),
    python_requires=">=3.8",
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    install_requires=[
        "logzero==1.7.0",
        "sympy==1.13.3",
        "psutil==7.0.0",
        "pympler==1.1",
        "requests==2.32.3",
        "typing-extensions==4.13.1",
        "tabulate==0.9.0",
    ],
)
