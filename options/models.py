from django.db import models
from options import model_names

option_models = {}

for name in model_names:
    class_name = name.capitalize() # TODO handle camelcase properly
    bases = (models.Model,)
    attrs = {
        'name': models.CharField(max_length=255, unique=True),
        'Meta': type('Meta', (object,), {'ordering': ['name']}),
        '__unicode__': lambda self: self.name,
        '__module__': __name__,
    }
    option_models[name] = type(class_name, bases, attrs)
