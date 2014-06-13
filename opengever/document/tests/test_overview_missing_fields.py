from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.document.document import IDocumentSchema
from opengever.testing import FunctionalTestCase
from plone.autoform.interfaces import OMITTED_KEY
from zope.interface import Interface


class TestDocumentOverviewMissingFields(FunctionalTestCase):

    def setUp(self):
        create(Builder('ogds_user'))
        omitted_values = IDocumentSchema.getTaggedValue(OMITTED_KEY)
        self.org_omitted_values = list(omitted_values)
        omitted_values.append((Interface, 'document_type', 'true'))
        IDocumentSchema.setTaggedValue(OMITTED_KEY, omitted_values)

        self.document = create(Builder('document'))

    def tearDown(self):
        IDocumentSchema.setTaggedValue(OMITTED_KEY, self.org_omitted_values)

    @browsing
    def test_document_overview_without_document_type(self, browser):
        browser.login()
        browser.visit(self.document, view="tabbedview_view-overview")
