# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Micro_test_other'
        db.create_table(u'options_micro_test_other', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'options', ['Micro_test_other'])

        # Adding model 'Micro_test_serology'
        db.create_table(u'options_micro_test_serology', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'options', ['Micro_test_serology'])

        # Adding model 'Micro_test_stool_pcr'
        db.create_table(u'options_micro_test_stool_pcr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'options', ['Micro_test_stool_pcr'])

        # Adding model 'Micro_test_swab_pcr'
        db.create_table(u'options_micro_test_swab_pcr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'options', ['Micro_test_swab_pcr'])

        # Adding model 'Micro_test_mcs'
        db.create_table(u'options_micro_test_mcs', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'options', ['Micro_test_mcs'])

        # Adding model 'Micro_test_ebv_serology'
        db.create_table(u'options_micro_test_ebv_serology', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'options', ['Micro_test_ebv_serology'])

        # Adding model 'Micro_test_leishmaniasis_pcr'
        db.create_table(u'options_micro_test_leishmaniasis_pcr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'options', ['Micro_test_leishmaniasis_pcr'])

        # Adding model 'Micro_test_syphilis_serology'
        db.create_table(u'options_micro_test_syphilis_serology', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'options', ['Micro_test_syphilis_serology'])

        # Adding model 'Micro_test_c_difficile'
        db.create_table(u'options_micro_test_c_difficile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'options', ['Micro_test_c_difficile'])

        # Adding model 'Micro_test_parasitaemia'
        db.create_table(u'options_micro_test_parasitaemia', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'options', ['Micro_test_parasitaemia'])

        # Adding model 'Micro_test_single_test_pos_neg'
        db.create_table(u'options_micro_test_single_test_pos_neg', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'options', ['Micro_test_single_test_pos_neg'])

        # Adding model 'Micro_test_single_test_pos_neg_equiv'
        db.create_table(u'options_micro_test_single_test_pos_neg_equiv', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'options', ['Micro_test_single_test_pos_neg_equiv'])

        # Adding model 'Micro_test_hiv'
        db.create_table(u'options_micro_test_hiv', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'options', ['Micro_test_hiv'])

        # Adding model 'Micro_test_respiratory_virus_pcr'
        db.create_table(u'options_micro_test_respiratory_virus_pcr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'options', ['Micro_test_respiratory_virus_pcr'])

        # Adding model 'Micro_test_csf_pcr'
        db.create_table(u'options_micro_test_csf_pcr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'options', ['Micro_test_csf_pcr'])

        # Adding model 'Micro_test_viral_load'
        db.create_table(u'options_micro_test_viral_load', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'options', ['Micro_test_viral_load'])

        # Adding model 'Micro_test_single_igg_test'
        db.create_table(u'options_micro_test_single_igg_test', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'options', ['Micro_test_single_igg_test'])

        # Adding model 'Micro_test_stool_parasitology_pcr'
        db.create_table(u'options_micro_test_stool_parasitology_pcr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'options', ['Micro_test_stool_parasitology_pcr'])

        # Adding model 'Micro_test_hepititis_b_serology'
        db.create_table(u'options_micro_test_hepititis_b_serology', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'options', ['Micro_test_hepititis_b_serology'])


    def backwards(self, orm):
        # Deleting model 'Micro_test_other'
        db.delete_table(u'options_micro_test_other')

        # Deleting model 'Micro_test_serology'
        db.delete_table(u'options_micro_test_serology')

        # Deleting model 'Micro_test_stool_pcr'
        db.delete_table(u'options_micro_test_stool_pcr')

        # Deleting model 'Micro_test_swab_pcr'
        db.delete_table(u'options_micro_test_swab_pcr')

        # Deleting model 'Micro_test_mcs'
        db.delete_table(u'options_micro_test_mcs')

        # Deleting model 'Micro_test_ebv_serology'
        db.delete_table(u'options_micro_test_ebv_serology')

        # Deleting model 'Micro_test_leishmaniasis_pcr'
        db.delete_table(u'options_micro_test_leishmaniasis_pcr')

        # Deleting model 'Micro_test_syphilis_serology'
        db.delete_table(u'options_micro_test_syphilis_serology')

        # Deleting model 'Micro_test_c_difficile'
        db.delete_table(u'options_micro_test_c_difficile')

        # Deleting model 'Micro_test_parasitaemia'
        db.delete_table(u'options_micro_test_parasitaemia')

        # Deleting model 'Micro_test_single_test_pos_neg'
        db.delete_table(u'options_micro_test_single_test_pos_neg')

        # Deleting model 'Micro_test_single_test_pos_neg_equiv'
        db.delete_table(u'options_micro_test_single_test_pos_neg_equiv')

        # Deleting model 'Micro_test_hiv'
        db.delete_table(u'options_micro_test_hiv')

        # Deleting model 'Micro_test_respiratory_virus_pcr'
        db.delete_table(u'options_micro_test_respiratory_virus_pcr')

        # Deleting model 'Micro_test_csf_pcr'
        db.delete_table(u'options_micro_test_csf_pcr')

        # Deleting model 'Micro_test_viral_load'
        db.delete_table(u'options_micro_test_viral_load')

        # Deleting model 'Micro_test_single_igg_test'
        db.delete_table(u'options_micro_test_single_igg_test')

        # Deleting model 'Micro_test_stool_parasitology_pcr'
        db.delete_table(u'options_micro_test_stool_parasitology_pcr')

        # Deleting model 'Micro_test_hepititis_b_serology'
        db.delete_table(u'options_micro_test_hepititis_b_serology')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'options.antimicrobial': {
            'Meta': {'ordering': "['name']", 'object_name': 'Antimicrobial'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.antimicrobial_route': {
            'Meta': {'ordering': "['name']", 'object_name': 'Antimicrobial_route'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.condition': {
            'Meta': {'ordering': "['name']", 'object_name': 'Condition'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.destination': {
            'Meta': {'ordering': "['name']", 'object_name': 'Destination'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.micro_test_c_difficile': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_c_difficile'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.micro_test_csf_pcr': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_csf_pcr'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.micro_test_ebv_serology': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_ebv_serology'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.micro_test_hepititis_b_serology': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_hepititis_b_serology'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.micro_test_hiv': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_hiv'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.micro_test_leishmaniasis_pcr': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_leishmaniasis_pcr'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.micro_test_mcs': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_mcs'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.micro_test_other': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_other'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.micro_test_parasitaemia': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_parasitaemia'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.micro_test_respiratory_virus_pcr': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_respiratory_virus_pcr'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.micro_test_serology': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_serology'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.micro_test_single_igg_test': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_single_igg_test'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.micro_test_single_test_pos_neg': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_single_test_pos_neg'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.micro_test_single_test_pos_neg_equiv': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_single_test_pos_neg_equiv'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.micro_test_stool_parasitology_pcr': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_stool_parasitology_pcr'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.micro_test_stool_pcr': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_stool_pcr'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.micro_test_swab_pcr': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_swab_pcr'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.micro_test_syphilis_serology': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_syphilis_serology'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.micro_test_viral_load': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_viral_load'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.microbiology_organism': {
            'Meta': {'ordering': "['name']", 'object_name': 'Microbiology_organism'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.patient_category': {
            'Meta': {'ordering': "['name']", 'object_name': 'Patient_category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'options.synonym': {
            'Meta': {'object_name': 'Synonym'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'options.travel_reason': {
            'Meta': {'ordering': "['name']", 'object_name': 'Travel_reason'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['options']