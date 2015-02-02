# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Micro_test_other'
        db.delete_table(u'opal_micro_test_other')

        # Deleting model 'Micro_test_stool_parasitology_pcr'
        db.delete_table(u'opal_micro_test_stool_parasitology_pcr')

        # Deleting model 'Symptom'
        db.delete_table(u'opal_symptom')

        # Deleting model 'Micro_test_single_test_pos_neg_equiv'
        db.delete_table(u'opal_micro_test_single_test_pos_neg_equiv')

        # Deleting model 'Micro_test_single_igg_test'
        db.delete_table(u'opal_micro_test_single_igg_test')

        # Deleting model 'Micro_test_respiratory_virus_pcr'
        db.delete_table(u'opal_micro_test_respiratory_virus_pcr')

        # Deleting model 'Micro_test_c_difficile'
        db.delete_table(u'opal_micro_test_c_difficile')

        # Deleting model 'Antimicrobial_adverse_event'
        db.delete_table(u'opal_antimicrobial_adverse_event')

        # Deleting model 'Antimicrobial_frequency'
        db.delete_table(u'opal_antimicrobial_frequency')

        # Deleting model 'Micro_test_csf_pcr'
        db.delete_table(u'opal_micro_test_csf_pcr')

        # Deleting model 'Clinical_advice_reason_for_interaction'
        db.delete_table(u'opal_clinical_advice_reason_for_interaction')

        # Deleting model 'Travel_reason'
        db.delete_table(u'opal_travel_reason')

        # Deleting model 'Micro_test_hepititis_b_serology'
        db.delete_table(u'opal_micro_test_hepititis_b_serology')

        # Deleting model 'Micro_test_serology'
        db.delete_table(u'opal_micro_test_serology')

        # Deleting model 'Line_removal_reason'
        db.delete_table(u'opal_line_removal_reason')

        # Deleting model 'Line_complication'
        db.delete_table(u'opal_line_complication')

        # Deleting model 'Micro_test_stool_pcr'
        db.delete_table(u'opal_micro_test_stool_pcr')

        # Deleting model 'Micro_test_parasitaemia'
        db.delete_table(u'opal_micro_test_parasitaemia')

        # Deleting model 'Line_site'
        db.delete_table(u'opal_line_site')

        # Deleting model 'Line_type'
        db.delete_table(u'opal_line_type')

        # Deleting model 'Micro_test_single_test_pos_neg'
        db.delete_table(u'opal_micro_test_single_test_pos_neg')

        # Deleting model 'Micro_test_mcs'
        db.delete_table(u'opal_micro_test_mcs')

        # Deleting model 'Antimicrobial'
        db.delete_table(u'opal_antimicrobial')

        # Deleting model 'Micro_test_hiv'
        db.delete_table(u'opal_micro_test_hiv')

        # Deleting model 'Microbiology_organism'
        db.delete_table(u'opal_microbiology_organism')

        # Deleting model 'Micro_test_syphilis_serology'
        db.delete_table(u'opal_micro_test_syphilis_serology')

        # Deleting model 'Duration'
        db.delete_table(u'opal_duration')

        # Deleting model 'Micro_test_leishmaniasis_pcr'
        db.delete_table(u'opal_micro_test_leishmaniasis_pcr')

        # Deleting model 'Micro_test_ebv_serology'
        db.delete_table(u'opal_micro_test_ebv_serology')

        # Deleting model 'Antimicrobial_route'
        db.delete_table(u'opal_antimicrobial_route')

        # Deleting model 'Micro_test_viral_load'
        db.delete_table(u'opal_micro_test_viral_load')

        # Deleting model 'Micro_test_swab_pcr'
        db.delete_table(u'opal_micro_test_swab_pcr')


    def backwards(self, orm):
        # Adding model 'Micro_test_other'
        db.create_table(u'opal_micro_test_other', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_other'])

        # Adding model 'Micro_test_stool_parasitology_pcr'
        db.create_table(u'opal_micro_test_stool_parasitology_pcr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_stool_parasitology_pcr'])

        # Adding model 'Symptom'
        db.create_table(u'opal_symptom', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Symptom'])

        # Adding model 'Micro_test_single_test_pos_neg_equiv'
        db.create_table(u'opal_micro_test_single_test_pos_neg_equiv', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_single_test_pos_neg_equiv'])

        # Adding model 'Micro_test_single_igg_test'
        db.create_table(u'opal_micro_test_single_igg_test', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_single_igg_test'])

        # Adding model 'Micro_test_respiratory_virus_pcr'
        db.create_table(u'opal_micro_test_respiratory_virus_pcr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_respiratory_virus_pcr'])

        # Adding model 'Micro_test_c_difficile'
        db.create_table(u'opal_micro_test_c_difficile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_c_difficile'])

        # Adding model 'Antimicrobial_adverse_event'
        db.create_table(u'opal_antimicrobial_adverse_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Antimicrobial_adverse_event'])

        # Adding model 'Antimicrobial_frequency'
        db.create_table(u'opal_antimicrobial_frequency', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Antimicrobial_frequency'])

        # Adding model 'Micro_test_csf_pcr'
        db.create_table(u'opal_micro_test_csf_pcr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_csf_pcr'])

        # Adding model 'Clinical_advice_reason_for_interaction'
        db.create_table(u'opal_clinical_advice_reason_for_interaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Clinical_advice_reason_for_interaction'])

        # Adding model 'Travel_reason'
        db.create_table(u'opal_travel_reason', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Travel_reason'])

        # Adding model 'Micro_test_hepititis_b_serology'
        db.create_table(u'opal_micro_test_hepititis_b_serology', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_hepititis_b_serology'])

        # Adding model 'Micro_test_serology'
        db.create_table(u'opal_micro_test_serology', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_serology'])

        # Adding model 'Line_removal_reason'
        db.create_table(u'opal_line_removal_reason', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Line_removal_reason'])

        # Adding model 'Line_complication'
        db.create_table(u'opal_line_complication', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Line_complication'])

        # Adding model 'Micro_test_stool_pcr'
        db.create_table(u'opal_micro_test_stool_pcr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_stool_pcr'])

        # Adding model 'Micro_test_parasitaemia'
        db.create_table(u'opal_micro_test_parasitaemia', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_parasitaemia'])

        # Adding model 'Line_site'
        db.create_table(u'opal_line_site', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Line_site'])

        # Adding model 'Line_type'
        db.create_table(u'opal_line_type', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Line_type'])

        # Adding model 'Micro_test_single_test_pos_neg'
        db.create_table(u'opal_micro_test_single_test_pos_neg', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_single_test_pos_neg'])

        # Adding model 'Micro_test_mcs'
        db.create_table(u'opal_micro_test_mcs', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_mcs'])

        # Adding model 'Antimicrobial'
        db.create_table(u'opal_antimicrobial', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Antimicrobial'])

        # Adding model 'Micro_test_hiv'
        db.create_table(u'opal_micro_test_hiv', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_hiv'])

        # Adding model 'Microbiology_organism'
        db.create_table(u'opal_microbiology_organism', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Microbiology_organism'])

        # Adding model 'Micro_test_syphilis_serology'
        db.create_table(u'opal_micro_test_syphilis_serology', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_syphilis_serology'])

        # Adding model 'Duration'
        db.create_table(u'opal_duration', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Duration'])

        # Adding model 'Micro_test_leishmaniasis_pcr'
        db.create_table(u'opal_micro_test_leishmaniasis_pcr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_leishmaniasis_pcr'])

        # Adding model 'Micro_test_ebv_serology'
        db.create_table(u'opal_micro_test_ebv_serology', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_ebv_serology'])

        # Adding model 'Antimicrobial_route'
        db.create_table(u'opal_antimicrobial_route', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Antimicrobial_route'])

        # Adding model 'Micro_test_viral_load'
        db.create_table(u'opal_micro_test_viral_load', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_viral_load'])

        # Adding model 'Micro_test_swab_pcr'
        db.create_table(u'opal_micro_test_swab_pcr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_swab_pcr'])


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'opal.communitynurse': {
            'Meta': {'object_name': 'CommunityNurse'},
            'address_line1': ('django.db.models.fields.CharField', [], {'max_length': '45', 'null': 'True', 'blank': 'True'}),
            'address_line2': ('django.db.models.fields.CharField', [], {'max_length': '45', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'post_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'tel1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'tel2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        u'opal.condition': {
            'Meta': {'ordering': "['name']", 'object_name': 'Condition'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.contactnumber': {
            'Meta': {'object_name': 'ContactNumber'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'opal.destination': {
            'Meta': {'ordering': "['name']", 'object_name': 'Destination'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.drug': {
            'Meta': {'ordering': "['name']", 'object_name': 'Drug'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.drugfreq': {
            'Meta': {'ordering': "['name']", 'object_name': 'Drugfreq'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.drugroute': {
            'Meta': {'ordering': "['name']", 'object_name': 'Drugroute'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.episode': {
            'Meta': {'object_name': 'Episode'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'consistency_token': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'date_of_admission': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'discharge_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['opal.Patient']"})
        },
        u'opal.ethnicity': {
            'Meta': {'ordering': "['name']", 'object_name': 'Ethnicity'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.filter': {
            'Meta': {'object_name': 'Filter'},
            'criteria': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'opal.gender': {
            'Meta': {'ordering': "['name']", 'object_name': 'Gender'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.gp': {
            'Meta': {'object_name': 'GP'},
            'address_line1': ('django.db.models.fields.CharField', [], {'max_length': '45', 'null': 'True', 'blank': 'True'}),
            'address_line2': ('django.db.models.fields.CharField', [], {'max_length': '45', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'post_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'tel1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'tel2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        u'opal.hospital': {
            'Meta': {'ordering': "['name']", 'object_name': 'Hospital'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.macro': {
            'Meta': {'object_name': 'Macro'},
            'expanded': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'opal.patient': {
            'Meta': {'object_name': 'Patient'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'opal.role': {
            'Meta': {'object_name': 'Role'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'opal.synonym': {
            'Meta': {'unique_together': "(('name', 'content_type'),)", 'object_name': 'Synonym'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'opal.tagging': {
            'Meta': {'object_name': 'Tagging'},
            'episode': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['opal.Episode']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['opal.Team']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'opal.team': {
            'Meta': {'object_name': 'Team'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'direct_add': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['opal.Team']", 'null': 'True', 'blank': 'True'}),
            'restricted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_all': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'useful_numbers': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['opal.ContactNumber']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'opal.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'can_extract': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'force_password_change': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'readonly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'restricted_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'roles': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['opal.Role']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['opal']