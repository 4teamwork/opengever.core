from opengever.base.command import CreateDocumentCommand
from opengever.base.command import CreateEmailCommand
from opengever.testing import IntegrationTestCase


class MockMsg2MimeTransform(object):

    def transform(self, data):
        return 'mock-eml-body'


class TestCreateEmailCommand(IntegrationTestCase):

    def test_converted_msg_is_created_correctly(self):
        self.login(self.regular_user)
        command = CreateEmailCommand(
            self.dossier, 'testm\xc3\xa4il.msg', 'mock-msg-body',
            transform=MockMsg2MimeTransform())
        mail = command.execute()

        self.assertEqual('message/rfc822', mail.message.contentType)
        self.assertEqual('No Subject.eml', mail.message.filename)

        self.assertEqual(u'No Subject.msg', mail.original_message.filename)
        self.assertEqual('mock-msg-body', mail.original_message.data)


class TestCreateDocumentCommand(IntegrationTestCase):

    def test_create_document_from_command(self):
        self.login(self.regular_user)
        command = CreateDocumentCommand(
            self.dossier, 'testm\xc3\xa4il.txt', 'buh!', title='\xc3\x9cnicode')
        document = command.execute()

        self.assertIsInstance(document.title, unicode)
        self.assertEqual(u'\xdcnicode', document.title)
        self.assertEqual('buh!', document.file.data)
        self.assertEqual('text/plain', document.file.contentType)
