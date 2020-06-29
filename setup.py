#!/usr/bin/env python
import os

from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="comb_spec_searcher",
    version="1.2.0",
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
    packages=find_packages(),
    package_data={"comb_spec_searcher": ["py.typed"]},
    long_description=read("README.rst"),
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    # fmt: off
    # Disable formatting until this is solved https://github.com/psf/black/issues/1288
    install_requires=[
        "logzero==1.5.0",
        "sympy==1.6",
        "psutil==5.7.0",
        "pympler==0.8",
    ],
    # fmt: on
)
