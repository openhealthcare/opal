from opal.utils import camelcase_to_underscore
from django.db import models
from django.contrib.contenttypes.models import ContentType


def is_numeric(field):
    numeric_fields = (
        models.IntegerField,
        models.DecimalField,
        models.BigIntegerField,
        models.FloatField,
        models.PositiveIntegerField
    )

    return field.__class__ in numeric_fields


class ForeignKeyOrFreeText(property):
    """Field-like object that stores either foreign key or free text.

    On being added to a class, it creates two fields: a ForeignKey and a
    CharField.

    When assigned a string, looks up foreign model with string value for given
    field.  If found, references foreign model in ForeignKey, otherwise stores
    string in CharField.
    """
    def __init__(
        self,
        foreign_model,
        related_name=None,
        verbose_name=None,
        help_text=None,
        default=None
    ):
        self.foreign_model = foreign_model
        self.related_name = related_name
        self._verbose_name = verbose_name
        self.default = default
        self.help_text = help_text

        # for use in the fields, lookup lists essentially have
        #  a max length based on the char field that's used internally
        self.max_length = 255

    @property
    def verbose_name(self):
        if self._verbose_name:
            return self._verbose_name
        else:
            field = camelcase_to_underscore(self.name)
            return field.replace('_', ' ')

    def contribute_to_class(self, cls, name):
        self.name = name
        self.fk_field_name = name + '_fk'
        self.ft_field_name = name + '_ft'
        setattr(cls, name, self)
        fk_kwargs = dict(blank=True, null=True)
        if self.related_name:
            fk_kwargs['related_name'] = self.related_name
        fk_field = models.ForeignKey(self.foreign_model, **fk_kwargs)
        fk_field.contribute_to_class(cls, self.fk_field_name)
        ft_field = models.CharField(
            max_length=255, blank=True, null=True, default=''
        )
        ft_field.contribute_to_class(cls, self.ft_field_name)

    def get_default(self):
        if callable(self.default):
            return self.default()
        else:
            return self.default

    def __set__(self, inst, val):
        if val is None:
            return
        # This is totally not the right place to look up synonyms...
        vals = []
        content_type = ContentType.objects.get_for_model(self.foreign_model)
        for val in val.split(','):
            val = val.strip()
            try:
                from opal.models import Synonym
                synonym = Synonym.objects.get(
                    content_type=content_type, name=val)
                vals.append(synonym.content_object.name)
            except Synonym.DoesNotExist:
                vals.append(val)

        if len(vals) > 1:
            setattr(inst, self.ft_field_name, ', '.join(vals))
            setattr(inst, self.fk_field_name, None)
        else:
            val = vals[0]
            try:
                foreign_obj = self.foreign_model.objects.get(name=val)
                setattr(inst, self.fk_field_name, foreign_obj)
                setattr(inst, self.ft_field_name, '')
            except self.foreign_model.DoesNotExist:
                setattr(inst, self.ft_field_name, val)
                setattr(inst, self.fk_field_name, None)

    def __get__(self, inst, cls):
        if inst is None:
            return self
        try:
            foreign_obj = getattr(inst, self.fk_field_name)
        except:
            return 'Unknown Lookuplist Entry'
#        foreign_obj = getattr(inst, self.fk_field_name)
        if foreign_obj is None:
            return getattr(inst, self.ft_field_name)
        else:
            return foreign_obj.name
