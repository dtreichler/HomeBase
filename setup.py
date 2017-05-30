from setuptools import setup

version = {}
with open('homebase/version.py') as fp:
    exec(fp.read(), version)

setup(name='HomeBase',
      version=version['__version__'],
      description='PaPiRus based Google Home companion for Raspberry Pi',
      author='Derrick Treichler',
      author_email='dtreichl@gmail.com',
      url='https://github.com/dtreichler/HomeBase',
      packages=['homebase'],
      scripts=['bin/homebase'],
      )
