"""
DDD Integration for OPAL
"""
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
import json
import requests

CHANGE_ENDPOINT = settings.DDD_ENDPOINT + 'change/'
OUR_ENDPOINT = settings.DEFAULT_DOMAIN + '/ddd/'

def change(pre, post):
    payload = {
            'pre': json.dumps(pre, cls=DjangoJSONEncoder), 
            'post': json.dumps(post, cls=DjangoJSONEncoder),
            'endpoint': OUR_ENDPOINT
        }
    print payload
    r = requests.post(
        CHANGE_ENDPOINT,
        data=payload
    )
    print 'status', r.status_code
    print 'text', r.text
    return
