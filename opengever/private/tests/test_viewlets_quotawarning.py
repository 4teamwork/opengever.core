from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.core.testing import OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER
from opengever.private.interfaces import IPrivateFolderQuotaSettings
from opengever.private.tests import create_members_folder
from opengever.testing import FunctionalTestCase
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import transaction


class TestQuotaWarningViewlet(FunctionalTestCase):
    layer = OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER

    @browsing
    def test_warning_visible_when_quota_exceeded(self, browser):
        user_folder = create_members_folder(create(Builder('private_root')))
        settings = getUtility(IRegistry).forInterface(
            IPrivateFolderQuotaSettings)
        create(Builder('document').attach_file_containing('X' * 100)
               .within(user_folder))

        browser.login().open(user_folder)
        statusmessages.assert_no_messages()

        settings.size_soft_limit = 70
        transaction.commit()
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
        transaction.commit()
        browser.reload()
        statusmessages.assert_no_messages()
