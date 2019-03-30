"""
Allowing us to define application medatada that we can
serve to client applications via a JSON API.

We also define some metadata defaults that we don't currently have
better places for.

These should eventually be moved out.
"""
from opal.core import discoverable


class Metadata(discoverable.DiscoverableFeature):
    module_name = 'metadata'


class MacrosMetadata(Metadata):
    slug = 'macros'

    @classmethod
    def to_dict(klass, **kw):
        from opal.models import Macro

        return {
            klass.slug: Macro.to_dict()
        }
