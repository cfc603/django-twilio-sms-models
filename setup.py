#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')

version = get_version('django_twilio_sms', '__init__.py')

if sys.argv[-1] == 'publish':
    try:
        import wheel
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on github:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='django-twilio-sms-models',
    version=version,
    description="""Django models for Twilio's Programmable SMS""",
    long_description=readme + '\n\n' + history,
    author='Trevor Watson',
    author_email='trevor@trevorwatson.me',
    url='https://github.com/cfc603/django-twilio-sms-models',
    packages=[
        'django_twilio_sms',
    ],
    include_package_data=True,
    install_requires=[
        'twilio>=5.4.0',
        'Django>=1.8.0',
        'django-twilio>=0.8.0',
        'django-phonenumber-field>=1.1.0',
    ],
    license="BSD",
    zip_safe=False,
    keywords='django-twilio-sms-models',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
