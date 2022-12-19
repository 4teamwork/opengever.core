from opengever.tabbedview.utils import get_containing_document_tab_url
from opengever.testing import IntegrationTestCase


class TestContainingDocumentsTabFunction(IntegrationTestCase):

    def test_given_required_permission_function_returns_tab_url(self):
        self.login(self.regular_user)

        url = get_containing_document_tab_url(self.document)

        self.assertEqual(url, '%s#documents' % self.dossier.absolute_url())

    def test_without_required_permission_function_returns_context_url(self):
        self.login(self.dossier_responsible)
        doc = self.protected_document

        self.login(self.regular_user)
        url = get_containing_document_tab_url(doc)
        self.assertEqual(url, doc.absolute_url())
