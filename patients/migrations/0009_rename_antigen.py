from south.db import db

class Migration:

    def forwards(self, orm):
        # Rename 'name' field to 'full_name'
        db.rename_column('patients_microbiologytest', 'c_difficile_antigenl',
                         'c_difficile_antigen')

    def backwards(self, orm):
        # Rename 'name' field to 'full_name'
        db.rename_column('patients_microbiologytest', 'c_difficile_antigen',
                         'c_difficile_antigenl')
