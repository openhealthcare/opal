"""
Model mixins for OPAL!
"""
from datetime import datetime
import random

from django.db import models

from opal import exceptions
from opal.utils.fields import ForeignKeyOrFreeText


class UpdatesFromDictMixin(object):

    @classmethod
    def _get_fieldnames_to_serialize(cls):
        """
        Return the list of field names we want to serialize.
        """
        fieldnames = [f.attname for f in cls._meta.fields]
        for name, value in vars(cls).items():
            if isinstance(value, ForeignKeyOrFreeText):
                fieldnames.append(name)
        return fieldnames

    @classmethod
    def _get_field_type(cls, name):
        try:
            return type(cls._meta.get_field_by_name(name)[0])
        except models.FieldDoesNotExist:
            pass

        # TODO: Make this dynamic
        if name in ['patient_id', 'episode_id', 'gp_id', 'nurse_id']:
            return models.ForeignKey

        try:
            value = vars(cls)[name]
            if isinstance(value, ForeignKeyOrFreeText):
                return ForeignKeyOrFreeText
        except KeyError:
            pass

        raise Exception('Unexpected fieldname: %s' % name)

    @classmethod
    def get_field_type_for_consistency_token(cls):
        return 'token'

    def set_consistency_token(self):
        self.consistency_token = '%08x' % random.randrange(16**8)

    def update_from_dict(self, data, user):
        if self.consistency_token:
            try:
                consistency_token = data.pop('consistency_token')
            except KeyError:
                raise exceptions.APIError('Missing field (consistency_token)')

            if consistency_token != self.consistency_token:
                raise exceptions.ConsistencyError

        fields = set(self._get_fieldnames_to_serialize())

        unknown_fields = set(data.keys()) - fields
        if unknown_fields:
            raise exceptions.APIError(
                'Unexpected fieldname(s): %s' % list(unknown_fields))

        for name, value in data.items():
            if name.endswith('_fk_id'):
                if name[:-6] in fields:
                    continue
            if name.endswith('_ft'):
                if name[:-3] in fields:
                    continue

            if name == 'consistency_token':
                continue # shouldn't be needed - Javascripts bug?
            setter = getattr(self, 'set_' + name, None)
            if setter is not None:
                setter(value, user)
            else:
                # TODO use form here?
                if value and self._get_field_type(name) == models.fields.DateField:
                    value = datetime.strptime(value, '%Y-%m-%d').date()

                setattr(self, name, value)

        self.set_consistency_token()
        self.save()
