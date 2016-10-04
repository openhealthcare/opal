"""
Load a series of lookup lists into our instance.
"""
import os
import ffs
from optparse import make_option

from django.core.management.base import BaseCommand

from opal.core.lookuplists import load_lookuplist
from opal.core import application


LOOKUPLIST_LOCATION = os.path.join(
    "{}", "data", "lookuplists", "lookuplists.json"
)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            "-f",
            "--file",
            dest="filename",
            help="specify import file",
            metavar="FILE"
        ),
    )

    def _from_file(self, plugin):
        filename = LOOKUPLIST_LOCATION.format(plugin.directory())
        if os.path.isfile(filename):
            datafile = ffs.Path(filename)
            return datafile.json_load()
        else:
            return {}

    def handle(self, *args, **options):
        application_and_plugins = application.get_all_components()
        for plugin in application_and_plugins:
            data = self._from_file(plugin)
            msg = "\nFor {}".format(plugin.__name__)
            num, created, synonyms_created = load_lookuplist(data)
            msg += "\nLoaded {0} lookup lists\n".format(num)
            msg += "\n\nNew items report:\n\n\n"
            msg += "{0} new items".format(created)
            msg += " {0} new synonyms".format(synonyms_created)
            self.stdout.write(msg)
