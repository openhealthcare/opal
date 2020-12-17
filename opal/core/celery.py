import os
import sys
from opal.core import commandline
from celery import Celery


def set_up():
    if 'runtests.py' not in sys.argv:
        if 'DJANGO_SETTINGS_MODULE' not in os.environ:
            app_name = commandline.find_application_name()
            settings_location = f"{app_name}.settings"
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_location)
    app = Celery('opal')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks()
    return app


app = set_up()


@app.task(bind=True)
def debug_task(self):
    sys.stdout.write('Request: {0!r}\n'.format(self.request))
