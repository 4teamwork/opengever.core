from ftw.dictstorage.interfaces import IDictStorage
from ftw.testing import MockTestCase
from lxml import etree
from mocker import ANY
from opengever.tabbedview.helper import linked_document_with_tooltip
from opengever.tabbedview.helper import linked_trashed_document_with_tooltip
from pyquery import PyQuery
from zope.interface import Interface
import cgi


ITEM_TITLE = u'lorem ipsum <with tags>'


def link(href='#', text=''):
    """Helper method to create a link element to be used in tests.
    """
    text = cgi.escape(text)
    lnk = PyQuery('<a href="%s">%s</a>' % (href, text))[0]
    return lnk


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
             'Title': ITEM_TITLE})

    def getURL(self):
        return 'http://nohost/plone/dossier-1/task-1/document'


class LinkTestCase(MockTestCase):
    """TestCase base class with helper methods and custom assertions to test
    - if a link is contained in a piece of markup
    - if a tooltip link (ftw.tooltip style) is contained in a piece of markup

    It also sets up some stubs and mocks required by testcases inheriting from
    it.
    """

    def setUp(self):
        super(LinkTestCase, self).setUp()
        self.request = self.stub_request()
        self.doc_brain = MockBrain(self.request, 'opengever.document.document')
        self.mail_brain = MockBrain(self.request, 'ftw.mail.mail')
        self.user_mock = self.stub()

        user_getter = self.mocker.replace('plone.api.user.get_current')
        self.expect(user_getter()).result(self.user_mock).count(0, None)
        self.expect(self.user_mock.getId()).result('foo')

        css_getter = self.mocker.replace(
            'opengever.base.browser.helper.get_css_class')
        self.expect(css_getter(self.doc_brain)
                    ).result('contenttype-opengever-document').count(0, None)
        self.expect(css_getter(self.mail_brain)
                    ).result('contenttype-ftw-mail').count(0, None)

        mtool = self.stub()
        self.expect(mtool.getAuthenticatedMember().getId()).result('test_id')
        self.mock_tool(mtool, 'portal_membership')

        dictstorage = self.stub()
        self.expect(dictstorage.get(ANY)).result(None)
        self.mock_adapter(dictstorage, IDictStorage, (Interface,))
        self.expect(dictstorage(ANY)).result({}).count(0, None)

    def _get_tooltip_data(self, content):
        if not isinstance(content, PyQuery):
            content = PyQuery(content)

        tooltip_data = content('.tabbedview-tooltip-data')
        if not len(tooltip_data) == 1:
            self.fail("None or more than one .tabbedview-tooltip-data found in"
                      " \n%s" % content)
        return tooltip_data

    def _get_tooltip_content(self, content):
        tooltip_data = self._get_tooltip_data(content)
        tooltip_content = tooltip_data('.tooltip-content')
        if not len(tooltip_content) == 1:
            self.fail("None or more than one .tooltip-content found in"
                      " \n%s" % content)
        return tooltip_content

    def assertLinkIn(self, link, content):
        if not isinstance(content, PyQuery):
            content = PyQuery(content)
        anchors = content('a')

        for anchor in anchors:
            href = anchor.attrib['href']
            text = anchor.text and anchor.text or ''

            if href == link.attrib['href'] \
            and text.strip() == link.text.strip():
                return True
        self.fail("%s not found in \n%s" % (etree.tostring(link), content))

    def assertTooltipLinkIn(self, link, content):
        tooltip_content = self._get_tooltip_content(content)
        return self.assertLinkIn(link, tooltip_content)

    def assertTooltipLinkNotIn(self, link, content):
        try:
            self.assertTooltipLinkIn(link, content)
        except AssertionError:
            return True
        self.fail("Found unexpected link %s in \n%s" %
                  (etree.tostring(link), content))

    def assertTooltipHeaderEquals(self, header_text, content):
        tooltip_content = self._get_tooltip_content(content)
        header_contents = tooltip_content('.tooltip-header' )[0]
        return self.assertEquals(header_text, header_contents.text)

    def assertTooltipBreadcrumbsEquals(self, breadcrumbs_text, content):
        tooltip_content = self._get_tooltip_content(content)
        breadcrumbs = tooltip_content('.tooltip-breadcrumb' )[0]
        return self.assertEquals(breadcrumbs_text, breadcrumbs.text)

    def assertIconLink(self, expected_link, content):
        content = PyQuery(content)
        link = content('.tabbedview-tooltip')[0]
        self.assertEquals(expected_link, link.get('href'))


class TestWithoutPDFConverter(LinkTestCase):
    """TestCase base class to simulate PDF converter NOT being available.
    """
    def setUp(self):
        super(TestWithoutPDFConverter, self).setUp()
        import opengever.tabbedview
        opengever.tabbedview.helper.PDFCONVERTER_AVAILABLE = False


class TestWithPDFConverter(LinkTestCase):
    """TestCase base class to simulate PDF converter being available.
    """
    def setUp(self):
        super(TestWithPDFConverter, self).setUp()
        import opengever.tabbedview
        opengever.tabbedview.helper.PDFCONVERTER_AVAILABLE = True


class TestTooltipLinkedHelperWithDocuments(TestWithPDFConverter):

    def markup(self):
        return linked_document_with_tooltip(self.doc_brain, ITEM_TITLE)

    def test_simple_link_to_document_view_is_available(self):
        self.replay()
        view_link = link(href=self.doc_brain.getURL(), text=ITEM_TITLE)
        self.assertLinkIn(view_link, self.markup())

    def test_tooltip_link_to_edit_metadata_is_available(self):
        self.replay()
        metadata_link = link(href="%s/edit_checker" % self.doc_brain.getURL(),
                             text="Edit metadata")
        self.assertTooltipLinkIn(metadata_link, self.markup())

    def test_tooltip_link_to_checkout_and_edit_is_available(self):
        self.replay()
        checkout_link = link(
            href="%s/editing_document" % self.doc_brain.getURL(),
            text="Checkout and edit")
        self.assertTooltipLinkIn(checkout_link, self.markup())

    def test_tooltip_header_equals_ITEM_TITLE(self):
        self.replay()
        self.assertTooltipHeaderEquals(ITEM_TITLE, self.markup())

    def test_tooltip_breadcrumbs_correspond_to_item_location(self):
        self.replay()
        self.assertTooltipBreadcrumbsEquals(
            'Dossier1 > Task 1 > lorem ipsum <with tags>', self.markup())

    def test_tooltip_icon_links_to_document(self):
        self.replay()
        self.assertIconLink(
            'http://nohost/plone/dossier-1/task-1/document',
            self.markup())


class TestTooltipLinkedHelperWithMails(TestWithPDFConverter):

    def markup(self):
        return linked_document_with_tooltip(self.mail_brain, ITEM_TITLE)

    def test_simple_link_to_mail_view_is_available(self):
        self.replay()
        view_link = link(href=self.mail_brain.getURL(), text=ITEM_TITLE)
        self.assertLinkIn(view_link, self.markup())

    def test_tooltip_link_to_edit_metadata_is_available(self):
        self.replay()
        metadata_link = link(href="%s/edit_checker" % self.mail_brain.getURL(),
                             text="Edit metadata")
        self.assertTooltipLinkIn(metadata_link, self.markup())

    def test_no_link_to_checkout_and_edit_for_mails(self):
        self.replay()
        # Mails can't be edited (only their metadata), so there must not be
        # a link to "Checkout and edit"
        self.assertNotIn('/editing_document', self.markup())

    def test_tooltip_header_equals_ITEM_TITLE(self):
        self.replay()
        self.assertTooltipHeaderEquals(ITEM_TITLE, self.markup())

    def test_tooltip_breadcrumbs_correspond_to_item_location(self):
        self.replay()
        self.assertTooltipBreadcrumbsEquals(
            'Dossier1 > Task 1 > lorem ipsum <with tags>', self.markup())

    def test_tooltip_icon_links_to_document(self):
        self.replay()
        self.assertIconLink(
            'http://nohost/plone/dossier-1/task-1/document',
            self.markup())


class TestTooltipLinkedHelperWithTrashedDocs(TestWithPDFConverter):

    def markup(self):
        return linked_trashed_document_with_tooltip(self.doc_brain, ITEM_TITLE)

    def test_link_to_document_view_is_available(self):
        self.replay()
        view_link = link(href=self.doc_brain.getURL(), text=ITEM_TITLE)
        self.assertLinkIn(view_link, self.markup())

    def test_tooltip_header_equals_ITEM_TITLE(self):
        self.replay()
        self.assertTooltipHeaderEquals(ITEM_TITLE, self.markup())

    def test_tooltip_breadcrumbs_correspond_to_item_location(self):
        self.replay()
        self.assertTooltipBreadcrumbsEquals(
            'Dossier1 > Task 1 > lorem ipsum <with tags>', self.markup())


class TestTooltipLinkedHelperWithPDFConverter(TestWithPDFConverter):

    def test_pdf_link_available_for_documents(self):
        self.replay()
        markup = linked_document_with_tooltip(self.doc_brain, ITEM_TITLE)
        pdf_link = link(href="%s/@@download_pdfpreview" % self.doc_brain.getURL(), text="PDF")
        self.assertTooltipLinkIn(pdf_link, markup)

    def test_no_pdf_link_for_mails(self):
        self.replay()
        markup = linked_document_with_tooltip(self.mail_brain, ITEM_TITLE)
        # Even with PDF Converter available there should be no PDF preview
        # links for mails.
        self.assertNotIn('@@download_pdfpreview', markup)

    def test_pdf_link_available_for_trashed_docs(self):
        self.replay()
        markup = linked_trashed_document_with_tooltip(self.doc_brain, ITEM_TITLE)
        pdf_link = link(href="%s/@@download_pdfpreview" % self.doc_brain.getURL(), text="PDF")
        self.assertTooltipLinkIn(pdf_link, markup)


class TestTooltipLinkedHelperWithoutPDFConverter(TestWithoutPDFConverter):

    def test_no_pdf_link_for_documents(self):
        self.replay()
        markup = linked_document_with_tooltip(self.doc_brain, ITEM_TITLE)
        self.assertNotIn('@@download_pdfpreview', markup)

    def test_no_pdf_link_for_mails(self):
        self.replay()
        markup = linked_document_with_tooltip(self.mail_brain, ITEM_TITLE)
        self.assertNotIn('@@download_pdfpreview', markup)

    def test_no_pdf_link_for_trashed_docs(self):
        self.replay()
        markup = linked_trashed_document_with_tooltip(self.doc_brain, ITEM_TITLE)
        self.assertNotIn('@@download_pdfpreview', markup)
