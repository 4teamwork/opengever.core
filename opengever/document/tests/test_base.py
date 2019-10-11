from ftw.builder import Builder
from ftw.builder import create
from opengever.mail.tests import MAIL_DATA
from opengever.testing import IntegrationTestCase


class TestBaseDocument(IntegrationTestCase):

    @property
    def base_document(self):
        return self.document

    @property
    def sub_document(self):
        return self.subdocument

    def test_is_trashed(self):
        self.login(self.regular_user)
        self.assertFalse(self.base_document.is_trashed)

        self.trash_documents(self.base_document)
        self.assertTrue(self.base_document.is_trashed)

    def test_containing_dossier_title_returns_main_dossier_title(self):
        self.login(self.regular_user)

        self.assertEqual(
            u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            self.document.containing_dossier_title())

        self.assertEqual(
            u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            self.sub_document.containing_dossier_title())


class TestBaseDocumentMails(TestBaseDocument):

    @property
    def base_document(self):
        return self.mail_eml

    @property
    def sub_document(self):
        return create(Builder("mail")
                      .with_message(MAIL_DATA)
                      .within(self.subdossier))
