"""
Glossolalia Integration for OPAL
"""
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
import json
import requests

INTEGRATING  = settings.INTEGRATING
NAME         = settings.GLOSSOLALIA_NAME
ENDPOINT     = settings.GLOSSOLALIA_URL + 'api/v0.1/accept/'
OUR_ENDPOINT = settings.DEFAULT_DOMAIN + 'ddd/'

def _send_upstream_message(event, payload):
    """
    Send a message upstream
    """
    try:
        payload['endpoint'] = OUR_ENDPOINT
        r = requests.post(
            ENDPOINT,
            data={
                'servicetype': 'OPAL',
                'event'      : event,
                'name':      NAME,
                'data'       : payload
            }
        )
        print 'status', r.status_code
        print 'text', r.text
    except requests.ConnectionError:
        print 'Glossolalia Connection Error :('
        return
    return

def admit(episode):
    """
    We have admitted a patient - pass on the message to whatever
    upstream services are listening
    """
    if not INTEGRATING:
        return
    print 'Sending upstream Admission'
    payload = {
        'episode': json.dumps(episode, cls=DjangoJSONEncoder),
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
    print 'Sending upstream discharge'
    payload = {
        'episode': json.dumps(episode, cls=DjangoJSONEncoder),
    }
    _send_upstream_message('discharge', payload)
    return

def transfer(episode):
    """
    We have transferred a patient - pass on the message to whatever
    upstream services are listening
    """
    if not INTEGRATING:
        return
    raise NotImplementedError('Need to sort out transfers Larry :(')
    return

def change(pre, post):
    """
    We have made a change to an episode - pass on the message
    to whatever upstream services are listening.
    """
    if not INTEGRATING:
        return
    print 'Sending upstream change'
    payload = {
        'pre': json.dumps(pre, cls=DjangoJSONEncoder), 
        'post': json.dumps(post, cls=DjangoJSONEncoder),
        }
    _send_upstream_message('change', payload)
    return
