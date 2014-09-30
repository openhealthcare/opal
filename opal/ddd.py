"""
DDD Integration for OPAL
"""
from django.conf import settings
import requests

CHANGE_ENDPOINT = settings.DDD_ENDPOINT + 'change/'
OUR_ENDPOINT = settings.DEFAULT_DOMAIN + '/ddd/'

def change(pre, post):
    r = requests.post(
        CHANGE_ENDPOINT,
        params={'pre': pre, 'post': post, 'endpoint': OUR_ENDPOINT}
    )
    print r.status_code
    print r.text
    return
