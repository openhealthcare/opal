"""
Opal comandline tool.

In which we expose useful commandline functionality to our users.
"""
import argparse
import os
import subprocess
import sys

import ffs

import opal
from opal.core import scaffold as scaffold_utils
from opal.core import test_runner
from opal.utils import write

USERLAND_HERE    = ffs.Path('.').abspath
OPAL             = ffs.Path(opal.__file__).parent


def find_application_name():
    """
    Return the name of the current Opal application
    """
    for d in USERLAND_HERE.ls():
        if d.is_dir:
            if d/'settings.py':
                return d[-1]

    write("\n\nCripes!\n")
    write("We can't figure out what the name of your application is :(\n")
    write("Are you in the application root directory? \n\n")
    sys.exit(1)


def startproject(args):
    scaffold_utils.start_project(args.name, USERLAND_HERE)
    return


def startplugin(args):
    """
    The steps to create our plugin are:

    * Copy across the scaffold to our plugin directory
    * Interpolate our name into the appropriate places.
    * Rename the code dir
    * Create template/static directories
    """
    scaffold_utils.start_plugin(args.name, USERLAND_HERE)
    return


def test(args):
    args.userland_here = USERLAND_HERE
    args.opal_location = OPAL.parent
    test_runner.run_tests(args)
    return


def check_for_uncommitted():
    changes = subprocess.check_output(["git", "status", "--porcelain"])
    return len(changes)


def get_requirements():
    """
    looks for a requirements file in the same directory as the
    fabfile. Parses it,
    """

    with USERLAND_HERE:
        requirements = subprocess.check_output(
            ["less", "requirements.txt"]
        ).split("\n")

        package_to_version = {}

        for requirement in requirements:
            parsed_url = parse_github_url(requirement)

            if parsed_url:
                package_to_version.update(parsed_url)

    return package_to_version


def parse_github_url(some_url):
    """
    takes in something that looks like a Github url in a requirements.txt
    file and returns the package name
    """

    if "github" in some_url and "opal" in some_url:
        package_name = some_url.split("@")[0].split("/")[-1]
        package_name = package_name.replace(".git", "")
        version = some_url.split("@")[-1].split("#")[0]
        return {package_name: version}


def checkout(args):
    """
    This is our main entrypoint for the checkout command.
    """
    package_name_version = get_requirements()
    SOURCE_DIR = USERLAND_HERE.parent
    with SOURCE_DIR:
        ls_source = [str(f) for f in SOURCE_DIR.ls()]
        uncommitted = []

        for package_name, version in package_name_version.items():
            if package_name in ls_source:
                with SOURCE_DIR/package_name:
                    if check_for_uncommitted():
                        uncommitted.append(package_name)

        if len(uncommitted):
            write("We have uncommitted changes in {}".format(
                ", ".join(uncommitted)
            ))
            write('Abandonning attempt to check out to requirements.txt')
            return

        for package_name, version in package_name_version.items():
            if package_name in ls_source:
                with SOURCE_DIR/package_name:
                    write("checking out {0} to {1}".format(
                        package_name, version
                    ))
                    os.system("git checkout {}".format(version))
                    os.system("python setup.py develop")
            else:
                write('Unable to checkout versions from requirements')
                write('{0} is missing'.format(package_name))
                return


def parse_args(args):
    """
    Set up Argparse argument parser and route ourselves to the
    target function.
    """
    description = "Opal - a full stack web framework for health " \
                  "care applications."
    parser = argparse.ArgumentParser(
        description=description,
        usage="opal <command> [<args>]",
        epilog="Brought to you by Open Health Care UK"
    )
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='Opal {0}'.format(opal.__version__)
    )
    subparsers = parser.add_subparsers(help="Opal Commands")

    parser_project = subparsers.add_parser(
        'startproject'
    )
    parser_project.add_argument(
        'name', help="name of your project"
    )
    parser_project.set_defaults(func=startproject)

    parser_plugin = subparsers.add_parser('startplugin')
    parser_plugin.add_argument(
        'name', help="name of your plugin"
    )
    parser_plugin.set_defaults(func=startplugin)

    parser_test = subparsers.add_parser("test")
    parser_test.add_argument(
        'what', default='all', choices=['all', 'py', 'js'], nargs='*')
    parser_test.add_argument(
        '-t', '--test', help='Test case or method to run'
    )
    parser_test.add_argument(
        '-c', '--coverage', action='store_true',
        help='Generate a test coverage report'
    )
    parser_test.add_argument(
        '--failfast', action='store_true',
        help="Stop the test run on the first failing test"
    )
    parser_test.set_defaults(func=test)

    parser_checkout = subparsers.add_parser("checkout")
    parser_checkout.set_defaults(func=checkout)

    args = parser.parse_args(args)
    args.func(args)
    sys.exit(0)


def main():
    parse_args(sys.argv[1:])
