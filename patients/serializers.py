from rest_framework import serializers
from patients import models
from utils.fields import ForeignKeyOrFreeText
from utils import camelcase_to_underscore

def build_subrecord_serializer(model):
    '''Builds a serializer for a Subrecord, handling ForeignKeyOrFreeText correctly.

    eg build_subrecord_serializer(Diagnosis) returns a serialzer that could've been defined:

    class DiagnosisSerializer(serializers.ModelSerializer):
        condition = serializers.WritableField(required=False)
        class Meta:
            model = Diagnosis
            exclude = ['condition']
    '''
    fkft_field_names = [name for name, value in vars(model).items() if isinstance(value, ForeignKeyOrFreeText)]
    field_names_to_exclude = []
    for name in fkft_field_names:
        field_names_to_exclude.extend([name + '_fk', name + '_ft'])
    attrs = {name: serializers.WritableField(required=False) for name in fkft_field_names}
    attrs['Meta'] = type('Meta', (object,), {'model': model, 'exclude': field_names_to_exclude})
    return type(model.__name__ + 'Serializer', (serializers.ModelSerializer,), attrs)

attrs = {'Meta': type('Meta', (object,), {'model': models.Patient})}

for model in models.SingletonSubrecord.__subclasses__():
    attrs[camelcase_to_underscore(model._meta.object_name)] = build_subrecord_serializer(model)(required=False)

for model in models.Subrecord.__subclasses__():
    attrs[camelcase_to_underscore(model._meta.object_name)] = build_subrecord_serializer(model)(many=True, required=False)

PatientSerializer = type('PatientSerializer', (serializers.ModelSerializer,), attrs)

class PatientSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Patient

    demographics = build_subrecord_serializer(models.Demographics)()
