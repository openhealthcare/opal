from django.db.models import ForeignKey, CharField

class ForeignKeyOrFreeText(property):
    """Field-like object that stores either foreign key or free text.

    On being added to a class, it creates two fields: a ForeignKey and a
    CharField.

    When assigned a string, looks up foreign model with string value for given
    field.  If found, references foreign model in ForeignKey, otherwise stores
    string in CharField.
    """
    def __init__(self, foreign_model, foreign_field='name'):
        self.foreign_model = foreign_model
        self.foreign_field = foreign_field

    def contribute_to_class(self, cls, name):
        self.name = name
        self.fk_field_name = name + '_fk'
        self.ft_field_name = name + '_ft'
        setattr(cls, name, self)
        fk_field = ForeignKey(self.foreign_model, null=True)
        fk_field.contribute_to_class(cls, self.fk_field_name)
        ft_field = CharField(max_length=255)
        ft_field.contribute_to_class(cls, self.ft_field_name)

    def __set__(self, inst, val):
        lookup = {self.foreign_field: val}
        try:
            foreign_obj = self.foreign_model.objects.get(**lookup)
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
            return getattr(foreign_obj, self.foreign_field)
