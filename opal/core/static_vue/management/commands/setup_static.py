import os
import logging
import shutil
from django.apps import apps
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        front_end_dir = os.path.join(settings.BASE_DIR,"frontend")
        if os.path.exists(front_end_dir):
            logging.warning('Front end directory already exists, not creating')
        else:
            app = apps.get_app_config('static_vue')
            shutil.copytree(os.path.join(app.path, 'frontend'), front_end_dir)


