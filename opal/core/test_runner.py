"""
Command line test runner entrypoints
"""
import errno
import os
import subprocess
import sys

import ffs

from opal.utils import write

TRAVIS = os.environ.get('TRAVIS', False)


def _has_file(where, filename):
    """
    Predicate function to determine whether we have FILENAME
    is to be found in WHERE
    """
    return bool(ffs.Path(where / filename))


def _run_py_tests(args):
    """
    Run our Python test suite
    """
    write("Running Python Unit Tests")
    test_args = None

    # We have a custom test runner - e.g. it's Opal itself or a plugin.
    if _has_file(args.userland_here, 'runtests.py'):
        test_args = ['python', 'runtests.py']

        if args.coverage:
            test_args = ['coverage', 'run', 'runtests.py']

        if args.test:
            test_args.append(args.test)

    # We have a manage.py script - assume that we're in an application
    elif _has_file(args.userland_here, 'manage.py'):
        test_args = ['python', 'manage.py', 'test']

        if args.coverage:
            test_args = ['coverage', 'run', 'manage.py', 'test', ]

        if args.test:
            test_args.append(args.test)

    else:
        write("\n\nCripes!\n")
        write("We can't figure out how to run your tests :(\n")
        write("Are you in the root directory? \n\n")
        sys.exit(1)

    if args.failfast:
        test_args.append('--failfast')

    if test_args:
        try:
            subprocess.check_call(test_args)
        except subprocess.CalledProcessError:
            sys.exit(1)

        if args.coverage:
            try:
                subprocess.check_call(['coverage', 'html'])
            except subprocess.CalledProcessError:
                sys.exit(1)

    return


def _run_js_tests(args):
    """
    Run our Javascript test suite
    """
    write("Running Javascript Unit Tests")
    env = os.environ.copy()

    # used by the karma config file where to find the opal karma defaults
    # python3 breaks on ffs if we don't explicitly cast the location
    # to a string
    env["OPAL_LOCATION"] = str(args.opal_location)

    if TRAVIS:
        karma = './node_modules/karma/bin/karma'
    else:
        karma = 'karma'
        env['DISPLAY'] = ':10'

    sub_args = [
        karma,
        'start',
        'config/karma.conf.js',
        '--single-run',
    ]
    if args.failfast:
        sub_args.append('--failfast')

    try:
        subprocess.check_call(sub_args, env=env)
    except subprocess.CalledProcessError:
        sys.exit(1)
    except OSError as e:
        if e.errno == errno.ENOENT:
            write("\n\nCripes!\n")
            write("We can't find the karma executable\n")
            write("Please consult the Opal documentation about installing the")
            write("Javascript testing tools required to run Javascript tests:")
            write(
                "http://opal.openhealthcare.org.uk/docs/reference/"
                "testing/"
            )
            write("\nAlternatively run just the Python test suite with")
            write("opal test py")
        sys.exit(1)
    return


def run_tests(args):
    """
    Run our test suites
    """
    if args.what == 'all':
        suites = ['py', 'js']
    else:
        suites = args.what
    for suite in suites:
        globals()['_run_{0}_tests'.format(suite)](args)
    return
