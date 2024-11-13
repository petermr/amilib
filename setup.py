try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# with open('requirements.txt') as f:
#    required = f.read().splitlines()

with open('README.md') as readme_file:
    readme = readme_file.read()

long_desc = """
amilib is a library for downloading, cleaning, annotating, documents of various sorts (HTML, PDF, XML)"""


requirements = [
 'lxml',
 'nltk',
 'pdfminer3',
 'Pillow',
 'setuptools',
 'pdfplumber',
 'requests',
 'numpy==1.24.1',
 'pandas==2.0.3',
 'pyvis',
 'selenium',
 'tinycss',
 'SPARQLWrapper',
 'Tkinterweb',
 'webdriver-manager',
 'scikit-learn==1.3.2',

]

setup(
    name='amilib',
    url='https://github.com/petermr/amilib',
    version='0.4.1',
    description='document and dictionary download, cleaning, management',
    long_description_content_type='text/markdown',
    long_description=readme,
    author="Peter Murray-Rust",
    author_email='petermurrayrust@googlemail.com',
    license='Apache2',
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False,
    keywords='text and data mining',
    packages=[
        'amilib'
    ],
    package_dir={'amilib': 'amilib'},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.8',
#        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.12',
    ],
    entry_points={
        'console_scripts': [
            'amilib=amilib.amix:main',
        ],
    },
    python_requires='>=3.7,<3.13',
)
