# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserProfile'
        db.create_table(u'opal_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('force_password_change', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'opal', ['UserProfile'])

        # Adding model 'Patient'
        db.create_table(u'opal_patient', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'opal', ['Patient'])

        # Adding model 'Episode'
        db.create_table(u'opal_episode', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['opal.Patient'])),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'opal', ['Episode'])

        # Adding model 'Tagging'
        db.create_table(u'opal_tagging', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('episode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['opal.Episode'], null=True)),
        ))
        db.send_create_signal(u'opal', ['Tagging'])

        # Adding model 'Synonym'
        db.create_table(u'opal_synonym', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'opal', ['Synonym'])

        # Adding unique constraint on 'Synonym', fields ['name', 'content_type']
        db.create_unique(u'opal_synonym', ['name', 'content_type_id'])

        # Adding model 'Antimicrobial'
        db.create_table(u'opal_antimicrobial', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Antimicrobial'])

        # Adding model 'Antimicrobial_route'
        db.create_table(u'opal_antimicrobial_route', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Antimicrobial_route'])

        # Adding model 'Clinical_advice_reason_for_interaction'
        db.create_table(u'opal_clinical_advice_reason_for_interaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Clinical_advice_reason_for_interaction'])

        # Adding model 'Condition'
        db.create_table(u'opal_condition', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Condition'])

        # Adding model 'Destination'
        db.create_table(u'opal_destination', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Destination'])

        # Adding model 'Hospital'
        db.create_table(u'opal_hospital', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Hospital'])

        # Adding model 'Microbiology_organism'
        db.create_table(u'opal_microbiology_organism', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Microbiology_organism'])

        # Adding model 'Travel_reason'
        db.create_table(u'opal_travel_reason', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Travel_reason'])

        # Adding model 'Micro_test_c_difficile'
        db.create_table(u'opal_micro_test_c_difficile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_c_difficile'])

        # Adding model 'Micro_test_csf_pcr'
        db.create_table(u'opal_micro_test_csf_pcr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_csf_pcr'])

        # Adding model 'Micro_test_ebv_serology'
        db.create_table(u'opal_micro_test_ebv_serology', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_ebv_serology'])

        # Adding model 'Micro_test_hepititis_b_serology'
        db.create_table(u'opal_micro_test_hepititis_b_serology', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_hepititis_b_serology'])

        # Adding model 'Micro_test_hiv'
        db.create_table(u'opal_micro_test_hiv', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_hiv'])

        # Adding model 'Micro_test_leishmaniasis_pcr'
        db.create_table(u'opal_micro_test_leishmaniasis_pcr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_leishmaniasis_pcr'])

        # Adding model 'Micro_test_mcs'
        db.create_table(u'opal_micro_test_mcs', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_mcs'])

        # Adding model 'Micro_test_other'
        db.create_table(u'opal_micro_test_other', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_other'])

        # Adding model 'Micro_test_parasitaemia'
        db.create_table(u'opal_micro_test_parasitaemia', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_parasitaemia'])

        # Adding model 'Micro_test_respiratory_virus_pcr'
        db.create_table(u'opal_micro_test_respiratory_virus_pcr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_respiratory_virus_pcr'])

        # Adding model 'Micro_test_serology'
        db.create_table(u'opal_micro_test_serology', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_serology'])

        # Adding model 'Micro_test_single_igg_test'
        db.create_table(u'opal_micro_test_single_igg_test', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_single_igg_test'])

        # Adding model 'Micro_test_single_test_pos_neg'
        db.create_table(u'opal_micro_test_single_test_pos_neg', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_single_test_pos_neg'])

        # Adding model 'Micro_test_single_test_pos_neg_equiv'
        db.create_table(u'opal_micro_test_single_test_pos_neg_equiv', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_single_test_pos_neg_equiv'])

        # Adding model 'Micro_test_stool_parasitology_pcr'
        db.create_table(u'opal_micro_test_stool_parasitology_pcr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_stool_parasitology_pcr'])

        # Adding model 'Micro_test_stool_pcr'
        db.create_table(u'opal_micro_test_stool_pcr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_stool_pcr'])

        # Adding model 'Micro_test_swab_pcr'
        db.create_table(u'opal_micro_test_swab_pcr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_swab_pcr'])

        # Adding model 'Micro_test_syphilis_serology'
        db.create_table(u'opal_micro_test_syphilis_serology', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_syphilis_serology'])

        # Adding model 'Micro_test_viral_load'
        db.create_table(u'opal_micro_test_viral_load', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'opal', ['Micro_test_viral_load'])


    def backwards(self, orm):
        # Removing unique constraint on 'Synonym', fields ['name', 'content_type']
        db.delete_unique(u'opal_synonym', ['name', 'content_type_id'])

        # Deleting model 'UserProfile'
        db.delete_table(u'opal_userprofile')

        # Deleting model 'Patient'
        db.delete_table(u'opal_patient')

        # Deleting model 'Episode'
        db.delete_table(u'opal_episode')

        # Deleting model 'Tagging'
        db.delete_table(u'opal_tagging')

        # Deleting model 'Synonym'
        db.delete_table(u'opal_synonym')

        # Deleting model 'Antimicrobial'
        db.delete_table(u'opal_antimicrobial')

        # Deleting model 'Antimicrobial_route'
        db.delete_table(u'opal_antimicrobial_route')

        # Deleting model 'Clinical_advice_reason_for_interaction'
        db.delete_table(u'opal_clinical_advice_reason_for_interaction')

        # Deleting model 'Condition'
        db.delete_table(u'opal_condition')

        # Deleting model 'Destination'
        db.delete_table(u'opal_destination')

        # Deleting model 'Hospital'
        db.delete_table(u'opal_hospital')

        # Deleting model 'Microbiology_organism'
        db.delete_table(u'opal_microbiology_organism')

        # Deleting model 'Travel_reason'
        db.delete_table(u'opal_travel_reason')

        # Deleting model 'Micro_test_c_difficile'
        db.delete_table(u'opal_micro_test_c_difficile')

        # Deleting model 'Micro_test_csf_pcr'
        db.delete_table(u'opal_micro_test_csf_pcr')

        # Deleting model 'Micro_test_ebv_serology'
        db.delete_table(u'opal_micro_test_ebv_serology')

        # Deleting model 'Micro_test_hepititis_b_serology'
        db.delete_table(u'opal_micro_test_hepititis_b_serology')

        # Deleting model 'Micro_test_hiv'
        db.delete_table(u'opal_micro_test_hiv')

        # Deleting model 'Micro_test_leishmaniasis_pcr'
        db.delete_table(u'opal_micro_test_leishmaniasis_pcr')

        # Deleting model 'Micro_test_mcs'
        db.delete_table(u'opal_micro_test_mcs')

        # Deleting model 'Micro_test_other'
        db.delete_table(u'opal_micro_test_other')

        # Deleting model 'Micro_test_parasitaemia'
        db.delete_table(u'opal_micro_test_parasitaemia')

        # Deleting model 'Micro_test_respiratory_virus_pcr'
        db.delete_table(u'opal_micro_test_respiratory_virus_pcr')

        # Deleting model 'Micro_test_serology'
        db.delete_table(u'opal_micro_test_serology')

        # Deleting model 'Micro_test_single_igg_test'
        db.delete_table(u'opal_micro_test_single_igg_test')

        # Deleting model 'Micro_test_single_test_pos_neg'
        db.delete_table(u'opal_micro_test_single_test_pos_neg')

        # Deleting model 'Micro_test_single_test_pos_neg_equiv'
        db.delete_table(u'opal_micro_test_single_test_pos_neg_equiv')

        # Deleting model 'Micro_test_stool_parasitology_pcr'
        db.delete_table(u'opal_micro_test_stool_parasitology_pcr')

        # Deleting model 'Micro_test_stool_pcr'
        db.delete_table(u'opal_micro_test_stool_pcr')

        # Deleting model 'Micro_test_swab_pcr'
        db.delete_table(u'opal_micro_test_swab_pcr')

        # Deleting model 'Micro_test_syphilis_serology'
        db.delete_table(u'opal_micro_test_syphilis_serology')

        # Deleting model 'Micro_test_viral_load'
        db.delete_table(u'opal_micro_test_viral_load')


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
        u'opal.antimicrobial': {
            'Meta': {'ordering': "['name']", 'object_name': 'Antimicrobial'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.antimicrobial_route': {
            'Meta': {'ordering': "['name']", 'object_name': 'Antimicrobial_route'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.clinical_advice_reason_for_interaction': {
            'Meta': {'ordering': "['name']", 'object_name': 'Clinical_advice_reason_for_interaction'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.condition': {
            'Meta': {'ordering': "['name']", 'object_name': 'Condition'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.destination': {
            'Meta': {'ordering': "['name']", 'object_name': 'Destination'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.episode': {
            'Meta': {'object_name': 'Episode'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['opal.Patient']"})
        },
        u'opal.hospital': {
            'Meta': {'ordering': "['name']", 'object_name': 'Hospital'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.micro_test_c_difficile': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_c_difficile'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.micro_test_csf_pcr': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_csf_pcr'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.micro_test_ebv_serology': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_ebv_serology'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.micro_test_hepititis_b_serology': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_hepititis_b_serology'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.micro_test_hiv': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_hiv'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.micro_test_leishmaniasis_pcr': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_leishmaniasis_pcr'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.micro_test_mcs': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_mcs'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.micro_test_other': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_other'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.micro_test_parasitaemia': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_parasitaemia'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.micro_test_respiratory_virus_pcr': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_respiratory_virus_pcr'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.micro_test_serology': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_serology'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.micro_test_single_igg_test': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_single_igg_test'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.micro_test_single_test_pos_neg': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_single_test_pos_neg'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.micro_test_single_test_pos_neg_equiv': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_single_test_pos_neg_equiv'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.micro_test_stool_parasitology_pcr': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_stool_parasitology_pcr'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.micro_test_stool_pcr': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_stool_pcr'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.micro_test_swab_pcr': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_swab_pcr'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.micro_test_syphilis_serology': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_syphilis_serology'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.micro_test_viral_load': {
            'Meta': {'ordering': "['name']", 'object_name': 'Micro_test_viral_load'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.microbiology_organism': {
            'Meta': {'ordering': "['name']", 'object_name': 'Microbiology_organism'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.patient': {
            'Meta': {'object_name': 'Patient'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
            'episode': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['opal.Episode']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'})
        },
        u'opal.travel_reason': {
            'Meta': {'ordering': "['name']", 'object_name': 'Travel_reason'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'opal.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'force_password_change': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['opal']