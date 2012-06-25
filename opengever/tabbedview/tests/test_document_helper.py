from ftw.testing import MockTestCase
from mocker import ANY
from opengever.tabbedview.utils import get_containg_document_tab_url
from zope.interface import Interface


class TestDocumentsUrl(MockTestCase):

    def test_containg_document_tab_url(self):
        document = self.stub()
        dossier = self.stub()
        tool = self.stub()
        finder = self.stub()
        self.expect(finder(ANY)).result(finder)
        self.expect(finder.find_dossier()).result(dossier)
        self.mock_adapter(finder, Interface, [Interface, ],
                          name=u'parent-dossier-finder')

        self.expect(dossier.absolute_url()).result(
            'http://nohost/plone/dossier-1')
        self.mock_tool(tool, 'portal_membership')
        self.expect(tool.checkPermission(ANY, ANY)).result(True)
        self.replay()
        url = get_containg_document_tab_url(document)
        self.assertEqual(url, 'http://nohost/plone/dossier-1#documents')

    def test_containg_document_tab_url_without_permission(self):
        document = self.stub()
        dossier = self.stub()
        tool = self.stub()
        finder = self.stub()
        self.expect(finder(ANY)).result(finder)
        self.expect(finder.find_dossier()).result(dossier)
        self.mock_adapter(
            finder, Interface, [Interface, ], name=u'parent-dossier-finder')

        self.expect(document.absolute_url()).result(
            'http://nohost/plone/dossier-1/task-1/document')
        self.mock_tool(tool, 'portal_membership')
        self.expect(tool.checkPermission(ANY, ANY)).result(False)
        self.replay()
        url = get_containg_document_tab_url(document)
        self.assertEqual(url, 'http://nohost/plone/dossier-1/task-1/document')
