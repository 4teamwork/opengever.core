from zope import schema
from zope.interface import Interface


class IPrivateContainer(Interface):
    """Marker interface for private containers, only accessible
    by the corresponding user.
    """


class IPrivateFolderQuotaSettings(Interface):
    """Global private folder quota registry settings.
    """

    size_soft_limit = schema.Int(
        title=u'Size soft limit',
        description=u'Limit in bytes, where 0 is unlimited.',
        default=0)

    size_hard_limit = schema.Int(
        title=u'Size hard limit',
        description=u'Limit in bytes, where 0 is unlimited.',
        default=0)
