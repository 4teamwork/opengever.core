from ftw.testbrowser import browsing
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import IntegrationTestCase
from plone.locking.interfaces import IRefreshableLockable
from zope.component import queryMultiAdapter


class TestDocumentQuickupload(IntegrationTestCase):

    @browsing
    def test_upload_box_is_hidden_when_document_is_not_checked_out(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document)
        self.assertEquals([], browser.css('#uploadbox'),
                          'uploadbox is wrongly displayed')

    @browsing
    def test_upload_box_is_hidden_when_document_is_locked(self, browser):
        self.login(self.regular_user, browser)

        manager = queryMultiAdapter(
            (self.document, self.request), ICheckinCheckoutManager)
        manager.checkout()
        IRefreshableLockable(self.document).lock()

        browser.open(self.document)
        self.assertEquals([], browser.css('#uploadbox'),
                          'uploadbox is wrongly displayed')

    @browsing
    def test_upload_box_is_shown_when_document_is_checked_out_and_not_locked(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document)

        manager = queryMultiAdapter(
            (self.document, self.request), ICheckinCheckoutManager)
        manager.checkout()

        browser.open(self.document)
        self.assertGreater(len(browser.css('#uploadbox')), 0,
                           'Uploadbox is not displayed, but should.')

    @browsing
    def test_upload_box_is_also_shown_in_a_resolved_task(self, browser):
        self.login(self.regular_user, browser)

        self.set_workflow_state('task-state-tested-and-closed', self.task)
        RoleAssignmentManager(self.dossier).add_assignment(
            SharingRoleAssignment('kathi.barfuss',
                                  ['Reader', 'Contributor', 'Editor']))

        manager = queryMultiAdapter(
            (self.taskdocument, self.request), ICheckinCheckoutManager)
        manager.checkout()

        browser.open(self.taskdocument)

        self.assertGreater(len(browser.css('#uploadbox')), 0,
                           'Uploadbox is not displayed, but should.')
