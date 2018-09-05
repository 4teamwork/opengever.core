from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import IntegrationTestCase
from opengever.dossier.command import CreateDocumentFromTemplateCommand


class TestCreateDocumentFromTemplateCommand(IntegrationTestCase):

    def test_create_document_from_template(self):
        expected_title = 'My title'
        expected_data = 'Test data'
        self.login(self.regular_user)
        template = create(Builder('document').within(self.dossiertemplate).with_dummy_content())
        command = CreateDocumentFromTemplateCommand(self.dossier, template, expected_title)
        document = command.execute()
        self.assertEqual(expected_title, document.title)
        self.assertEqual(expected_data, document.file.data)

    def test_create_document_from_template_without_file(self):
        expected_title = 'My title'
        self.login(self.regular_user)
        template = create(Builder('document').within(self.dossiertemplate))
        command = CreateDocumentFromTemplateCommand(self.dossier, template, expected_title)
        document = command.execute()
        self.assertEqual(expected_title, document.title)
        self.assertIsNone(document.file)
