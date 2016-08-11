from opal.admin import LookupListForm
from opal.core.test import OpalTestCase
from opal.tests.models import Hat
from opal.models import Synonym
from django.contrib.contenttypes.models import ContentType


class HatForm(LookupListForm):
    class Meta:
        model=Hat
        fields = '__all__'


class LookupListFormTestCase(OpalTestCase):

    def test_invalid_synonym(self):
        hat = Hat.objects.create(name="Cowboy")
        ct = ContentType.objects.get_for_model(Hat)
        Synonym.objects.create(
            content_type=ct,
            object_id=hat.id,
            name="Stetson"
        )

        form = HatForm(dict(name="Stetson"))

        with self.assertRaises(ValueError):
            form.save()

    def test_valid_synonym(self):
        hat = Hat.objects.create(name="Cowboy")
        form = HatForm()
        form.cleaned_data = dict(name="Stetson")
        self.assertEqual("Stetson", form.clean_name())
