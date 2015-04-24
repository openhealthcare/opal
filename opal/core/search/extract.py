"""
Utilities for extracting data from OPAL
"""
import datetime 

import ffs
from ffs.contrib import archive

from opal.core.subrecords import episode_subrecords, patient_subrecords

class ExtractCSV(object):
    
    def __init__(self, contents=None, filename=None):
        self.contents = contents
        self.filename = filename
        

def episode_csv(episodes, user):
    """
    Given an iterable of EPISODES, 
    """
        
def subrecord_csv(episodes, subrecord):
    """
    Given an iterable of EPISODES, the SUBRECORD we want to serialise, and
    the USER for which we want to serialise, return an ExtractCSV for this
    subrecord for these episodes.
    """
    filename = '{0}.csv'.format(subrecord.get_api_name())
    lines = []
    fieldnames = subrecord._get_fieldnames_to_serialize()
    for fname in ['consistency_token', 'id']:
        if fname in fieldnames:
            fieldnames.remove(fname)
    lines.append(','.join(fieldnames))

    subrecords = subrecord.objects.filter(episode__in=episodes)
    for sub in subrecords:
        lines.append(','.join([str(getattr(sub, f)) for f in fieldnames]))
    
    contents = '\n'.join(lines)
    csv = ExtractCSV(filename=filename, contents=contents)
    return csv

def zip_archive(episodes, description, user):
    """
    Given an iterable of EPISODES, the DESCRIPTION of this set of episodes,
    and the USER for which we are extracting, create a zip archive suitable
    for download with all of these episodes as CSVs.
    """
    csvs = []
    for sub in episode_subrecords():
        csvs.append(subrecord_csv(episodes, sub))
        
    # collect CSV file like objects for each subrecord
    # Create a CSV file for the "episode", "patient"
    # Group all of these as a Zipfile

    target_dir = str(ffs.Path.newdir())
    target = target_dir + '/extract.zip'
    
    with ffs.Path.temp() as tempdir:
        zipfolder = '{0}.{1}/'.format(user.username, datetime.date.today())
        with tempdir:
            zipfile = archive.ZipPath('episodes.zip')
            for csv in csvs:
                zipfile/(zipfolder+csv.filename) << csv.contents.encode('UTF-8')
            zipfile/(zipfolder+'filter.txt') << description.encode('UTF-8')
            ffs.mv(zipfile, target)
    return target
    

