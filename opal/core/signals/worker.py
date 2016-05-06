"""
Custom OPAL Django signals that are fired in workers
(e.g. outside of the request/response cycle)
"""
from django import dispatch

patient_post_save   = dispatch.Signal(providing_args=["created"])
episode_post_save   = dispatch.Signal(providing_args=["created"])
subrecord_post_save = dispatch.Signal(providing_args=["created"])
tagging_post_save   = dispatch.Signal(providing_args=["created"])
