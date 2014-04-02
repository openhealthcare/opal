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
    clinical_advice_csv = [['episode_id', 'initials', 'reason_for_interaction',
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
                    str(e['id']),
                    str(e['date_of_admission']),
                    str(e['discharge_date']),
                    str(e['demographics'][0]['hospital_number']),
                    str(e['demographics'][0]['date_of_birth']),
                    str(e['demographics'][0]['country_of_birth']),
                    str(e['demographics'][0]['ethnicity']),
                    str(e['location'][0]['category']),
                    tags,
                    str(e['location'][0]['hospital']),
                    str(e['location'][0]['ward']),
                    str(e['location'][0]['bed']),
                    ])
            for diagnosis in e['diagnosis']:
                coded = ''
                if diagnosis['condition_fk_id']:
                    coded = diagnosis['condition']

                diagnosis_csv.append([
                        str(e['id']),
                        coded,
                        str(diagnosis['condition_ft']),
                        str(diagnosis['provisional']),
                        str(diagnosis['details']),
                        str(diagnosis['date_of_diagnosis'])
                        ])
            for pmh in e['past_medical_history']:
                coded = ''
                if pmh['condition_fk_id']:
                    coded = pmh['condition']
                pmh_csv.append([
                        str(e['id']),
                        coded,
                        str(pmh['condition_ft']),
                        str(pmh['year']),
                        str(pmh['details'])
                        ])
            for antimicrobial in e['antimicrobial']:
                coded = ''
                if antimicrobial['drug_fk_id']:
                    coded = antimicrobial['drug']

                antimicrobials_csv.append([
                        str(e['id']),
                        coded,
                        str(antimicrobial['drug_ft']),
                        str(antimicrobial['dose']),
                        str(antimicrobial['route']),
                        str(antimicrobial['start_date']),
                        str(antimicrobial['end_date'])
                        ])
            for allergy in e['allergies']:
                allergies_csv.append([
                        str(e['id']),
                        str(allergy['drug']),
                        str(allergy['provisional']),
                        str(allergy['details'])
                        ])
            for travel in e['travel']:
                coded_dest, coded_reason = '', ''
                if travel['destination_fk_id']:
                    coded_dest = travel['destination']
                if travel['reason_for_travel_fk_id']:
                    coded_reason = travel['reason_for_travel']

                travel_csv.append([
                        str(e['id']),
                        coded_dest,
                        str(travel['destination_ft']),
                        str(travel['dates']),
                        coded_reason,
                        str(travel['reason_for_travel_ft']),
                        str(travel['specific_exposures'])
                        ])

            for advice in e['microbiology_input']:
                clinical_advice_csv.append([
                        str(e['id']),
                        str(advice['date']),
                        str(advice['initials']),
                        str(advice['reason_for_interaction']),
                        str(advice['clinical_discussion']),
                        str(advice['agreed_plan']),
                        str(advice['discussed_with']),
                        str(advice['clinical_advice_given']),
                        str(advice['infection_control_advice_given']),
                        str(advice['change_in_antibiotic_prescription']),
                        str(advice['referred_to_opat']),
                        ])
            for test in e['microbiology_test']:

                investigations_csv.append([
                        str(e['id']),
                        str(test['test']),
                        str(test['date_ordered']),
                        str(test['details']),
                        str(test['microscopy']),
                        str(test['organism']),
                        str(test['sensitive_antibiotics']),
                        str(test['resistant_antibiotics']),
                        str(test['result']),
                        str(test['igm']),
                        str(test['igg']),
                        str(test['vca_igm']),
                        str(test['vca_igg']),
                        str(test['ebna_igg']),
                        str(test['hbsag']),
                        str(test['anti_hbs']),
                        str(test['anti_hbcore_igm']),
                        str(test['anti_hbcore_igg']),
                        str(test['rpr']),
                        str(test['tppa']),
                        str(test['viral_load']),
                        str(test['parasitaemia']),
                        str(test['hsv']),
                        str(test['vzv']),
                        str(test['syphilis']),
                        str(test['c_difficile_antigen']),
                        str(test['c_difficile_toxin']),
                        str(test['species']),
                        str(test['hsv_1']),
                        str(test['hsv_2']),
                        str(test['enterovirus']),
                        str(test['cmv']),
                        str(test['ebv']),
                        str(test['influenza_a']),
                        str(test['influenza_b']),
                        str(test['parainfluenza']),
                        str(test['metapneumovirus']),
                        str(test['rsv']),
                        str(test['adenovirus']),
                        str(test['norovirus']),
                        str(test['rotavirus']),
                        str(test['giardia']),
                        str(test['entamoeba_histolytica']),
                        str(test['cryptosporidium'])
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
            zipfile/(zipfolder+'episodes.csv') << episode_csv
            zipfile/(zipfolder+'diagnosis.csv') << diagnosis_csv
            zipfile/(zipfolder+'past_medical_history.csv') << pmh_csv
            zipfile/(zipfolder+'antimicrobials.csv') << antimicrobials_csv
            zipfile/(zipfolder+'allergies.csv') << allergies_csv
            zipfile/(zipfolder+'travel.csv') << travel_csv
            zipfile/(zipfolder+'clinical_advice.csv') << clinical_advice_csv.encode('UTF-8')
            zipfile/(zipfolder+'investigations.csv') << investigations_csv
            zipfile/(zipfolder+'filter.txt') << description
            ffs.mv(zipfile, target)
    return target
