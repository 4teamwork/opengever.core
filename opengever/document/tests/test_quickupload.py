from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import IntegrationTestCase
from plone.locking.interfaces import IRefreshableLockable
from zExceptions import Unauthorized


class TestDocumentQuickupload(IntegrationTestCase):

    def test_raises_unauthorized_when_document_is_not_checked_out(self):
        self.login(self.regular_user)
        with self.assertRaises(Unauthorized):
            create(Builder('quickuploaded_document')
                   .within(self.document)
                   .with_data('text'))

    def test_raises_unauthorized_when_document_is_locked(self):
        self.login(self.regular_user)
        IRefreshableLockable(self.document).lock()
        with self.assertRaises(Unauthorized):
            create(Builder('quickuploaded_document')
                   .within(self.document)
                   .with_data('text'))

    def test_file_is_updated(self):
        self.login(self.regular_user)
        self.checkout_document(self.document)
        create(Builder('quickuploaded_document')
               .within(self.document)
               .with_data('NEW DATA'))
        self.assertEquals('NEW DATA', self.document.file.data)

    def test_can_update_proposal_document(self):
        self.login(self.regular_user)
        original_filename = self.draftproposaldocument.file.filename
        self.checkout_document(self.draftproposaldocument)
        create(Builder('quickuploaded_document')
               .within(self.draftproposaldocument)
               .with_data('NEW DATA', filename='new.docx'))
        self.assertEqual('NEW DATA', self.draftproposaldocument.file.data)
        self.assertEqual(
            original_filename, self.draftproposaldocument.file.filename)

    def test_empty_file_is_rejected(self):
        self.login(self.regular_user)
        self.checkout_document(self.document)
        original_data = self.document.file.data
        create(Builder('quickuploaded_document')
               .within(self.document)
               .with_data(''))
        self.assertEqual(original_data, self.document.file.data)

    def test_uses_existing_filename_but_new_extension(self):
        self.login(self.regular_user)
        self.checkout_document(self.document)
        create(Builder('quickuploaded_document')
               .within(self.document)
               .with_data('NEW DATA', filename='test.pdf'))
        self.assertEquals('Vertraegsentwurf.pdf', self.document.file.filename)

    def test_non_docx_file_is_rejected_on_proposal_document(self):
        self.login(self.regular_user)
        original_data = self.draftproposaldocument.file.data
        self.checkout_document(self.draftproposaldocument)
        create(Builder('quickuploaded_document')
               .within(self.draftproposaldocument)
               .with_data('NEW DATA', filename='test.pdf'))
        self.assertEqual(original_data, self.draftproposaldocument.file.data)
