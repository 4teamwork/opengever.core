from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import assert_no_error_messages
from opengever.testing import IntegrationTestCase
from plone import api
from plone.uuid.interfaces import IUUID


class TestMoveItemsWithBrowser(IntegrationTestCase):
    
    @browsing
    def test_move_items_to_repository(self, browser):
        self.login(self.secretariat_user, browser)
        
        paths = ['/'.join(self.inbox_document.getPhysicalPath())]

        uid = IUUID(self.inbox_document)

        # copy the document
        browser.open(self.inbox, {'paths:list': paths}, view='copy_items')
        assert_no_error_messages()

        # move the document
        browser.open(self.dossier, {'paths:list': paths}, view='move_items')
        browser.fill({'Destination': self.dossier})
    
        browser.css('#form-buttons-button_submit').first.click()
        assert_no_error_messages()

        inbox_document = api.content.get(UID=uid)
        self.assertEquals(self.dossier, aq_parent(aq_inner(inbox_document)))
