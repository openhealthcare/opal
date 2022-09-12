import os
import re
from setuptools import setup, find_packages

long_desc = """
Opal is a web framework for building highly usable healthcare applications.

Opal builds deep clinical domain specific functionality on top of Django, Angular
and Bootstrap to help developers quickly build easy to maintain,
robust clinical applications.

Full documentation is available at http://opal.openhealthcare.org.uk/docs/
Source code is available at https://github.com/openhealthcare/opal/
"""

# allow setup.py to be run from any path
HERE = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

VERSION_FILE = os.path.join(HERE, "opal/_version.py")
verstrline = open(VERSION_FILE, "rt").read()
VSRE = r'^__version__ = [\'"]([^\'"]*)[\'"]'
mo = re.search(VSRE,  verstrline, re.M)
if mo:
    VERSION = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in {0}".format(VERSION_FILE))


setup(
    name='opal',
    version=VERSION,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    license='GPL3',  # example license
    description='A web framework for building highly usable healthcare applications.',
    long_description=long_desc,
    url='http://opal.openhealthcare.org.uk/',
    author='Open Health Care UK',
    author_email='hello@openhealthcare.org.uk',
    entry_points={
        'console_scripts': [
            'opal = opal.core.commandline:main'
        ]
    },
    install_requires=[
        # We pin kombu because kombu 5.3 imports does not work on python 3.6.9
        'kombu==5.1.0',
        'ffs>=0.0.8.2',
        'Jinja2==2.10.1',
        'django==2.2.16',
        'requests==2.25.0',
        'djangorestframework==3.12.2',
        'django-reversion==3.0.8',
        'django-compressor==2.4',
        'python-dateutil==2.8.1',
        'django-celery-results==2.0.0',
        'celery==5.0.2',
        'MarkupSafe==1.1.1', # required for python 3.5
        'six==1.15.0'
        ],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
