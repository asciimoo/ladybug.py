# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name = 'ladybug',
    version = '0.0.1',
    author = 'Dániel Kántor',
    author_email = 'kdani3@gmail.com',
    description = ('Handle CSV files using table models and queries.'),
    license = 'GPLv3+',
    keywords = "CSV data model table query",
    url = 'https://github.com/kdani3/ladybug.py',
    scripts = [],
    py_modules = ['ladybug'],
    packages = find_packages(),
    install_requires = [],
    download_url = 'https://github.com/kdani3/ladybug.py/tarball/master',
    # TODO
    #entry_points={
    #    "console_scripts": ["ladybug=ladybug:__main__"]
    #},
    classifiers = [
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3'
    ],
)

