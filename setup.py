#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path

from setuptools import setup

# Read version from __init__.py
import re

parent = Path(__file__).parent
with open(str(Path(parent, "amilib", "__init__.py"))) as f:
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
    author='Peter Murray-Rust and semanticClimate team',
    author_email='pm286@cam.ac.uk',
    url='https://github.com/petermr/amilib',
    packages=['amilib'],
    package_dir={'amilib': 'amilib'},
    include_package_data=True,
    install_requires=requirements,
    extras_require=optional_requirements,
    license='Apache License 2.0',
    license_files=[],  # Prevent automatic License-File metadata field
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
