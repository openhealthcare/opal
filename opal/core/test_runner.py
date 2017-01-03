"""
Command line test runner entrypoints
"""
import os
import subprocess
import sys

import ffs

TRAVIS = os.environ.get('TRAVIS', False)

def _has_file(where, filename):
    """
    Predicate function to determine whether we have FILENAME is to be found in WHERE
    """
    return bool(ffs.Path(where/filename))


def _run_py_tests(args):
    """
    Run our Python test suite
    """
    print("Running Python Unit Tests")

    # We have a custom test runner - e.g. it's OPAL itself or a plugin.
    if _has_file(args.userland_here, 'runtests.py'):
        test_args= ['python', 'runtests.py']
        if args.test:
            test_args.append(args.test)
        if args.coverage:
            test_args = ['coverage', 'run', 'runtests.py']

    # We have a manage.py script - assume that we're in an application
    elif _has_file(args.userland_here, 'manage.py'):
        test_args = ['python', 'manage.py', 'test']

        if args.test:
            test_args.append(args.test)

        if args.coverage:
            test_args = ['coverage', 'run', 'manage.py', 'test',]

    else:
        print("\n\nCripes!\n")
        print("We can't figure out how to run your tests :(\n")
        print("Are you in the root directory? \n\n")
        sys.exit(1)

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
    print("Running Javascript Unit Tests")
    env = os.environ.copy()
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

    try:
        subprocess.check_call(sub_args, env=env)
    except subprocess.CalledProcessError:
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
