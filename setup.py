#!/usr/bin/env python
import os

from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="comb_spec_searcher",
    version="0.2.1",
    author="Permuta Triangle",
    author_email="christianbean@ru.is",
    description="A library for performing combinatorial exploration.",
    license="BSD-3",
    keywords="enumerative combinatorics combinatorial specification counting",
    url="https://github.com/PermutaTriangle/comb_spec_searcher",
    project_urls={
        'Source': 'https://github.com/PermutaTriangle/comb_spec_searcher',
        'Tracker': ('https://github.com/PermutaTriangle/comb_spec_searcher'
                    '/issues')
    },
    packages=find_packages(),
    long_description=read("README.rst"),
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: PyPy',

        'Topic :: Education',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    install_requires=[
        'logzero==1.5.0',
        'sympy==1.4',
        'psutil==5.6.3'
    ],
    setup_requires=['pytest-runner==5.1'],
    tests_require=[
        'pytest==5.2.2',
        'pytest-cov==2.8.1',
        'pytest-isort==0.3.1',
        'pytest-pep8==1.0.6',
        'pytest-repeat==0.8.0',
        'docutils==0.15.2',
        'Pygments==2.4.2'
    ]
)
