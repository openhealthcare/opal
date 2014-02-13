"""
Generic OPAL utilities
"""
from collections import namedtuple
import importlib
import re

import ffs
from ffs.contrib import archive

camelcase_to_underscore = lambda str: re.sub('(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))', '_\\1', str).lower().strip('_')

def stringport(module):
    try:
        return importlib.import_module(module)
    except ImportError, e:
        raise ImportError("Could not import module '%s'\
                   (Is it on sys.path? Does it have syntax errors?):\
                    %s" % (module, e))

Tag = namedtuple('Tag', 'name title subtags')

def json_to_csv(episodes):
    """
    Given a list of episodes as JSON, write these to our CSV
    format.
    """
    from opal import models
    target = str(ffs.Path.newfile())

    episode_csv = [['id', 'date of admission', 'discharge date',
                   'name', 'hospital number', 'date of birth',
                   'country of birth', 'ethnicity', 'category',
                   'tags', 'hospital', 'ward', 'bed']]
    for e in episodes:
        historic = models.Tagging.historic_tags_for_episodes([e['id']])[e['id']].keys()
        current = e['location'][0]['tags'].keys()
        current = set(current + historic)
        tags = ";".join(current)
        episode_csv.append([
                str(e['id']),
                str(e['date_of_admission']),
                str(e['discharge_date']),
                e['demographics'][0]['name'],
                e['demographics'][0]['hospital_number'],
                str(e['demographics'][0]['date_of_birth']),
                e['demographics'][0]['country_of_birth'],
                e['demographics'][0]['ethnicity'],
                e['location'][0]['category'],
                tags,
                e['location'][0]['hospital'],
                e['location'][0]['ward'],
                e['location'][0]['bed'],
                ])
    episode_csv = "\n".join([",".join(r) for r in episode_csv])

    with ffs.Path.temp() as tempdir:
        with tempdir:
            zipfile = archive.ZipPath('episodes.zip')
            zipfile/'episodes.csv' << episode_csv
            ffs.mv(zipfile, target)
    return target
