import os
import re
from setuptools import setup, find_packages

long_desc = """
OPAL is a web framework for building highly usable healthcare applications.

OPAL builds deep clinical domain specific functionality on top of Django, Angular
and Bootstrap to help developers quickly build easy to maintain,
robust clinical applications.

Full documentation is available at http://opal.openhealthcare.org.uk/docs/
Source code is available at https://github.com/openhealthcare/opal/
"""

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

HERE = os.path.realpath(os.path.dirname(__file__))

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
    scripts=['bin/opal'],
    install_requires=[
        'ffs>=0.0.8.1',
        'letter',
        'jinja2',
        'requests',
        'django==1.8.3',
        'django-reversion==1.8.7',
        'django-axes==1.4.0',
        'djangorestframework==3.2.2',
        'django-compressor==1.5',
        'python-dateutil==2.4.2',
        'Fabric==1.10.2'
        ]
)
