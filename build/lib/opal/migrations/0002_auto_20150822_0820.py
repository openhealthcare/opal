# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='antimicrobial_adverse_event',
            options={'verbose_name': 'Antimicrobial adverse event'},
        ),
        migrations.AlterModelOptions(
            name='antimicrobial_frequency',
            options={'verbose_name': 'Antimicrobial frequency', 'verbose_name_plural': 'Antimicrobial frequencies'},
        ),
        migrations.AlterModelOptions(
            name='antimicrobial_route',
            options={'verbose_name': 'Antimicrobial route'},
        ),
        migrations.AlterModelOptions(
            name='clinical_advice_reason_for_interaction',
            options={'verbose_name': 'Clinical advice reason for interaction', 'verbose_name_plural': 'Clinical advice reasons for interaction'},
        ),
        migrations.AlterModelOptions(
            name='drugfreq',
            options={'verbose_name': 'Drug frequency', 'verbose_name_plural': 'Drug frequencies '},
        ),
        migrations.AlterModelOptions(
            name='drugroute',
            options={'verbose_name': 'Drug route'},
        ),
        migrations.AlterModelOptions(
            name='ethnicity',
            options={'verbose_name_plural': 'Ethnicities'},
        ),
        migrations.AlterModelOptions(
            name='line_complication',
            options={'verbose_name': 'Line complication'},
        ),
        migrations.AlterModelOptions(
            name='line_removal_reason',
            options={'verbose_name': 'Line removal reason'},
        ),
        migrations.AlterModelOptions(
            name='line_site',
            options={'verbose_name': 'Line site'},
        ),
        migrations.AlterModelOptions(
            name='line_type',
            options={'verbose_name': 'Line type'},
        ),
        migrations.AlterModelOptions(
            name='micro_test_c_difficile',
            options={'verbose_name': 'Micro test C difficile', 'verbose_name_plural': 'Micro tests C difficile'},
        ),
        migrations.AlterModelOptions(
            name='micro_test_csf_pcr',
            options={'verbose_name': 'Micro test CSF PCR', 'verbose_name_plural': 'Micro tests CSF PCR'},
        ),
        migrations.AlterModelOptions(
            name='micro_test_ebv_serology',
            options={'verbose_name': 'Micro test EBV serology', 'verbose_name_plural': 'Micro tests EBV serology'},
        ),
        migrations.AlterModelOptions(
            name='micro_test_hepititis_b_serology',
            options={'verbose_name': 'Micro test hepatitis B serology', 'verbose_name_plural': 'Micro tests hepatitis B serology'},
        ),
        migrations.AlterModelOptions(
            name='micro_test_hiv',
            options={'verbose_name': 'Micro test HIV', 'verbose_name_plural': 'Micro tests HIV'},
        ),
        migrations.AlterModelOptions(
            name='micro_test_leishmaniasis_pcr',
            options={'verbose_name': 'Micro test leishmaniasis PCR', 'verbose_name_plural': 'Micro tests leishmaniasis PCR'},
        ),
        migrations.AlterModelOptions(
            name='micro_test_mcs',
            options={'verbose_name': 'Micro test MCS', 'verbose_name_plural': 'Micro tests MCS'},
        ),
        migrations.AlterModelOptions(
            name='micro_test_other',
            options={'verbose_name': 'Micro test other', 'verbose_name_plural': 'Micro tests other'},
        ),
        migrations.AlterModelOptions(
            name='micro_test_parasitaemia',
            options={'verbose_name': 'Micro test parasitaemia', 'verbose_name_plural': 'Micro tests parasitaemia'},
        ),
        migrations.AlterModelOptions(
            name='micro_test_respiratory_virus_pcr',
            options={'verbose_name': 'Micro test respiratory virus PCR', 'verbose_name_plural': 'Micro tests respiratory virus PCR'},
        ),
        migrations.AlterModelOptions(
            name='micro_test_serology',
            options={'verbose_name': 'Micro test serology', 'verbose_name_plural': 'Micro tests serology'},
        ),
        migrations.AlterModelOptions(
            name='micro_test_single_igg_test',
            options={'verbose_name': 'Micro test single IgG test', 'verbose_name_plural': 'Micro tests single IgG test'},
        ),
        migrations.AlterModelOptions(
            name='micro_test_single_test_pos_neg',
            options={'verbose_name': 'Micro test single test pos neg', 'verbose_name_plural': 'Micro tests single test pos neg'},
        ),
        migrations.AlterModelOptions(
            name='micro_test_single_test_pos_neg_equiv',
            options={'verbose_name': 'Micro test single test pos neg equiv', 'verbose_name_plural': 'Micro tests single test pos neg equiv'},
        ),
        migrations.AlterModelOptions(
            name='micro_test_stool_parasitology_pcr',
            options={'verbose_name': 'Micro test stool parasitology PCR', 'verbose_name_plural': 'Micro tests stool parasitology PCR'},
        ),
        migrations.AlterModelOptions(
            name='micro_test_stool_pcr',
            options={'verbose_name': 'Micro test stool PCR', 'verbose_name_plural': 'Micro tests stool PCR'},
        ),
        migrations.AlterModelOptions(
            name='micro_test_swab_pcr',
            options={'verbose_name': 'Micro test swab PCR', 'verbose_name_plural': 'Micro tests swab PCR'},
        ),
        migrations.AlterModelOptions(
            name='micro_test_syphilis_serology',
            options={'verbose_name': 'Micro test syphilis serology', 'verbose_name_plural': 'Micro tests syphilis serology'},
        ),
        migrations.AlterModelOptions(
            name='micro_test_viral_load',
            options={'verbose_name': 'Micro test viral load', 'verbose_name_plural': 'Micro tests viral load'},
        ),
        migrations.AlterModelOptions(
            name='microbiology_organism',
            options={'verbose_name': 'Microbiology organism'},
        ),
        migrations.AlterModelOptions(
            name='travel_reason',
            options={'verbose_name': 'Travel reason'},
        ),
    ]
