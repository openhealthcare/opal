import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='opal',
    version='0.1',
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
        'ffs',
        'letter',
        'jinja2',
        'requests',
        'django==1.5.2',
        'South==0.8.1',
        'django-reversion==1.8.0',
        'django-axes==1.3.4'
        ]
)
