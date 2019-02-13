"""
Our Opal defined errors
"""


class Error(Exception):
    pass


class APIError(Error):
    pass


class ConsistencyError(Error):
    pass


class MissingConsistencyTokenError(Error):
    pass


class FTWLarryError(Error):
    pass


class InvalidDiscoverableFeatureError(Error):
    pass


class UnexpectedFieldNameError(Error):
    pass


class InitializationError(Error):
    pass


class MissingTemplateError(Error):
    pass


class UnexpectedEpisodeCategoryNameError(Error):
    pass


class InvalidDataError(Error):
    pass
