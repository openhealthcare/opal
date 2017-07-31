"""
Load a series of lookup lists into our instance.
"""
import os
import ffs
from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import transaction

from opal.core.lookuplists import load_lookuplist
from opal.core import application, lookuplists


LOOKUPLIST_LOCATION = os.path.join(
    "{}", "data", "lookuplists", "lookuplists.json"
)


class Command(BaseCommand):

    def __init__(self, *a, **k):
        self.set_counter()
        return super(Command, self).__init__(*a, **k)

    option_list = BaseCommand.option_list + (
        make_option(
            "-f",
            "--file",
            dest="filename",
            help="specify import file",
            metavar="FILE"
        ),
    )

    def set_counter(self):
        self.num = 0
        self.created = 0
        self.synonyms = 0

    def from_path(self, path):
        if path:
            return path.json_load()
        else:
            return {}

    def from_component(self, component):
        # Start with the initial lookuplists.json
        filename = ffs.Path(LOOKUPLIST_LOCATION.format(component.directory()))
        self.load(self.from_path(filename))
        # then work throught the lookuplists we know about
        for lookuplist in lookuplists.LookupList.__subclasses__():
            path = ffs.Path("{0}/data/lookuplists/{1}.json".format(
                application.get_app().directory(),
                lookuplist.get_api_name()
            ))
            self.load(self.from_path(path))

    def load(self, data):
        num, created, synonyms = load_lookuplist(data)
        self.num += num
        self.created += created
        self.synonyms += synonyms

    def print_status(self, name):
        msg = "\nFor {}".format(name)
        msg += "\nLoaded {0} lookup lists\n".format(self.num)
        msg += "\n\nNew items report:\n\n\n"
        msg += "{0} new items".format(self.created)
        msg += " {0} new synonyms".format(self.synonyms)

        self.stdout.write(msg)

    def handle_explicit_filename(self, **kwargs):
        filename = kwargs['filename']
        contents = self.from_path(ffs.Path(filename).abspath)
        self.set_counter()
        self.load(contents)
        self.print_status(filename)

    @transaction.atomic()
    def handle(self, *args, **options):
        if options.get('filename', None):
            return self.handle_explicit_filename(**options)

        components = application.get_all_components()
        for component in components:

            self.set_counter()

            self.from_component(component)
            self.print_status(component.__name__)
