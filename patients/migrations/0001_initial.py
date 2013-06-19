# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Patient'
        db.create_table(u'patients_patient', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'patients', ['Patient'])

        # Adding model 'Tagging'
        db.create_table(u'patients_tagging', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['patients.Patient'])),
        ))
        db.send_create_signal(u'patients', ['Tagging'])

        # Adding model 'Demographics'
        db.create_table(u'patients_demographics', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('hospital_number', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('date_of_birth', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('patient', self.gf('django.db.models.fields.related.OneToOneField')(related_name='demographics', unique=True, to=orm['patients.Patient'])),
        ))
        db.send_create_signal(u'patients', ['Demographics'])

        # Adding model 'Location'
        db.create_table(u'patients_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('hospital', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('ward', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('bed', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('date_of_admission', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('patient', self.gf('django.db.models.fields.related.OneToOneField')(related_name='location', unique=True, to=orm['patients.Patient'])),
        ))
        db.send_create_signal(u'patients', ['Location'])

        # Adding model 'Diagnosis'
        db.create_table(u'patients_diagnosis', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('provisional', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('details', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(related_name='diagnosis', to=orm['patients.Patient'])),
            ('condition_fk', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['options.Condition'], null=True, blank=True)),
            ('condition_ft', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'patients', ['Diagnosis'])

        # Adding model 'PastMedicalHistory'
        db.create_table(u'patients_pastmedicalhistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('year', self.gf('django.db.models.fields.CharField')(max_length=4, blank=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(related_name='past_medical_history', to=orm['patients.Patient'])),
            ('condition_fk', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['options.Condition'], null=True, blank=True)),
            ('condition_ft', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'patients', ['PastMedicalHistory'])

        # Adding model 'GeneralNote'
        db.create_table(u'patients_generalnote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')()),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(related_name='general_note', to=orm['patients.Patient'])),
        ))
        db.send_create_signal(u'patients', ['GeneralNote'])

        # Adding model 'Travel'
        db.create_table(u'patients_travel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dates', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('specific_exposures', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(related_name='travel', to=orm['patients.Patient'])),
            ('destination_fk', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['options.Destination'], null=True, blank=True)),
            ('destination_ft', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('reason_for_travel_fk', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['options.Travel_reason'], null=True, blank=True)),
            ('reason_for_travel_ft', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'patients', ['Travel'])

        # Adding model 'Antimicrobial'
        db.create_table(u'patients_antimicrobial', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dose', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(related_name='antimicrobial', to=orm['patients.Patient'])),
            ('route_fk', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['options.Antimicrobial_route'], null=True, blank=True)),
            ('route_ft', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('drug_fk', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['options.Antimicrobial'], null=True, blank=True)),
            ('drug_ft', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'patients', ['Antimicrobial'])

        # Adding model 'MicrobiologyInput'
        db.create_table(u'patients_microbiologyinput', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('initials', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('clinical_discussion', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('agreed_plan', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('discussed_with', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('clinical_advice_given', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('giving_result', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('infection_control_advice_given', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('change_in_antibiotic_prescription', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(related_name='microbiology_input', to=orm['patients.Patient'])),
        ))
        db.send_create_signal(u'patients', ['MicrobiologyInput'])

        # Adding model 'Plan'
        db.create_table(u'patients_plan', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('plan', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('patient', self.gf('django.db.models.fields.related.OneToOneField')(related_name='plan', unique=True, to=orm['patients.Patient'])),
        ))
        db.send_create_signal(u'patients', ['Plan'])

        # Adding model 'Discharge'
        db.create_table(u'patients_discharge', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('discharge', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('patient', self.gf('django.db.models.fields.related.OneToOneField')(related_name='discharge', unique=True, to=orm['patients.Patient'])),
        ))
        db.send_create_signal(u'patients', ['Discharge'])

        # Adding model 'MicrobiologyTest'
        db.create_table(u'patients_microbiologytest', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('date_ordered', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('details', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('microscopy', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('organism', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('sensitive_antibiotics', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('resistant_antibiotics', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('igm', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('igg', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('vca_igm', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('vca_igg', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('ebna_igg', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('hbsag', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('anti_hbs', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('anti_hbcore_igm', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('anti_hbcore_igg', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('rpr', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('tppa', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('viral_load', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('parasitaemia', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('hsv', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('vzv', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('syphilis', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('c_difficile_antigenl', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('c_difficile_toxin', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('species', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('hsv_1', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('hsv_2', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('enterovirus', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('cmv', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('ebv', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('influenza_a', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('influenza_b', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('parainfluenza', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('metapneumovirus', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('rsv', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('adenovirus', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('norovirus', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('rotavirus', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('giardia', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('entamoeba_histolytica', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('cryptosporidium', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(related_name='microbiology_test', to=orm['patients.Patient'])),
        ))
        db.send_create_signal(u'patients', ['MicrobiologyTest'])


    def backwards(self, orm):
        # Deleting model 'Patient'
        db.delete_table(u'patients_patient')

        # Deleting model 'Tagging'
        db.delete_table(u'patients_tagging')

        # Deleting model 'Demographics'
        db.delete_table(u'patients_demographics')

        # Deleting model 'Location'
        db.delete_table(u'patients_location')

        # Deleting model 'Diagnosis'
        db.delete_table(u'patients_diagnosis')

        # Deleting model 'PastMedicalHistory'
        db.delete_table(u'patients_pastmedicalhistory')

        # Deleting model 'GeneralNote'
        db.delete_table(u'patients_generalnote')

        # Deleting model 'Travel'
        db.delete_table(u'patients_travel')

        # Deleting model 'Antimicrobial'
        db.delete_table(u'patients_antimicrobial')

        # Deleting model 'MicrobiologyInput'
        db.delete_table(u'patients_microbiologyinput')

        # Deleting model 'Plan'
        db.delete_table(u'patients_plan')

        # Deleting model 'Discharge'
        db.delete_table(u'patients_discharge')

        # Deleting model 'MicrobiologyTest'
        db.delete_table(u'patients_microbiologytest')


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
        },
        u'patients.antimicrobial': {
            'Meta': {'object_name': 'Antimicrobial'},
            'dose': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'drug_fk': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['options.Antimicrobial']", 'null': 'True', 'blank': 'True'}),
            'drug_ft': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'antimicrobial'", 'to': u"orm['patients.Patient']"}),
            'route_fk': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['options.Antimicrobial_route']", 'null': 'True', 'blank': 'True'}),
            'route_ft': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        u'patients.demographics': {
            'Meta': {'object_name': 'Demographics'},
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'hospital_number': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'patient': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'demographics'", 'unique': 'True', 'to': u"orm['patients.Patient']"})
        },
        u'patients.diagnosis': {
            'Meta': {'object_name': 'Diagnosis'},
            'condition_fk': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['options.Condition']", 'null': 'True', 'blank': 'True'}),
            'condition_ft': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'details': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'diagnosis'", 'to': u"orm['patients.Patient']"}),
            'provisional': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'patients.discharge': {
            'Meta': {'object_name': 'Discharge'},
            'discharge': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'discharge'", 'unique': 'True', 'to': u"orm['patients.Patient']"})
        },
        u'patients.generalnote': {
            'Meta': {'object_name': 'GeneralNote'},
            'comment': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'general_note'", 'to': u"orm['patients.Patient']"})
        },
        u'patients.location': {
            'Meta': {'object_name': 'Location'},
            'bed': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'date_of_admission': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'hospital': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'location'", 'unique': 'True', 'to': u"orm['patients.Patient']"}),
            'ward': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'patients.microbiologyinput': {
            'Meta': {'object_name': 'MicrobiologyInput'},
            'agreed_plan': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'change_in_antibiotic_prescription': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'clinical_advice_given': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'clinical_discussion': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'discussed_with': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'giving_result': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'infection_control_advice_given': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'initials': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'microbiology_input'", 'to': u"orm['patients.Patient']"})
        },
        u'patients.microbiologytest': {
            'Meta': {'object_name': 'MicrobiologyTest'},
            'adenovirus': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'anti_hbcore_igg': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'anti_hbcore_igm': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'anti_hbs': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'c_difficile_antigenl': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'c_difficile_toxin': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'cmv': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'cryptosporidium': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'date_ordered': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'details': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'ebna_igg': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'ebv': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'entamoeba_histolytica': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'enterovirus': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'giardia': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'hbsag': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'hsv': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'hsv_1': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'hsv_2': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'igg': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'igm': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'influenza_a': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'influenza_b': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'metapneumovirus': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'microscopy': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'norovirus': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'organism': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'parainfluenza': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'parasitaemia': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'microbiology_test'", 'to': u"orm['patients.Patient']"}),
            'resistant_antibiotics': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'rotavirus': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'rpr': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'rsv': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'sensitive_antibiotics': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'species': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'syphilis': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'test': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tppa': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'vca_igg': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'vca_igm': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'viral_load': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'vzv': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        u'patients.pastmedicalhistory': {
            'Meta': {'object_name': 'PastMedicalHistory'},
            'condition_fk': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['options.Condition']", 'null': 'True', 'blank': 'True'}),
            'condition_ft': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'past_medical_history'", 'to': u"orm['patients.Patient']"}),
            'year': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'})
        },
        u'patients.patient': {
            'Meta': {'object_name': 'Patient'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'patients.plan': {
            'Meta': {'object_name': 'Plan'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'plan'", 'unique': 'True', 'to': u"orm['patients.Patient']"}),
            'plan': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'patients.tagging': {
            'Meta': {'object_name': 'Tagging'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patients.Patient']"}),
            'tag_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'patients.travel': {
            'Meta': {'object_name': 'Travel'},
            'dates': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'destination_fk': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['options.Destination']", 'null': 'True', 'blank': 'True'}),
            'destination_ft': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'travel'", 'to': u"orm['patients.Patient']"}),
            'reason_for_travel_fk': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['options.Travel_reason']", 'null': 'True', 'blank': 'True'}),
            'reason_for_travel_ft': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'specific_exposures': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        }
    }

    complete_apps = ['patients']