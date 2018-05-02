from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.private.interfaces import IPrivateFolderQuotaSettings
from opengever.private.tests import create_members_folder
from opengever.testing import IntegrationTestCase
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import transaction


class TestQuotaWarningViewlet(IntegrationTestCase):

    features = ('private', )

    @browsing
    def test_warning_visible_when_quota_exceeded(self, browser):
        self.login(self.regular_user, browser=browser)

        settings = getUtility(IRegistry).forInterface(IPrivateFolderQuotaSettings)
        create(Builder('document').attach_file_containing('X' * 100)
               .within(self.private_dossier))

        browser.open(self.private_folder)
        statusmessages.assert_no_messages()

        settings.size_soft_limit = 70
        browser.reload()
        statusmessages.assert_message(
            u'The quota of your private folder will exceed soon.')

        settings.size_hard_limit = 80
        transaction.commit()
        browser.reload()
        statusmessages.assert_message(
            u'The quota of your private folder has exceeded,'
            ' you can not add any new files or mails.')

        settings.size_soft_limit = 0
        settings.size_hard_limit = 0
        browser.reload()
        statusmessages.assert_no_messages()
