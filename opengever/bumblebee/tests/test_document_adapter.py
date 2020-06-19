from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.interfaces import IBumblebeeDocument
from opengever.mail.tests import MAIL_DATA
from opengever.testing import FunctionalTestCase


class TestDocumentAdapter(FunctionalTestCase):

    def test_document_with_file_is_digitally_available(self):
        document_with_file = create(Builder("document").with_dummy_content())
        self.assertTrue(
            IBumblebeeDocument(document_with_file).is_convertable())

    def test_document_without_file_is_not_digitally_available(self):
        document_without_file = create(Builder("document"))
        self.assertFalse(
            IBumblebeeDocument(document_without_file).is_convertable())


class TestMailDocumentAdapter(FunctionalTestCase):

    def test_use_original_message_as_primary_field_if_available(self):
        mail_with_original_message = create(Builder('mail')
                                            .with_message(MAIL_DATA)
                                            .with_dummy_message()
                                            .with_dummy_original_message())

        bumblebee_document = IBumblebeeDocument(mail_with_original_message)
        self.assertEqual(
            'No Subject.msg',
            bumblebee_document.get_primary_field().filename)

    def test_use_default_primary_field_without_original_message_available(self):
        mail_with_original_message = create(Builder('mail')
                                            .with_message(MAIL_DATA)
                                            .with_dummy_message())

        bumblebee_document = IBumblebeeDocument(mail_with_original_message)
        self.assertEqual(
            'No Subject.eml',
            bumblebee_document.get_primary_field().filename)
