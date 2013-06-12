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

        # Adding model 'Demographics'
        db.create_table(u'patients_demographics', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['patients.Patient'], unique=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('hospital_number', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('date_of_birth', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'patients', ['Demographics'])

        # Adding model 'Location'
        db.create_table(u'patients_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['patients.Patient'], unique=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('hospital', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('ward', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('bed', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('date_of_admission', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'patients', ['Location'])

        # Adding model 'Diagnosis'
        db.create_table(u'patients_diagnosis', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['patients.Patient'])),
            ('provisional', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('details', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('condition_fk', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['options.Condition'], null=True, blank=True)),
            ('condition_ft', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'patients', ['Diagnosis'])

        # Adding model 'PastMedicalHistory'
        db.create_table(u'patients_pastmedicalhistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['patients.Patient'])),
            ('year', self.gf('django.db.models.fields.CharField')(max_length=4, blank=True)),
            ('condition_fk', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['options.Condition'], null=True, blank=True)),
            ('condition_ft', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'patients', ['PastMedicalHistory'])

        # Adding model 'GeneralNote'
        db.create_table(u'patients_generalnote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['patients.Patient'])),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'patients', ['GeneralNote'])

        # Adding model 'Destination'
        db.create_table(u'patients_destination', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['patients.Patient'])),
            ('dates', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('specific_exposures', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('destination_fk', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['options.Destination'], null=True, blank=True)),
            ('destination_ft', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('reason_for_travel_fk', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['options.Travel_reason'], null=True, blank=True)),
            ('reason_for_travel_ft', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'patients', ['Destination'])

        # Adding model 'Antimicrobial'
        db.create_table(u'patients_antimicrobial', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['patients.Patient'])),
            ('dose', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('route_fk', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['options.Antimicrobial_route'], null=True, blank=True)),
            ('route_ft', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('drug_fk', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['options.Antimicrobial'], null=True, blank=True)),
            ('drug_ft', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'patients', ['Antimicrobial'])

        # Adding model 'MicrobiologyInput'
        db.create_table(u'patients_microbiologyinput', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['patients.Patient'])),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('initials', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('clinical_discussion', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('agreed_plan', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('discussed_with', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('clinical_advice_given', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('giving_result', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('infection_control_advice_given', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('change_in_antibiotic_prescription', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'patients', ['MicrobiologyInput'])

        # Adding model 'Plan'
        db.create_table(u'patients_plan', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['patients.Patient'], unique=True)),
            ('plan', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'patients', ['Plan'])

        # Adding model 'Discharge'
        db.create_table(u'patients_discharge', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['patients.Patient'], unique=True)),
            ('plan', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'patients', ['Discharge'])


    def backwards(self, orm):
        # Deleting model 'Patient'
        db.delete_table(u'patients_patient')

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

        # Deleting model 'Destination'
        db.delete_table(u'patients_destination')

        # Deleting model 'Antimicrobial'
        db.delete_table(u'patients_antimicrobial')

        # Deleting model 'MicrobiologyInput'
        db.delete_table(u'patients_microbiologyinput')

        # Deleting model 'Plan'
        db.delete_table(u'patients_plan')

        # Deleting model 'Discharge'
        db.delete_table(u'patients_discharge')


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
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patients.Patient']"}),
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
            'patient': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['patients.Patient']", 'unique': 'True'})
        },
        u'patients.destination': {
            'Meta': {'object_name': 'Destination'},
            'dates': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'destination_fk': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['options.Destination']", 'null': 'True', 'blank': 'True'}),
            'destination_ft': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patients.Patient']"}),
            'reason_for_travel_fk': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['options.Travel_reason']", 'null': 'True', 'blank': 'True'}),
            'reason_for_travel_ft': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'specific_exposures': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'patients.diagnosis': {
            'Meta': {'object_name': 'Diagnosis'},
            'condition_fk': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['options.Condition']", 'null': 'True', 'blank': 'True'}),
            'condition_ft': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'details': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patients.Patient']"}),
            'provisional': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'patients.discharge': {
            'Meta': {'object_name': 'Discharge'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['patients.Patient']", 'unique': 'True'}),
            'plan': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'patients.generalnote': {
            'Meta': {'object_name': 'GeneralNote'},
            'comment': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patients.Patient']"})
        },
        u'patients.location': {
            'Meta': {'object_name': 'Location'},
            'bed': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'date_of_admission': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'hospital': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['patients.Patient']", 'unique': 'True'}),
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
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patients.Patient']"})
        },
        u'patients.pastmedicalhistory': {
            'Meta': {'object_name': 'PastMedicalHistory'},
            'condition_fk': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['options.Condition']", 'null': 'True', 'blank': 'True'}),
            'condition_ft': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patients.Patient']"}),
            'year': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'})
        },
        u'patients.patient': {
            'Meta': {'object_name': 'Patient'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'patients.plan': {
            'Meta': {'object_name': 'Plan'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['patients.Patient']", 'unique': 'True'}),
            'plan': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['patients']