"""
Opal "magic" modules
"""
import sys
import types


class DynamicSubrecordModule(types.ModuleType):
    def __getattr__(self, attr):
        from opal.core import subrecords
        try:
            return subrecords.get_subrecord_from_model_name(attr)
        except ValueError:
            pass  # No subrecord found - use the default response
        return getattr(types.ModuleType, attr)


class ApplicationSubrecordImporter(object):
    def find_module(self, fullname, path=None):
        if fullname == 'opal.application_subrecords':
            return self
        return None

    def load_module(self, name):
        return DynamicSubrecordModule(name)


sys.meta_path.append(ApplicationSubrecordImporter())
