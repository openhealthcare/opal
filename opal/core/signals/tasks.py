"""
Tasks for our OPAL signals
"""
from celery import shared_task

from opal.models import Patient, Episode
from opal.core.subrecords import get_subrecord_from_api_name


@shared_task
def patient_post_save(created, instance_id):
    from opal.core.signals.worker import patient_post_save
    instance = Patient.objects.get(id=instance_id)
    patient_post_save.send(Patient, created=created, instance=instance)
    return


@shared_task
def episode_post_save(created, instance_id):
    from opal.core.signals.worker import episode_post_save
    instance = Episode.objects.get(id=instance_id)
    episode_post_save.send(Episode, created=created, instance=instance)
    return


@shared_task
def subrecord_post_save(sender_api_name, created, instance_id):
    from opal.core.signals.worker import subrecord_post_save
    sender = get_subrecord_from_api_name(sender_api_name)
    instance = sender.objects.get(id=instance_id)
    subrecord_post_save.send(sender, created=created, instance=instance)
    return
