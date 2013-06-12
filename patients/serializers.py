from rest_framework import serializers
from patients import models
from utils.fields import ForeignKeyOrFreeText

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Patient

def build_subrecord_serializer(model):
    fkft_field_names = [name for name, value in vars(model).items() if isinstance(value, ForeignKeyOrFreeText)]
    field_names_to_exclude = []
    for name in fkft_field_names:
        field_names_to_exclude.extend([name + '_fk', name + '_ft'])
    attrs = {name: serializers.WritableField(required=False) for name in fkft_field_names}
    attrs['Meta'] = type('Meta', (object,), {'model': model, 'exclude': field_names_to_exclude})
    return type('name', (serializers.ModelSerializer,), attrs)


