from opengever.testing import IntegrationTestCase


class TestBaseDocument(IntegrationTestCase):

    @property
    def base_document(self):
        return self.document

    def test_is_trashed(self):
        self.login(self.regular_user)
        self.assertFalse(self.base_document.is_trashed)

        self.trash_documents(self.base_document)
        self.assertTrue(self.base_document.is_trashed)


class TestBaseDocumentMails(TestBaseDocument):

    @property
    def base_document(self):
        return self.mail_eml
