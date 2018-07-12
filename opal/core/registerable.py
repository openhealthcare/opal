"""
opal.core.registerable

Features which allow users to override instances by a namespace
"""
import collections

from opal.core import exceptions, subrecords


REGISTER_REGISTER = collections.defaultdict(dict)


class Registerable(object):
    """
    The core Registerable class.
    """
    default_subrecord_class = None

    @classmethod
    def register(klass, namespace, target):
        """
        Register TARGET as the class to use for NAMESPAE in the context of
        this Registerable.

        If NAMESPACE has already been registered raise DuplicateNameError
        """
        global REGISTER_REGISTER

        if namespace in REGISTER_REGISTER[klass.__name__]:
            msg = "Attempted to register {0} twice in the registerable {1}"
            raise exceptions.DuplicateNameError(
                msg.format(namespace, klass.__name__)
            )

        REGISTER_REGISTER[klass.__name__][namespace] = target

    @classmethod
    def unregister(namespace):
        """
        Unregister NAMESPACE for a Registerable.

        Enables the user to override if they feel they know what they're doing.
        """
        global REGISTER_REGISTER

        if namespace not in REGISTER_REGISTER[klass.__name__]:
            raise ValueError('{0} not registered for {1}'.format(
                namespace, klass.__name__
            ))

        del REGISTER_REGISTER[klass.__name__][namespace]

    @classmethod
    def get_instance_for(klass, namespace):
        """
        Return an instantiated instance of this registerable.

        If there is no registered target, check to see if NAMESPACE is
        a subrecord. If so, return CLASS.DEFAULT_SUBRECORD_CLASS for that
        subrecord. If not, raise InvalidRegisterableNamespaceError
        """
        global REGISTER_REGISTER

        if klass.__name__ in REGISTER_REGISTER:
            if namespace in REGISTER_REGISTER[klass.__name__]:
                return REGISTER_REGISTER[klass.__name__][namespace]()
            else:
                subrecord = subrecords.get_subrecord_from_api_name(namespace)
                if not subrecord:
                    msg = "No valid target for the registerable {0} with "\
                          "namespace {1}".format(klass.__name__, namespace)
                    raise exceptions.InvalidRegisterableNamespaceError(msg)
                else:
                    if self.default_subrecord_class is None:
                        msg = "No registered target found and no default "\
                        "subrecord class for the registerable {0} with "\
                        "namespace {1}".format(klass.__name__, namespace)
                        raise ValueError(msg)
                    return self.default_subrecord_class(namespace=namespace)
