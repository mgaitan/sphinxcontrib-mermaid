# -*- coding: utf-8 -*-

import io
from setuptools import setup, find_packages

readme = io.open('README.rst', encoding="utf-8").read()
version = '0.1.1'

setup(
    name='sphinxcontrib-mermaid',
    version=version,
    url='https://github.com/mgaitan/sphinxcontrib-mermaid',
    download_url='https://pypi.python.org/pypi/sphinxcontrib-mermaid',
    license='BSD',
    author=u'Martín Gaitán',
    author_email='gaitan@gmail.com',
    description='Mermaid diagrams in yours Sphinx powered docs',
    long_description=readme,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    namespace_packages=['sphinxcontrib'],
)
