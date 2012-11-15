from ftw.testing import MockTestCase
from mocker import ANY
from opengever.tabbedview.utils import get_containg_document_tab_url
from opengever.tabbedview.helper import linked_document_with_tooltip
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

    def tests_linked_document_with_tooltip(self):
        value = u'lorem ipsum <with tags>'

        class MockBrain(object):
            def __init__(self, request, type):
                self.REQUEST = request
                self.portal_type = type
                self.breadcrumb_titles = (
                    {'absolute_url': 'http://nohost/plone/dossier1',
                     'Title': 'Dossier1'},
                    {'absolute_url': 'http://nohost/plone/dossier1/task-1',
                     'Title': 'Task 1'},
                    {'absolute_url': 'http://nohost/plone/dossier1/task-1/document',
                     'Title': 'lorem ipsum <with tags>'})

            def getURL(self):
                return 'http://nohost/plone/dossier-1/task-1/document'

        request = self.stub_request()
        doc_brain = MockBrain(request, 'opengever.document.document')
        mail_brain = MockBrain(request, 'ftw.mail.mail')
        css_getter = self.mocker.replace('opengever.base.browser.helper.get_css_class')
        self.expect(css_getter(doc_brain)).result('contenttype-opengever-document').count(0, None)
        self.expect(css_getter(mail_brain)).result('contenttype-ftw-mail')

        self.replay()

        # document
        expected_link = """<div class='linkWrapper'>
    <a class='tabbedview-tooltip contenttype-opengever-document' href='#'></a>
    <a href='http://nohost/plone/dossier-1/task-1/document'>lorem ipsum &lt;with tags&gt;</a>
    <div class='tabbedview-tooltip-data'>
        <div class='tooltip-content'>
            <div class='tooltip-header'>lorem ipsum &lt;with tags&gt;</div>
            <div class='tooltip-breadcrumb'>Dossier1 &gt; Task 1 &gt; lorem ipsum &lt;with tags&gt;</div>
            <div class='tooltip-links'>
                <a href='http://nohost/plone/dossier-1/task-1/document/@@download'>
                    PDF
                </a>
                <a href='http://nohost/plone/dossier-1/task-1/document/edit'>
                    Edit metadata
                </a>
                <a href='http://nohost/plone/dossier-1/task-1/document/editing_document'>
                    Checkout and edit
                </a>
            </div>
        </div>
        <div class='bottomImage'></div>
    </div>
</div>"""

        self.assertEqual(linked_document_with_tooltip(doc_brain, value),
                         expected_link)

        # mail
        expected_link = """<div class='linkWrapper'>
    <a class='tabbedview-tooltip contenttype-ftw-mail' href='#'></a>
    <a href='http://nohost/plone/dossier-1/task-1/document'>lorem ipsum &lt;with tags&gt;</a>
    <div class='tabbedview-tooltip-data'>
        <div class='tooltip-content'>
            <div class='tooltip-header'>lorem ipsum &lt;with tags&gt;</div>
            <div class='tooltip-breadcrumb'>Dossier1 &gt; Task 1 &gt; lorem ipsum &lt;with tags&gt;</div>
            <div class='tooltip-links'>
                <a href='http://nohost/plone/dossier-1/task-1/document/edit'>
                    Edit metadata
                </a>
            </div>
        </div>
        <div class='bottomImage'></div>
    </div>
</div>"""

        self.assertEqual(linked_document_with_tooltip(mail_brain, value),
                 expected_link)
