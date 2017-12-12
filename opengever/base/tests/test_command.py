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
        self.assertEqual('no-subject.eml', mail.message.filename)

        self.assertEqual(u'testm\xe4il.msg', mail.original_message.filename)
        self.assertEqual('mock-msg-body', mail.original_message.data)
