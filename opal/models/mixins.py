"""
Model mixins for OPAL!
"""
from datetime import datetime
import random

from django.db import models

from opal import exceptions
from opal.utils.fields import ForeignKeyOrFreeText

class TaggedSubrecordMixin(object):

    @classmethod
    def _get_fieldnames_to_serialize(cls):
        fieldnames = super(TaggedSubrecordMixin, cls)._get_fieldnames_to_serialize()
        fieldnames.append('tags')
        return fieldnames

    @classmethod
    def get_field_type_for_tags(cls):
        return 'list'

    def get_tags(self, user):
        return {tag_name: True for tag_name in self.episode.get_tag_names(user)}

    # value is a dictionary mapping tag names to a boolean
    def set_tags(self, value, user):
        tag_names = [k for k, v in value.items() if v]
        self.episode.set_tag_names(tag_names, user)


class UpdatesFromDictMixin(object):

    @classmethod
    def _get_fieldnames_to_serialize(cls):
        fieldnames = [f.attname for f in cls._meta.fields]
        for name, value in vars(cls).items():
            if isinstance(value, ForeignKeyOrFreeText):
                fieldnames.append(name)
#                fieldnames.remove(name + '_ft')
 #               fieldnames.remove(name + '_fk_id')

        return fieldnames

    @classmethod
    def _get_field_type(cls, name):
        try:
            return type(cls._meta.get_field_by_name(name)[0])
        except models.FieldDoesNotExist:
            pass

        if name in ['patient_id', 'episode_id']:
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

        unknown_fields = set(data.keys()) - set(self._get_fieldnames_to_serialize())
        if unknown_fields:
            raise exceptions.APIError(
                'Unexpected fieldname(s): %s' % list(unknown_fields))

        for name, value in data.items():
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
