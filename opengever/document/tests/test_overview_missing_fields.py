from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.testing import FunctionalTestCase
from plone.autoform.interfaces import OMITTED_KEY
from zope.interface import Interface


class TestDocumentOverviewMissingFields(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentOverviewMissingFields, self).setUp()
        omitted_values = []
        if OMITTED_KEY in IDocumentMetadata.getTaggedValueTags():
            omitted_values.extend(
                IDocumentMetadata.getTaggedValue(OMITTED_KEY))
        self.orig_omitted_values = list(omitted_values)
        omitted_values.append((Interface, 'document_type', 'true'))
        IDocumentMetadata.setTaggedValue(OMITTED_KEY, omitted_values)

        self.document = create(Builder('document'))

    def tearDown(self):
        IDocumentMetadata.setTaggedValue(OMITTED_KEY, self.orig_omitted_values)

    @browsing
    def test_document_type_can_be_dropped_from_overview(self, browser):
        browser.login()
        browser.visit(self.document, view="tabbedview_view-overview")
        field_headers = browser.css('table tr th').text
        self.assertEquals(
            ['Title',
             'Document Date',
             'File',
             'Created',
             'Modified',
             'Author',
             'creator',
             'Description',
             'Keywords',
             'Foreign Reference',
             'Checked out',
             'Digital Available',
             'Preserved as paper',
             'Date of receipt',
             'Date of delivery',
             'Related Documents',
             'Classification',
             'Privacy layer',
             'Public Trial',
             'Public trial statement'],
            field_headers)
