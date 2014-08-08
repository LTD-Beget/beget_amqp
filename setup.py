#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


package_folder = 'beget_amqp'

setup(name=package_folder,
      version='0.1.3',
      description='AMQP server with Workers, Manager, Callbacks and queue by tag',
      author='LTD Beget',
      author_email='support@beget.ru',
      url='http://beget.ru',
      license="GPL",
      install_requires=['pika'],
      packages=[package_folder,
                package_folder + '.lib',
                package_folder + '.lib.dependence',
                package_folder + '.lib.message'])
