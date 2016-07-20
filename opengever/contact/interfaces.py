from opengever.base.interfaces import ISQLObjectWrapper
from zope.interface import Interface


class IContactFolder(Interface):
    """Marker interface for ContactFolder objects.
    """


class IContact(ISQLObjectWrapper):
    """Base Markerinterface for contactish object wrappers."""


class IPerson(IContact):
    """Marker interface for person object wrappers."""


class IOrganization(IContact):
    """Marker interface for organization object wrappers."""
