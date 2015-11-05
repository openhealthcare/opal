import os
import re
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

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
    packages=['opal', 'opal.utils'],
    include_package_data=True,
    license='GPL3',  # example license
    description='Clinical Transactional Digital Services Framework.',
    long_description=README,
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
        'django-axes==1.3.9',
        'djangorestframework==3.2.2',
        'django-compressor==1.5'
        ]
)
