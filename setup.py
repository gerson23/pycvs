#!/usr/bin/env python3
from distutils.core import setup

setup(name='Pycvs',
      version='0.0.1',
      description='A Python client for CVS projects',
      author='Gerson Carlos',
      author_email='gerson.mtg@gmail.com',
      url='https://github.com/gerson23/pycvs',
      license='MIT',
      scripts=['src/scripts/pycvs'],
      package_dir={'': 'src/python'},
      packages=['pycvs'],
      install_requires=['pexpect', 'colorama']
      )
