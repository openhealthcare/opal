"""
Our Opal defined errors
"""
from __future__ import unicode_literals


class Error(Exception):
    pass


class APIError(Error):
    pass


class ConsistencyError(Error):
    pass


class FTWLarryError(Error):
    pass


class InvalidDiscoverableFeatureError(Error):
    pass


class UnexpectedFieldNameError(Error):
    pass


class InitializationError(Error):
    pass
