# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
        install_requires = f.read().strip().split('\n')

# get version from __version__ variable in nueoo_journey/__init__.py
from tablix import __version__ as version

setup(
	name='tablix',
	version=version,
	description='Tablix',
	author='sahil',
	author_email='sahil19893@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
