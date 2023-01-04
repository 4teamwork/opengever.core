from zope import schema
from zope.interface import Interface


class IContactFolder(Interface):
    """Marker interface for ContactFolder objects.
    """


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
