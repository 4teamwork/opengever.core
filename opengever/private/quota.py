from opengever.private.folder import IPrivateFolder
from opengever.private.interfaces import IPrivateFolderQuotaSettings
from opengever.quota.interfaces import IQuotaSizeSettings
from plone.registry.interfaces import IRegistry
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer


@implementer(IQuotaSizeSettings)
@adapter(IPrivateFolder)
class PrivateFolderQuotaSizeSettings(object):
    """Provide persistence for private folder quota settings."""

    def __init__(self, context):
        self.context = context

    def get_soft_limit(self):
        settings = getUtility(IRegistry).forInterface(
            IPrivateFolderQuotaSettings)

        return settings.size_soft_limit

    def get_hard_limit(self):
        settings = getUtility(IRegistry).forInterface(
            IPrivateFolderQuotaSettings)

        return settings.size_hard_limit
