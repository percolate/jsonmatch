# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='jsonmatch',
    version='0.3',
    author="jamesob, bcen",
    author_email='bocai@percolate.com',
    packages=['jsonmatch'],
    install_requires=['future==0.16.0'],
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
