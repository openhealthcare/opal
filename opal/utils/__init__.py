"""
Generic OPAL utilities
"""
from collections import namedtuple
import datetime
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

# TODO depreciate this entirely
Tag = namedtuple('Tag', 'name title subtags')

# TODO - make this non-UCLH specific.
# TODO - pick up FT/FK fields from introspection not hardcodings.
def json_to_csv(episodes, description, user):
    """
    Given a list of episodes as JSON, write these to our CSV
    format.
    """
    from opal import models
    target_dir = str(ffs.Path.newdir())
    target = target_dir + '/extract.zip'

    episode_csv = [['id', 'date of admission', 'discharge date',
                   'hospital number', 'date of birth',
                   'country of birth', 'ethnicity', 'category',
                   'tags', 'hospital', 'ward', 'bed']]
    diagnosis_csv = [['episode_id', 'condition', 'condition_freetext', 'provisional',
                      'details', 'date_of_diagnosis']]
    pmh_csv = [['episode_id', 'condition', 'condition_freetext', 'year', 'details']]
    antimicrobials_csv = [['episode_id', 'drug', 'drug_freetext', 'dose', 'route',
                           'start_date', 'end_date']]
    allergies_csv = [['episode_id', 'drug', 'provisional',
                      'details']]
    travel_csv = [['episode_id', 'destination', 'destination_freetext', 'dates',
                   'reason_for_travel', 'reason_for_travel_freetext', 'specific_exposures']]
    clinical_advice_csv = [['episode_id', 'date', 'initials', 'reason_for_interaction',
                            'clinical_discussion', 'agreed_plan',
                            'discussed_with', 'clinical_advice_given',
                            'infection_control_advice_given',
                            'change_in_antibiotic_prescription',
                            'referred_to_opat']]
    investigations_csv = [[
            'episode_id',
            'test',
            'date_ordered',
            'details',
            'microscopy',
            'organism',
            'sensitive_antibiotics',
            'resistant_antibiotics',
            'result',
            'igm',
            'igg',
            'vca_igm',
            'vca_igg',
            'ebna_igg',
            'hbsag',
            'anti_hbs',
            'anti_hbcore_igm',
            'anti_hbcore_igg',
            'rpr',
            'tppa',
            'viral_load',
            'parasitaemia',
            'hsv',
            'vzv',
            'syphilis',
            'c_difficile_antigen',
            'c_difficile_toxin',
            'species',
            'hsv_1',
            'hsv_2',
            'enterovirus',
            'cmv',
            'ebv',
            'influenza_a',
            'influenza_b',
            'parainfluenza',
            'metapneumovirus',
            'rsv',
            'adenovirus',
            'norovirus',
            'rotavirus',
            'giardia',
            'entamoeba_histolytica',
            'cryptosporidium'
            ]]

    for episode in episodes:
        e = episode.to_dict(user)
        try:
            historic = models.Tagging.historic_tags_for_episodes([e['id']])[e['id']].keys()
            current = e['location'][0]['tags'].keys()
            current = set(current + historic)
            tags = ";".join(current)

            episode_csv.append([
                    unicode(e['id']),
                    unicode(e['date_of_admission']),
                    unicode(e['discharge_date']),
                    unicode(e['demographics'][0]['hospital_number']),
                    unicode(e['demographics'][0]['date_of_birth']),
                    unicode(e['demographics'][0]['country_of_birth']),
                    unicode(e['demographics'][0]['ethnicity']),
                    unicode(e['location'][0]['category']),
                    tags,
                    unicode(e['location'][0]['hospital']),
                    unicode(e['location'][0]['ward']),
                    unicode(e['location'][0]['bed']),
                    ])
            for diagnosis in e['diagnosis']:
                coded = ''
                if diagnosis['condition_fk_id']:
                    coded = diagnosis['condition']

                diagnosis_csv.append([
                        unicode(e['id']),
                        coded,
                        unicode(diagnosis['condition_ft']),
                        unicode(diagnosis['provisional']),
                        unicode(diagnosis['details']),
                        unicode(diagnosis['date_of_diagnosis'])
                        ])
            for pmh in e['past_medical_history']:
                coded = ''
                if pmh['condition_fk_id']:
                    coded = pmh['condition']
                pmh_csv.append([
                        unicode(e['id']),
                        coded,
                        unicode(pmh['condition_ft']),
                        unicode(pmh['year']),
                        unicode(pmh['details'])
                        ])
            for antimicrobial in e['antimicrobial']:
                coded = ''
                if antimicrobial['drug_fk_id']:
                    coded = antimicrobial['drug']

                antimicrobials_csv.append([
                        unicode(e['id']),
                        coded,
                        unicode(antimicrobial['drug_ft']),
                        unicode(antimicrobial['dose']),
                        unicode(antimicrobial['route']),
                        unicode(antimicrobial['start_date']),
                        unicode(antimicrobial['end_date'])
                        ])
            for allergy in e['allergies']:
                allergies_csv.append([
                        unicode(e['id']),
                        unicode(allergy['drug']),
                        unicode(allergy['provisional']),
                        unicode(allergy['details'])
                        ])
            for travel in e['travel']:
                coded_dest, coded_reason = '', ''
                if travel['destination_fk_id']:
                    coded_dest = travel['destination']
                if travel['reason_for_travel_fk_id']:
                    coded_reason = travel['reason_for_travel']

                travel_csv.append([
                        unicode(e['id']),
                        coded_dest,
                        unicode(travel['destination_ft']),
                        unicode(travel['dates']),
                        coded_reason,
                        unicode(travel['reason_for_travel_ft']),
                        unicode(travel['specific_exposures'])
                        ])

            for advice in e['microbiology_input']:
                clinical_advice_csv.append([
                        unicode(e['id']),
                        unicode(advice['date']),
                        unicode(advice['initials']),
                        unicode(advice['reason_for_interaction']),
                        unicode(advice['clinical_discussion']),
                        unicode(advice['agreed_plan']),
                        unicode(advice['discussed_with']),
                        unicode(advice['clinical_advice_given']),
                        unicode(advice['infection_control_advice_given']),
                        unicode(advice['change_in_antibiotic_prescription']),
                        unicode(advice['referred_to_opat']),
                        ])
            for test in e['microbiology_test']:

                investigations_csv.append([
                        unicode(e['id']),
                        unicode(test['test']),
                        unicode(test['date_ordered']),
                        unicode(test['details']),
                        unicode(test['microscopy']),
                        unicode(test['organism']),
                        unicode(test['sensitive_antibiotics']),
                        unicode(test['resistant_antibiotics']),
                        unicode(test['result']),
                        unicode(test['igm']),
                        unicode(test['igg']),
                        unicode(test['vca_igm']),
                        unicode(test['vca_igg']),
                        unicode(test['ebna_igg']),
                        unicode(test['hbsag']),
                        unicode(test['anti_hbs']),
                        unicode(test['anti_hbcore_igm']),
                        unicode(test['anti_hbcore_igg']),
                        unicode(test['rpr']),
                        unicode(test['tppa']),
                        unicode(test['viral_load']),
                        unicode(test['parasitaemia']),
                        unicode(test['hsv']),
                        unicode(test['vzv']),
                        unicode(test['syphilis']),
                        unicode(test['c_difficile_antigen']),
                        unicode(test['c_difficile_toxin']),
                        unicode(test['species']),
                        unicode(test['hsv_1']),
                        unicode(test['hsv_2']),
                        unicode(test['enterovirus']),
                        unicode(test['cmv']),
                        unicode(test['ebv']),
                        unicode(test['influenza_a']),
                        unicode(test['influenza_b']),
                        unicode(test['parainfluenza']),
                        unicode(test['metapneumovirus']),
                        unicode(test['rsv']),
                        unicode(test['adenovirus']),
                        unicode(test['norovirus']),
                        unicode(test['rotavirus']),
                        unicode(test['giardia']),
                        unicode(test['entamoeba_histolytica']),
                        unicode(test['cryptosporidium'])
                        ])
        except UnicodeDecodeError:
            continue

    episode_csv = "\n".join([",".join(['"'+x+'"' for x in r]) for r in episode_csv])
    diagnosis_csv = "\n".join([",".join(['"'+x+'"' for x in r]) for r in diagnosis_csv])
    pmh_csv = "\n".join([",".join(['"'+x+'"' for x in r]) for r in pmh_csv])
    antimicrobials_csv = "\n".join([",".join(['"'+x+'"' for x in r]) for r in antimicrobials_csv])
    allergies_csv = "\n".join([",".join(['"'+x+'"' for x in r]) for r in allergies_csv])
    travel_csv = "\n".join([",".join(['"'+x+'"' for x in r]) for r in travel_csv])
    clinical_advice_csv = "\n".join([",".join(['"'+x+'"' for x in r]) for r in clinical_advice_csv])
    investigations_csv = "\n".join([",".join(['"'+x+'"' for x in r]) for r in investigations_csv])

    with ffs.Path.temp() as tempdir:
        zipfolder = '{0}.{1}/'.format(user.username, datetime.date.today())
        with tempdir:
            zipfile = archive.ZipPath('episodes.zip')
            zipfile/(zipfolder+'episodes.csv') << episode_csv.encode('UTF-8')
            zipfile/(zipfolder+'diagnosis.csv') << diagnosis_csv.encode('UTF-8')
            zipfile/(zipfolder+'past_medical_history.csv') << pmh_csv.encode('UTF-8')
            zipfile/(zipfolder+'antimicrobials.csv') << antimicrobials_csv.encode('UTF-8')
            zipfile/(zipfolder+'allergies.csv') << allergies_csv.encode('UTF-8')
            zipfile/(zipfolder+'travel.csv') << travel_csv.encode('UTF-8')
            zipfile/(zipfolder+'clinical_advice.csv') << clinical_advice_csv.encode('UTF-8')
            zipfile/(zipfolder+'investigations.csv') << investigations_csv.encode('UTF-8')
            zipfile/(zipfolder+'filter.txt') << description.encode('UTF-8')
            ffs.mv(zipfile, target)
    return target
