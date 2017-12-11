from opal.core.pathway import Pathway
from django.utils.functional import SimpleLazyObject


class PathwaysContextProcessor(object):
    def __init__(self):
        for i in Pathway.list():
            setattr(self, i.__name__, i)


def pathways(request):
    return {
        "pathways": SimpleLazyObject(PathwaysContextProcessor)
    }
