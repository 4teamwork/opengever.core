from ftw.builder import Builder
from ftw.builder import create
from opengever.base.command import CreateEmailCommand
from opengever.testing import FunctionalTestCase


class MockMsg2MimeTransform(object):

    def transform(self, data):
        return 'mock-eml-body'


class TestCreateEmailCommand(FunctionalTestCase):

    def setUp(self):
        super(TestCreateEmailCommand, self).setUp()
        self.repo, self.repo_folder = create(Builder('repository_tree'))
        self.dossier = create(Builder('dossier').within(self.repo_folder))

    def test_converted_msg_is_created_correctly(self):
        command = CreateEmailCommand(
            self.dossier, 'testm\xc3\xa4il.msg', 'mock-msg-body',
            transform=MockMsg2MimeTransform())
        mail = command.execute()

        self.assertEqual('message/rfc822', mail.message.contentType)
        self.assertEqual('no-subject.eml', mail.message.filename)

        self.assertEqual(u'testm\xe4il.msg', mail.original_message.filename)
        self.assertEqual('mock-msg-body', mail.original_message.data)
