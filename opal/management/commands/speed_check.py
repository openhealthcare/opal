"""
Create singletons that may have been dropped
"""
import time

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from opal.models import Episode


class Command(BaseCommand):
    def test_run(self, prefetch):
        last_hundred = Episode.objects.count() - 100
        before = time.time()
        Episode.objects.serialised(
            User.objects.first(),
            Episode.objects.filter(id__gte=last_hundred),
            prefetch=prefetch
        )
        return time.time() - before

    def add_arguments(self, parser):
        parser.add_argument(
            '--prefetch',
            action='store_true',
        )

    def handle(self, *args, **options):
        times = []
        for i in xrange(20):
            times.append(self.test_run(options["prefetch"]))

        print "=" * 10
        print "time taken with {} {}".format(
            options["prefetch"],
            sum(times)/100
        )
        print "=" * 10
        return
