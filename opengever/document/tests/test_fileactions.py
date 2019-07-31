from opengever.document.fileactions import BaseDocumentFileActions
from opengever.document.fileactions import DocumentFileActions
from opengever.document.interfaces import IFileActions
from opengever.testing.test_case import TestCase
from zope.interface.verify import verifyClass


class TestFileActionsInterface(TestCase):

    def test_base_document_file_actions_implements_ifileactions(self):
        verifyClass(IFileActions, BaseDocumentFileActions)

    def test_document_file_actions_implements_ifileactions(self):
        verifyClass(IFileActions, DocumentFileActions)
