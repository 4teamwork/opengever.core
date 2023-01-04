from zope.interface import Interface


class IContactFolder(Interface):
    """Marker interface for ContactFolder objects.
    """


class IDuringContactMigration(Interface):
    """Request layer to indicate that contacts are being migrated to KuB.
    It is used to skip creation of journal entries during the migration.
    """
