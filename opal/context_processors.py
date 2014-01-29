"""
Context Processors for OPAL
"""
from django.conf import settings as s

def settings(request):
    """
    Put all settings in locals() for our templte context.
    """
    return {x: getattr(s,x) for x in dir(s)}
