from opengever.base.command import CreateDocumentCommand
from opengever.base.command import CreateEmailCommand
from opengever.document.behaviors.related_docs import IRelatedDocuments
from opengever.testing import IntegrationTestCase
from z3c.relationfield.relation import RelationValue
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


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

    def test_create_document_from_command_respects_behaviors(self):
        self.login(self.regular_user)

        relation = RelationValue(getUtility(IIntIds).getId(self.subdocument))
        command = CreateDocumentCommand(
            self.dossier, 'testm\xc3\xa4il.txt', 'buh!', relatedItems=[relation])
        document = command.execute()

        self.assertIn(
            'opengever.document.behaviors.related_docs.IRelatedDocuments.relatedItems',
            IAnnotations(document))
        self.assertIn(relation, IRelatedDocuments(document).relatedItems)
