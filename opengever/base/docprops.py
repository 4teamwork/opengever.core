from opengever.base.interfaces import IDocPropertyProvider
from zope.interface import implementer


@implementer(IDocPropertyProvider)
class BaseDocPropertyProvider(object):
    """Baseclass for DocPropertyProvider.

    Contains utility methods to create a dict of doc-properties. Allows
    definition of a prefix that will be inserted in the namespace after the
    application part.
    """

    NS_APP = ('ogg',)
    DEFAULT_PREFIX = tuple()

    def __init__(self, context):
        self.context = context

    def _as_ns_part(self, name_or_iterable):
        if isinstance(name_or_iterable, basestring):
            return (name_or_iterable,)

        return tuple(name_or_iterable)

    def _prefix_properties_with_namespace(self, properties, prefix=None):
        """Prefix all keys in properties with the correct namespace."""

        namespace = self._as_ns_part(self.NS_APP)
        if prefix:
            namespace += self._as_ns_part(prefix)
        namespace += self._as_ns_part(self.DEFAULT_PREFIX)

        return {
            '.'.join(namespace + self._as_ns_part(key)): value
            for key, value in properties.items()
        }

    def _collect_properties(self):
        """Return properties of context as a flat dict."""

        return dict()

    def _merge(self, d1, d2):
        """Merge two dictionaries."""

        merged = d1.copy()
        merged.update(d2)
        return merged

    def get_properties(self, prefix=None):
        properties = self._collect_properties()
        return self._prefix_properties_with_namespace(
            properties, prefix=prefix)
