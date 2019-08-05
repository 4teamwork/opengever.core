from opengever.document.fileactions import BaseDocumentFileActions
from opengever.document.fileactions import DocumentFileActions
from opengever.document.interfaces import IFileActions
from opengever.testing import IntegrationTestCase
from opengever.testing.test_case import TestCase
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass


class TestFileActionsInterface(TestCase):

    def test_base_document_file_actions_implements_ifileactions(self):
        verifyClass(IFileActions, BaseDocumentFileActions)

    def test_document_file_actions_implements_ifileactions(self):
        verifyClass(IFileActions, DocumentFileActions)


class TestIsVersionedDocument(IntegrationTestCase):
    """Test if we correctly detect if we're on a versioned document or not."""

    def test_returns_false_if_no_version_id_is_given(self):
        self.login(self.regular_user)
        adapter = getMultiAdapter((self.document, self.request), IFileActions)
        self.assertFalse(adapter.is_versioned())

    def test_returns_true_if_version_id_is_a_string(self):
        self.login(self.regular_user)
        self.request['version_id'] = '0'
        adapter = getMultiAdapter((self.document, self.request), IFileActions)
        self.assertTrue(adapter.is_versioned())

    def test_test_returns_false_if_version_id_is_no_digit(self):
        self.login(self.regular_user)
        self.request['version_id'] = u'g\xe4x'
        adapter = getMultiAdapter((self.document, self.request), IFileActions)
        self.assertFalse(adapter.is_versioned())

    def test_returns_true_if_version_id_is_a_number(self):
        self.login(self.regular_user)
        self.request['version_id'] = 123
        adapter = getMultiAdapter((self.document, self.request), IFileActions)
        self.assertTrue(adapter.is_versioned())


class TestIsVersionedMail(IntegrationTestCase):

    def test_mails_are_never_versioned(self):
        self.login(self.regular_user)
        self.request['version_id'] = '0'
        adapter = getMultiAdapter((self.mail_eml, self.request), IFileActions)
        self.assertFalse(adapter.is_versioned())
