"""Easily update version numbers across your project.
"""
import argparse
from functools import reduce
import re
import sys
import toml

from . import deltas

__version__ = "0.2"

class ConfigError(ValueError):
    pass

def read_config():
    with open('reversion.toml') as f:
        conf = toml.load(f)

    if 'currentversion' not in conf:
        raise ConfigError("No field named currentversion")

    if not isinstance(conf['currentversion'], str):
        raise ConfigError("currentversion should be a string, not {}".format(
                                            type(conf['currentversion'])))

    places = conf.get('place', [])
    if not places:
        raise ConfigError("Need at least one replacement site ([[place]] section)")

    if not isinstance(places, list):
        raise ConfigError("place must be an array")

    if not isinstance(places[0], dict):
        raise ConfigError("place must be an array of tables")

    for place in places:
        if 'file' not in place:
            raise ConfigError("Missing file= field for place")

        if not isinstance(place['file'], str):
            raise ConfigError("file must be string")

        if ('line-regex' in place) and not isinstance(place['line-regex'], str):
            raise ConfigError("linematch must be string")

    return conf

def check():
    conf = read_config()
    current = conf['currentversion']
    current_pattern = re.compile(r'\b' + re.escape(current) + r'\b')

    problems = []
    for place in conf['place']:
        linematch = place.get('line-regex', 'version')
        line_pattern = re.compile(linematch)
        match_lines = []
        try:
            with open(place['file']) as f:
                for lineno, line in enumerate(f, start=1):
                    if line_pattern.search(line):
                        m = current_pattern.search(line)
                        if m is not None:
                            match_lines.append(lineno)
        except FileNotFoundError:
            problems.append("No such file: " + place['file'])

        if not match_lines:
            problems.append("No match found in {} with pattern {!r}".format(
                place['file'], linematch
            ))
        elif len(match_lines) > 1:
            problems.append("{} matches found in {} with pattern {!r}: lines {}"
                .format(len(match_lines), place['file'], linematch,
                        ', '.join(str(n) for n in match_lines)))

    return problems

class CheckAction(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        try:
            problems = check()
        except ConfigError as e:
            sys.exit(str(e))

        if problems:
            for p in problems:
                print(p)
            sys.exit(1)
        else:
            print('OK')
            sys.exit(0)

class VersionMatchingError(ValueError): pass

def update_version(changes):
    conf = read_config()
    current_pattern = re.compile(r'\b' + re.escape(conf['currentversion']) + r'\b')
    new_version = reduce(deltas.apply, changes, conf['currentversion'])

    reversion_conf_place = {'file': 'reversion.toml', 'linematch': 'currentversion'}
    files_changed = []
    for place in (conf['place'] + [reversion_conf_place]):
        match_lines = []
        line_pattern = re.compile(place.get('line-regex', 'version'))
        file = place['file']
        contents = []
        files_changed.append((file, contents))
        with open(file) as f:
            for lineno, line in enumerate(f, start=1):
                if line_pattern.search(line):
                    line, nsubs = current_pattern.subn(new_version, line)
                    if nsubs > 1:
                        raise VersionMatchingError('Multiple matches in {} at line {}'
                                                   .format(file, lineno))
                    elif nsubs:
                        match_lines.append(lineno)

                contents.append(line)

        if len(match_lines) == 0:
            raise VersionMatchingError('No matches found in {}'
                                       .format(file))
        elif len(match_lines) > 1:
            raise VersionMatchingError('Multiple matches found in {} at lines {}'
                        .format(file, ', '.join(str(n) for n in match_lines)))


    for filename, contents in files_changed:
        with open(filename, 'w') as f:
            f.writelines(contents)

    return len(files_changed)

def main(argv=None):
    ap = argparse.ArgumentParser(prog='reversion')
    ap.add_argument('--version', action='version', version=__version__)
    ap.add_argument('--check', action=CheckAction,
        help="Check version numbers in project files without changing anything")
    ap.add_argument('change', nargs='+')
    options = ap.parse_args(argv)

    try:
        n = update_version(options.change)
    except (ConfigError, deltas.BadDelta, VersionMatchingError) as e:
        print('Error:', e)
    else:
        print('Updated version number in %d files' % n)
