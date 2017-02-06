"""
Custom OPAL Django signals that are fired in workers
(e.g. outside of the request/response cycle)
"""
from django import dispatch
from django.db.models.signals import post_save

from opal import models

patient_post_save   = dispatch.Signal(providing_args=["created", "instance"])
episode_post_save   = dispatch.Signal(providing_args=["created", "instance"])
subrecord_post_save = dispatch.Signal(providing_args=["created", "instance"])


def post_save_worker_forwarder(sender, created=None, instance=None, **kwargs):
    from django.conf import settings
    if 'djcelery' in settings.INSTALLED_APPS:
        from opal.core.signals import tasks
        if sender == models.Patient:
            tasks.patient_post_save.delay(created, instance.id)
        if sender == models.Episode:
            tasks.episode_post_save.delay(created, instance.id)
        if issubclass(sender, models.Subrecord):
            tasks.subrecord_post_save.delay(sender, created, instance.id)
    return


post_save.connect(
    post_save_worker_forwarder,
    dispatch_uid='OPAL.async_signal_connector'
)
