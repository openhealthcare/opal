# Generated by Django 2.0.13 on 2019-11-29 11:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0040_delete_contactnumber'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patientrecordaccess',
            name='patient',
        ),
        migrations.RemoveField(
            model_name='patientrecordaccess',
            name='user',
        ),
        migrations.DeleteModel(
            name='PatientRecordAccess',
        ),
    ]