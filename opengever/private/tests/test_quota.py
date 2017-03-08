from opengever.private.interfaces import IPrivateFolderQuotaSettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from ftw.builder import Builder
from ftw.builder import create
from opengever.core.testing import OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER
from opengever.private.tests import create_members_folder
from opengever.quota.interfaces import IQuotaSizeSettings
from opengever.testing import FunctionalTestCase


class TestPrivateFolderQuota(FunctionalTestCase):
    layer = OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER

    def test_configured_quota_settings_are_available_in_qutoa_adapter(self):
        private_folder = create_members_folder(create(Builder('private_root')))
        self.assertEquals(0, IQuotaSizeSettings(private_folder).get_soft_limit())
        self.assertEquals(0, IQuotaSizeSettings(private_folder).get_hard_limit())

        settings = getUtility(IRegistry).forInterface(
            IPrivateFolderQuotaSettings)
        settings.size_soft_limit = 77
        settings.size_hard_limit = 88
        self.assertEquals(77, IQuotaSizeSettings(private_folder).get_soft_limit())
        self.assertEquals(88, IQuotaSizeSettings(private_folder).get_hard_limit())
