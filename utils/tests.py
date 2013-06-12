from django.test import TestCase
from django.db.models import ForeignKey, CharField
from utils import models

class ForeignKeyOrFreeTextTest(TestCase):
    def setUp(self):
        models.Colour.objects.create(name='red')

    def assert_has_field(self, model, field_name, field_type):
        for field in model._meta.fields:
            if field.name == field_name:
                if type(field) == field_type:
                    return
                else:
                    raise AssertionError("Model %s field %s not of type %s" %
                            (model, field_name, field_type))
        raise AssertionError("Model %s has no field %s" %
                (model, field_name))

    def test_fk_field_created(self):
        self.assert_has_field(models.Person, 'favorite_colour_fk', ForeignKey)

    def test_ft_field_created(self):
        self.assert_has_field(models.Person, 'favorite_colour_ft', CharField)

    def test_can_create_with_known_name(self):
        models.Person.objects.create(favorite_colour='red')
        
    def test_can_create_with_unknown_name(self):
        models.Person.objects.create(favorite_colour='green')

    def test_can_create_with_field_not_set(self):
        models.Person.objects.create()

    def test_can_lookup_with_known_name(self):
        person = models.Person.objects.create(favorite_colour='red')
        person = models.Person.objects.get(pk=person.id)
        self.assertEqual('red', person.favorite_colour)

    def test_can_lookup_without_known_name(self):
        person = models.Person.objects.create(favorite_colour='green')
        person = models.Person.objects.get(pk=person.id)
        self.assertEqual('green', person.favorite_colour)

    def test_can_change_from_known_to_unknown_name(self):
        person = models.Person.objects.create(favorite_colour='red')
        person = models.Person.objects.get(pk=person.id)
        person.favorite_colour = 'green'
        person.save()
        person = models.Person.objects.get(pk=person.id)
        self.assertEqual('green', person.favorite_colour)

    def test_can_change_from_unknown_to_known_name(self):
        person = models.Person.objects.create(favorite_colour='green')
        person = models.Person.objects.get(pk=person.id)
        person.favorite_colour = 'red'
        person.save()
        person = models.Person.objects.get(pk=person.id)
        self.assertEqual('red', person.favorite_colour)
