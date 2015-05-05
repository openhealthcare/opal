"""
Glossolalia Integration for OPAL
"""
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
import json
import requests

INTEGRATING  = settings.INTEGRATING
NAME         = getattr(settings, 'GLOSSOLALIA_NAME', '')
ENDPOINT     = getattr(settings, 'GLOSSOLALIA_URL', '') + 'api/v0.1/accept/'
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
    return

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
