from opengever.base.interfaces import ISQLObjectWrapper
from zope import schema
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


class IContactSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable contact feature',
        description=u'Temporary feature flag for the improvements on the'
        'contact module (Persons and Organizations)',
        default=False)


class IDuringContactMigration(Interface):
    """Request layer to indicate that contacts are being migrated to KuB.
    It is used to skip creation of journal entries during the migration.
    """
