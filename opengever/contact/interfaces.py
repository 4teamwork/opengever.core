from opengever.base.interfaces import ISQLObjectWrapper
from zope.interface import Interface


class IContactFolder(Interface):
    """Marker interface for ContactFolder objects.
    """


class IPerson(ISQLObjectWrapper):
    """Marker interface for person object wrappers."""
