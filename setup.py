# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='jsonmatch',
    version='0.2',
    author="jamesob",
    author_email='jamesob@percolate.com',
    packages=['jsonmatch'],
    test_suite='tests',
    url='https://github.com/percolate/jsonmatch',
    license='see LICENCE.txt',
    description='A flexible framework for testing JSON dicts against schemas.',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
    ],
)
