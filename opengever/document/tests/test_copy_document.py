from opengever.testing import IntegrationTestCase
from plone import api


class TestCopyDocuments(IntegrationTestCase):

    def test_copying_a_document_prefixes_title_with_copy_of(self):
        self.login(self.regular_user)
        copy = api.content.copy(source=self.document, target=self.subdossier)
        self.assertEqual(u'copy of Vertr\xe4gsentwurf', copy.title)

    def test_copying_a_mail_prefixes_title_with_copy_of(self):
        self.login(self.regular_user)
        copy = api.content.copy(source=self.mail_eml, target=self.subdossier)
        self.assertEqual(u'copy of Die B\xfcrgschaft', copy.title)

    def test_copying_a_mail_does_not_create_versions(self):
        self.login(self.regular_user)
        copy = api.content.copy(source=self.mail_eml, target=self.subdossier)
        new_history = self.portal.portal_repository.getHistory(copy)
        self.assertEqual(len(new_history), 0)

    def test_copying_a_document_does_not_copy_its_versions(self):
        self.login(self.regular_user)

        # Check the original actually has a history
        old_history = self.portal.portal_repository.getHistory(self.document)
        self.assertEqual(len(old_history), 0)
        self.checkout_document(self.document)
        self.checkin_document(self.document)
        old_history = self.portal.portal_repository.getHistory(self.document)
        self.assertEqual(len(old_history), 1)

        cb = self.dossier.manage_copyObjects(self.document.id)
        self.dossier.manage_pasteObjects(cb)
        new_doc = self.dossier['copy_of_document-14']
        new_history = self.portal.portal_repository.getHistory(new_doc)
        self.assertEqual(len(new_history), 0)
