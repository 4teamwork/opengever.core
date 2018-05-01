from opengever.private.interfaces import IPrivateFolderQuotaSettings
from opengever.quota.interfaces import IQuotaSizeSettings
from opengever.testing import IntegrationTestCase
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TestPrivateFolderQuota(IntegrationTestCase):

    features = ('private',)

    def test_configured_quota_settings_are_available_in_qutoa_adapter(self):
        self.login(self.regular_user)
        self.assertEquals(0, IQuotaSizeSettings(self.private_folder).get_soft_limit())
        self.assertEquals(0, IQuotaSizeSettings(self.private_folder).get_hard_limit())

        settings = getUtility(IRegistry).forInterface(
            IPrivateFolderQuotaSettings)
        settings.size_soft_limit = 77
        settings.size_hard_limit = 88
        self.assertEquals(77, IQuotaSizeSettings(self.private_folder).get_soft_limit())
        self.assertEquals(88, IQuotaSizeSettings(self.private_folder).get_hard_limit())
