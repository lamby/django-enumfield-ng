#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-enumfield-ng',
    description="Type-safe, efficient & database-agnostic enumeration field "
        'for Django.',
    version='1.1.0',

    url="https://chris-lamb.co.uk/projects/django-enumfield",
    author="Chris Lamb",
    author_email='chris@chris-lamb.co.uk',
    license='BSD',

    packages=find_packages(),

    install_requires=(
        'Django>=1.8',
        'six',
    ),
)
