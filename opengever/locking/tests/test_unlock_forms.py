from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.locking.lock import COPIED_TO_WORKSPACE_LOCK
from opengever.meeting.model import SubmittedDocument
from opengever.testing import IntegrationTestCase
from plone.locking.interfaces import ILockable
from zExceptions import NotFound


class TestUnlockSubmittedProposalDocument(IntegrationTestCase):

    features = (
        'meeting',
    )

    @browsing
    def test_unlock_submited_additional_document_will_unlock_but_not_unlink_document(self, browser):
        self.login(self.administrator, browser)

        with self.observe_children(self.submitted_proposal) as children:
            with self.login(self.dossier_responsible):
                self.proposal.submit_additional_document(self.subdocument)

        submitted_document, = children['added']
        lockable = ILockable(submitted_document)

        self.assertTrue(lockable.locked())
        self.assertIsNotNone(SubmittedDocument.query.get_by_target(submitted_document))

        browser.visit(submitted_document, view="@@unlock_submitted_document_form")
        browser.find_button_by_label('Unlock').click()

        statusmessages.assert_message('Document has been unlocked')

        self.assertFalse(lockable.locked(), "Submitted document should be unlocked")
        self.assertIsNotNone(
            SubmittedDocument.query.get_by_target(submitted_document),
            "Submitted document should not be unlinked")

    @browsing
    def test_unlock_not_submitted_document_raises_not_found_error(self, browser):
        self.login(self.administrator, browser)

        browser.exception_bubbling = True
        with self.assertRaises(NotFound):
            browser.visit(self.document, view="@@unlock_submitted_document_form")

    @browsing
    def test_unlock_submitted_document_returns_no_content_if_ajax_load_is_true(self, browser):
        self.login(self.administrator, browser)

        with self.observe_children(self.submitted_proposal) as children:
            with self.login(self.dossier_responsible):
                self.proposal.submit_additional_document(self.subdocument)

        submitted_document, = children['added']
        lockable = ILockable(submitted_document)

        browser.visit(submitted_document, view="@@unlock_submitted_document_form?ajax_load=true&form.buttons.unlock=true")

        self.assertEqual([''], browser.css('body').text_content())
        self.assertFalse(lockable.locked(), "Submitted document should be unlocked")


class TestUnlockDocumentCopiedToWorkspace(IntegrationTestCase):

    @browsing
    def test_unlocking_document_through_unlock_form(self, browser):
        self.login(self.administrator, browser)

        lockable = ILockable(self.document)
        self.assertFalse(lockable.locked())

        lockable.lock(COPIED_TO_WORKSPACE_LOCK)
        self.assertTrue(lockable.locked())

        browser.visit(self.document, view="@@unlock_document_copied_to_workspace_form")
        browser.find_button_by_label('Unlock').click()

        statusmessages.assert_message('Document has been unlocked')
        self.assertFalse(lockable.locked(), "Document should be unlocked")

    @browsing
    def test_unlock_form_redirects_to_document_if_document_is_not_locked(self, browser):
        self.login(self.administrator, browser)

        lockable = ILockable(self.document)
        self.assertFalse(lockable.locked())

        browser.visit(self.document, view="@@unlock_document_copied_to_workspace_form")
        self.assertEqual(self.document.absolute_url(), browser.url)
