from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER
from opengever.private.interfaces import IPrivateFolderQuotaSettings
from opengever.private.tests import create_members_folder
from opengever.testing import FunctionalTestCase
from plone.namedfile.file import NamedBlobFile
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
import transaction


class TestUsageView(FunctionalTestCase):
    layer = OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER

    @browsing
    def test_size_usage_table(self, browser):
        self.grant('Manager')

        user_folder = create_members_folder(create(Builder('private_root')))
        user_dossier = create(Builder('dossier').within(user_folder))
        document = create(Builder('document')
                          .attach_file_containing('1234')
                          .within(user_dossier))

        browser.login().open(user_folder).find('Usage').click()
        self.assertEquals(
            [['Storage usage', '4.0 Bytes'],
             ['Soft limit', 'unlimited'],
             ['Hard limit', 'unlimited']],
            browser.css('table.usage').first.lists())

        document.file = NamedBlobFile('X' * 30, filename=u'test.txt')
        notify(ObjectModifiedEvent(document))
        settings = getUtility(IRegistry).forInterface(
            IPrivateFolderQuotaSettings)
        settings.size_soft_limit = 40
        settings.size_hard_limit = 50
        transaction.commit()
        browser.reload()
        self.assertEquals(
            [['Storage usage', '30.0 Bytes'],
             ['Soft limit', '40.0 Bytes (75.0%)'],
             ['Hard limit', '50.0 Bytes (60.0%)']],
            browser.css('table.usage').first.lists())

        browser.find('Back').click()
        self.assertEquals(user_folder.absolute_url(), browser.url)
