from django.db.models import ForeignKey, CharField
from django.contrib.contenttypes.models import ContentType

from options.models import Synonym

class ForeignKeyOrFreeText(property):
    """Field-like object that stores either foreign key or free text.

    On being added to a class, it creates two fields: a ForeignKey and a
    CharField.

    When assigned a string, looks up foreign model with string value for given
    field.  If found, references foreign model in ForeignKey, otherwise stores
    string in CharField.
    """
    def __init__(self, foreign_model):
        self.foreign_model = foreign_model

    def contribute_to_class(self, cls, name):
        self.name = name
        self.fk_field_name = name + '_fk'
        self.ft_field_name = name + '_ft'
        setattr(cls, name, self)
        fk_field = ForeignKey(self.foreign_model, blank=True, null=True)
        fk_field.contribute_to_class(cls, self.fk_field_name)
        ft_field = CharField(max_length=255, blank=True)
        ft_field.contribute_to_class(cls, self.ft_field_name)

    def __set__(self, inst, val):
        # This is totally not the right place to look up synonyms...
        vals = []
        content_type = ContentType.objects.get_for_model(self.foreign_model)
        for val in val.split(','):
            val = val.strip()
            try:
                synonym = Synonym.objects.get(content_type=content_type, name=val)
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
        foreign_obj = getattr(inst, self.fk_field_name)
        if foreign_obj is None:
            return getattr(inst, self.ft_field_name)
        else:
            return foreign_obj.name
