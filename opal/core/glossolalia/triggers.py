"""
Glossolalia Integration for OPAL
"""
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from opal.core.glossolalia.models import GlossolaliaSubscription
from django.core.urlresolvers import reverse
import requests
import json

INTEGRATING = settings.INTEGRATING
NAME = getattr(settings, 'GLOSSOLALIA_NAME', '')
ENDPOINT = getattr(settings, 'GLOSSOLALIA_URL', '') + 'api/v0.1/accept/'
OUR_ENDPOINT = settings.DEFAULT_DOMAIN


def _send_upstream_message(event, payload):
    """
    Send a message upstream
    """
    try:
        payload['servicetype'] = 'OPAL'
        payload['event'] = event
        payload['name'] = NAME
        r = requests.post(
            ENDPOINT,
            data=payload
        )
    except requests.ConnectionError:
        # print 'Glossolalia Connection Error :('
        return
    return r


def subscribe_to_type(episode, subscription_type):
    demographics = episode.patient.demographics_set.get()
    payload = {
        "hopsital_number": demographics.hospital_number,
        "subscription_type": subscription_type,
        "end_point": reverse('glossolalia-list')
    }
    result = _send_upstream_message("subscribe", payload)
    if result:
        gloss_id = result.json()["id"]
        GlossolaliaSubscription.objects.create(
            patient=episode.patient, gloss_id=gloss_id,
            subscription_type=subscription_type
        )


def subscribe(episode):
    subscribe_to_type(episode, GlossolaliaSubscription.ALL_INFORMATION)


def unsubscribe(episode):
    # we never want to really unsubscribe, we just want core demographics data
    subscribe_to_type(episode, GlossolaliaSubscription.CORE_DEMOGRAPHICS)


def demographics_query(hospital_number):
    pass


def admit(episode):
    """
    We have admitted a patient - pass on the message to whatever
    upstream services are listening
    """
    if not INTEGRATING:
        return
    payload = {
        'data': json.dumps(
            {
                'episode': episode,
                'endpoint': OUR_ENDPOINT
        }, cls=DjangoJSONEncoder)
    }
    _send_upstream_message('admit', payload)
    return

def discharge(episode):
    """
    We have discharged a patient - pass on the message to whatever
    upstream services are listening
    """
    if not INTEGRATING:
        return
    payload = {
        'data': json.dumps({
            'episode': episode,
            'endpoint': OUR_ENDPOINT
        }, cls=DjangoJSONEncoder)
    }
    _send_upstream_message('discharge', payload)
    return

def transfer(pre, post):
    """
    We have transferred a patient - pass on the message to whatever
    upstream services are listening
    """
    if not INTEGRATING:
        return
    payload = {'data':
               json.dumps({
                   'endpoint': OUR_ENDPOINT,
                   'pre': pre,
                   'post': post,
               }, cls=DjangoJSONEncoder)
    }
    _send_upstream_message('transfer', payload)
    return

def change(pre, post):
    """
    We have made a change to an episode - pass on the message
    to whatever upstream services are listening.
    """
    if not INTEGRATING:
        return
    payload = {'data':
               json.dumps({
                   'endpoint': OUR_ENDPOINT,
                   'pre': pre,
                   'post': post,
               }, cls=DjangoJSONEncoder)
    }
    _send_upstream_message('change', payload)
    return
