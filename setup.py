#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


package_folder = 'beget_amqp'

# Define __version__ without importing beget_amqp.
# This allows building sdist without installing any 3rd party packages.
exec(open(package_folder + '/_version.py').read())

setup(
    name=package_folder,
    version=__version__,
    description='AMQP server with Workers, Manager, Callbacks and queue by tag',
    author='LTD Beget',
    author_email='support@beget.ru',
    url='http://beget.ru',
    license="GPL",
    install_requires=[
        'pika',
        'redis',
        'setproctitle==1.1.8',
        'filelock',
        'redis-collections'
    ],
    dependency_links=[
        'http://github.com/LTD-Beget/setproctitle/tarball/master#egg=setproctitle-1.1.8'
    ],
    packages=[
        package_folder,
        package_folder + '.lib',
        package_folder + '.lib.communicate',
        package_folder + '.lib.consumer',
        package_folder + '.lib.consumer.storage',
        package_folder + '.lib.dependence',
        package_folder + '.lib.dependence.storage',
        package_folder + '.lib.exception',
        package_folder + '.lib.helpers',
        package_folder + '.lib.message',
        package_folder + '.lib.message.storage',
    ]
)
