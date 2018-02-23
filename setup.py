#!/usr/bin/python
"""

@author: mcosta

"""
from setuptools import setup, find_packages
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))


# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


def get_version():

    with open('version', 'r') as f:
        for line in f:
            version = line

    return version


setup(
        name='spival',

        version=get_version(),

        description='SPICE Kernel Dataset in Git',
        url="https://mcosta@repos.cosmos.esa.int/socci/scm/spice/spival.git",

        author='Marc Costa Sitja (ESA SPICE Service)',
        author_email='esa_spice@sciops.esa.int',

        # Classifiers
        classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 3 - Alpha',
            'Intended Audience :: SPICE and Ancillary Data Engineers, Science Operations Engineers and Developers',
            'Topic :: Git :: Planetary Science :: Geometry Computations',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
        ],

        # Keywords
        keywords=['esa', 'spice', 'naif', 'planetary', 'space', 'geometry'],

        # Packages
        packages=find_packages(),

        # Include additional files into the package
        include_package_data=False,

        # Dependent packages (distributions)
        python_requires='>=3',

        # Scripts
        scripts=['bin/spival']

      )