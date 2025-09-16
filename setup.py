#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import configparser
import os

# Read version from __init__.py
import re
with open(os.path.join(os.path.dirname(__file__), "amilib", "__init__.py")) as f:
    content = f.read()
version = re.search(r'__version__ = ["\']([^"\']+)["\']', content).group(1)

# Read README
try:
    with open('README.md', encoding='utf-8') as readme_file:
        readme = readme_file.read()
except FileNotFoundError:
    readme = "amilib: A library for processing and analyzing scientific documents"

# Core dependencies actually used by amilib modules
requirements = [
    'lxml',           # XML/HTML processing
    'requests',       # HTTP requests
    'chardet',        # Character encoding detection
    'pandas',         # Data manipulation
    'numpy',          # Numerical operations
    'pdfplumber',     # PDF processing
    'pymupdf',        # PDF processing (fitz)
    'selenium',       # Web automation
    'webdriver-manager', # Chrome driver management
    'SPARQLWrapper',    # SPARQL querying
]

# Optional dependencies for specific features
optional_requirements = {
    'graph': [
        'graphviz',    # Graph visualization
        'networkx',    # Graph algorithms
        'matplotlib',  # Plotting
    ],
    'config': [
        'configparser', # Configuration file parsing
    ]
}

setup(
    name='amilib',
    version=version,
    description='A library for processing and analyzing scientific documents',
    long_description_content_type='text/markdown',
    long_description=readme,
    author='Peter Murray-Rust',
    author_email='pm286@cam.ac.uk',
    url='https://github.com/petermr/amilib',
    packages=['amilib'],
    package_dir={'amilib': 'amilib'},
    include_package_data=True,
    install_requires=requirements,
    extras_require=optional_requirements,
    license='Apache License 2.0',
    zip_safe=False,
    keywords='scientific documents, PDF processing, HTML processing, text analysis',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: XML',
    ],
    entry_points={
        'console_scripts': [
            'amilib=amilib.amix:main',
        ],
    },
    python_requires='>=3.8',
) 
