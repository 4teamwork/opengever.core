from ftw.testing import MockTestCase
from mocker import ANY
from opengever.tabbedview.utils import get_containing_document_tab_url
from zope.interface import Interface


class TestContainingDocumentsTabFunction(MockTestCase):

    def mock_obj(self, absolute_url=None):
        obj = self.stub()
        if absolute_url:
            self.expect(obj.absolute_url()).result(absolute_url)
        return obj

    def mock_finder(self, dossier):
        finder = self.stub()
        self.expect(finder(ANY)).result(finder)
        self.expect(finder.find_dossier()).result(dossier)
        self.mock_adapter(finder, Interface, [Interface, ],
                          name=u'parent-dossier-finder')

    def mock_membership_tool(self, permission_granted=True):
        tool = self.stub()
        self.mock_tool(tool, 'portal_membership')
        self.expect(tool.checkPermission(ANY, ANY)).result(permission_granted)

    def test_given_required_permission_function_returns_tab_url(self):
        dossier_url = 'http://nohost/plone/dossier-1'
        dossier = self.mock_obj(dossier_url)
        document = self.mock_obj()
        self.mock_finder(dossier)
        self.mock_membership_tool(permission_granted=True)
        self.replay()

        url = get_containing_document_tab_url(document)
        self.assertEqual(url, '%s#documents' % dossier_url)

    def test_without_required_permission_function_returns_context_url(self):
        document_url = 'http://nohost/plone/dossier-1/task-1/document'
        document = self.mock_obj(document_url)
        dossier = self.mock_obj()
        self.mock_finder(dossier)
        self.mock_membership_tool(permission_granted=False)
        self.replay()

        url = get_containing_document_tab_url(document)
        self.assertEqual(url, document_url)
