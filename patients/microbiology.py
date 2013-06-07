import os
import re

POS_NEG_EQUIV = ['pending', 'positive', 'negative', 'equivocal']
POS_NEG = ['pending', 'positive', 'negative']
HIV_TEST_RESULTS = ['pending', 'antibody positive', 'GP24 positive', 'negative']

micro_tests = [
    {
        'category': 'mcs',
        'test_names': [
            'Broncheoalveolar lavage MC&S',
            'Blood Culture',
            'CSF AFB microscopy & TB culture',
            'CSF MC&S',
            'Fluid MC&S',
            'Lymph Node MC&S',
            'Pleural MC&S',
            'Sputum AFB microscopy & TB culture',
            'Sputum MC&S',
            'Stool MC&S',
            'Stool OCP',
            'Throat Swab MC&S',
            'Tissue AFB microscopy & TB culture',
            'Tissue MC&S',
            'Urine AFB microscopy & TB culture',
            'Urine MC&S',
            'Wound swab MC&S',
        ],
        'fields': [
            {'name': 'Microscopy'},
            {'name': 'Organism'},
            {'name': 'Sensitive antibiotics'},
            {'name': 'Resistant antibiotics'},
        ],
    },
    {
        'category': 'serology',
        'test_names': [
            'CMV Serology',
            'Dengue Serology',
            'Hepatitis A Serology',
            'Hepatitis E Serology',
            'Measles Serology',
            'Rubella Serology',
            'Toxoplasmosis Serology',
            'VZV Serology',
            'Brucella Serology',
        ],
        'fields': [
            {'name': 'IgM', 'choices': POS_NEG_EQUIV},
            {'name': 'IgG', 'choices': POS_NEG_EQUIV},
        ],
    },
    {
        'category': 'ebv_serology',
        'test_names': [
            'EBV Serology',
        ],
        'fields': [
            {'name': 'VCA IgM', 'choices': POS_NEG_EQUIV},
            {'name': 'VCA IgG', 'choices': POS_NEG_EQUIV},
            {'name': 'EBNA IgG', 'choices': POS_NEG_EQUIV},
        ],
    },
    {
        'category': 'hiv',
        'test_names': [
            'HIV',
        ],
        'fields': [
            {'name': 'Result', 'choices': HIV_TEST_RESULTS},
        ],
    },
    {
        'category': 'hepititis_b_serology',
        'test_names': [
            'Hepatitis B Serology'
        ],
        'fields': [
            {'name': 'HBsAg', 'choices': POS_NEG_EQUIV},
            {'name': 'anti-HbS', 'choices': POS_NEG_EQUIV},
            {'name': 'anti-HbCore IgM', 'choices': POS_NEG_EQUIV},
            {'name': 'anti-HbCore IgG', 'choices': POS_NEG_EQUIV},
        ],
    },
    {
        'category': 'syphilis_serology',
        'test_names': [
            'Syphilis Serology'
        ],
        'fields': [
            {'name': 'RPR'},
            {'name': 'TPPA', 'choices': POS_NEG}
        ],
    },
    {
        'category': 'single_test_pos_neg',
        'test_names': [
            'Cryptococcal antigen',
            'Dengue PCR',
            'JC Virus PCR',
            'MRSA PCR',
            'Rickettsia PCR',
            'Scrub Typhus PCR',
            'Borrleia Screening Serology',
            'Brorleia Reference Serology',
            'Viral Haemorrhagic Fever PCR',
        ],
        'fields': [
            {'name': 'Result', 'choices': POS_NEG}
        ],
    },
    {
        'category': 'single_test_pos_neg_equiv',
        'test_names': [
            'Amoebic Serology',
            'Cystercicosis Serology',
            'Fasciola Serology',
            'Filaria Serology',
            'Hydatid Serology',
            'Strongyloides Serology',
            'Toxcocara Serology',
            'Trypanosomiasis brucei Serology',
            'Trypanosomiasis cruzi serology',
        ],
        'fields': [
            {'name': 'Result', 'choices': POS_NEG_EQUIV}
        ],
    },
    {
        'category': 'single_igg_test',
        'test_names': [
            'Hepatitis C Serology',
            'Hepatitis D Serology',
            'HHV-6 Serology',
            'HHV-7 Serology',
            'HTLV Serology',
        ],
        'fields': [
            {'name': 'IgG', 'choices': POS_NEG_EQUIV}
        ],
    },
    {
        'category': 'viral_load',
        'test_names': [
            'CMV Viral Load',
            'EBV Viral Load ',
            'HBV Viral Load',
            'HCV Viral Load',
            'HHV-6 Viral Load',
            'HHV-7 Viral Load',
            'HHV-8 Viral Load',
            'HIV Viral Load',
            'Measles PCR',
            'VZV Viral Load',
        ],
        'fields': [
            {'name': 'Viral load'}
        ],
    },
    {
        'category': 'parasitaemia',
        'test_names': [
            'Babesia Film',
            'Malaria Film',
            'Microfilarial Film',
        ],
        'fields': [
            {'name': 'Parasitaemia'}
        ],
    },
    {
        'category': 'swab_pcr',
        'test_names': [
            'Swab PCR'
        ],
        'fields': [
            {'name': 'HSV', 'choices': POS_NEG},
            {'name': 'VZV', 'choices': POS_NEG},
            {'name': 'Syphilis', 'choices': POS_NEG},
        ],
    },
    {
        'category': 'c_difficile',
        'test_names': [
            'C. difficile'
        ],
        'fields': [
            {'name': 'C. difficile antigen', 'choices': POS_NEG},
            {'name': 'C. difficile toxin', 'choices': POS_NEG},
        ],
    },
    {
        'category': 'leishmaniasis_pcr',
        'test_names': [
            'Leishmaniasis PCR'
        ],
        'fields': [
            {'name': 'Species'},
            {'name': 'Result', 'choices': POS_NEG},
        ],
    },
    {
        'category': 'csf_pcr',
        'test_names': [
            'CSF PCR'
        ],
        'fields': [
            {'name': 'HSV-1', 'choices': POS_NEG},
            {'name': 'HSV-1', 'choices': POS_NEG},
            {'name': 'Enterovirus', 'choices': POS_NEG},
            {'name': 'CMV', 'choices': POS_NEG},
            {'name': 'EBV', 'choices': POS_NEG},
            {'name': 'VZV', 'choices': POS_NEG},
        ],
    },
    {
        'category': 'respiratory_virus_pcr',
        'test_names': [
            'Respiratory Virus PCR'
        ],
        'fields': [
            {'name': 'Influenza-A', 'choices': POS_NEG},
            {'name': 'Influenza-B', 'choices': POS_NEG},
            {'name': 'Parainfluenza', 'choices': POS_NEG},
            {'name': 'Metapneumovirus', 'choices': POS_NEG},
            {'name': 'RSV', 'choices': POS_NEG},
            {'name': 'Adenovirus', 'choices': POS_NEG},
        ],
    },
    {
        'category': 'stool_pcr',
        'test_names': [
            'Stool PCR'
        ],
        'fields': [
            {'name': 'Norovirus', 'choices': POS_NEG},
            {'name': 'Rotavirus', 'choices': POS_NEG},
            {'name': 'Adenovirus', 'choices': POS_NEG},
        ],
    },
    {
        'category': 'stool_parasitology_pcr',
        'test_names': [
            'Stool Parasitology PCR'
        ],
        'fields': [
            {'name': 'Giardia', 'choices': POS_NEG},
            {'name': 'Entamoeba Histolytica', 'choices': POS_NEG},
            {'name': 'Cryptosporidium', 'choices': POS_NEG},
        ],
    },
    {
        'category': 'other',
        'test_names': [
            'Other'
        ],
        'fields': [
            {'name': 'Result'}
        ],
    },
]

form_template = '''
<form class="form-horizontal">
    <div class="control-group">
        <label class="control-label">Test</label>
        <div class="controls">
            <input type="text" ng-model="editing.test" bs-typeahead="microbiology_test_list" data-provide="typeahead">
        </div>
    </div>
{tests}
</form>
'''

test_template = '''
    <span ng-show="{show_conditions}">
{fields}
    </span>
'''

date_template = '''
        <div class="control-group">
            <label class="control-label">Date</label>
            <div class="controls">
                <input type="text" ng-model="editing.date">
            </div>
        </div>
'''

text_input_template = '''
        <div class="control-group">
            <label class="control-label">{title}</label>
            <div class="controls">
                <input type="text" ng-model="editing.{field_name}">
            </div>
        </div>
'''

radio_inputs_template = '''
        <div class="control-group">
            <label class="control-label">{title}</label>
            <div class="controls">
{inputs}
            </div>
        </div>
'''

radio_input_template = '''
                <label class="radio inline">
                    <input type="radio" value="{value}" ng-model="editing.{field_name}">
                    {value}
                </label>
'''

tests_html = ''

def make_slug(s):
    s = s.lower()
    s = s.replace(' ', '_')
    s = s.replace('-', '_')
    s = re.sub('\W', '', s)
    return s

for test in micro_tests:
    fields_html = date_template + text_input_template.format(title='Details', field_name='details')
    for field in test['fields']:
        key = make_slug(field['name'])
        if 'choices' in field:
            inputs = ''
            for option in field['choices']:
                inputs += radio_input_template.format(value=option, field_name=key)
            fields_html += radio_inputs_template.format(inputs=inputs, title=field['name'])
        else:
            fields_html += text_input_template.format(title=field['name'], field_name=key)
    show_conditions = ' || '.join("editing.test == '%s'" % test_name for test_name in test['test_names'])
    tests_html += test_template.format(show_conditions=show_conditions, fields=fields_html)

form_html = form_template.format(tests=tests_html)

with open(os.path.join(os.path.dirname(__file__), '../opal/assets/templates/microbiology-modal.html'), 'w') as f:
    f.write(form_html)

print "Copy the following into the definition of $scope.microbiology_test_list in opal/assets/js/opal.js"

for test in micro_tests:
    for test_name in test['test_names']:
        print "'%s'," % test_name
