from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee import utils as bumblebee_utils
from ftw.bumblebee.tests.helpers import asset as bumblebee_asset
from ftw.bumblebee.tests.helpers import DOCX_CHECKSUM
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.testing import FunctionalTestCase
from plone.rfc822.interfaces import IPrimaryFieldInfo
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class TestBumblebeeIntegrationWithDisabledFeature(FunctionalTestCase):
    """Test integration of ftw.bumblebee."""

    def setUp(self):
        super(TestBumblebeeIntegrationWithDisabledFeature, self).setUp()

        self.document = create(Builder('document')
                               .attach_file_containing(
                                   bumblebee_asset('example.docx').bytes(),
                                   u'example.docx'))

    def test_bumblebee_checksum_is_calculated_for_opengever_docs(self):
        self.assertEquals(
            DOCX_CHECKSUM,
            bumblebee_utils.get_document_checksum(self.document))

    def test_opengever_documents_have_a_primary_field(self):
        fieldinfo = IPrimaryFieldInfo(self.document)
        self.assertEqual('file', fieldinfo.fieldname)

    @browsing
    def test_document_preview_is_hidden(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        browser.login().visit(document, view='tabbedview_view-overview')

        self.assertEqual(0, len(browser.css('.documentPreview')))


class TestBumblebeeIntegrationWithEnabledFeature(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_document_preview_is_visible(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        browser.login().visit(document, view='tabbedview_view-overview')

        self.assertEqual(1, len(browser.css('.documentPreview')))

    @browsing
    def test_link_previews_to_bumblebee_overlay_document(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        create(Builder('document').within(dossier))

        browser.login().visit(document, view="tabbedview_view-overview")

        self.assertEqual(
            'http://nohost/plone/dossier-1/document-1/@@bumblebee-overlay-document',
            browser.css('.imageContainer').first.get('data-showroom-target'))

    def test_prevents_checked_out_document_checksum_update(self):
        document = create(Builder('document')
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx')
                          .checked_out())

        self.assertEquals(
            DOCX_CHECKSUM,
            bumblebee_utils.get_document_checksum(document))

        document.update_file(filename=u'foo.txt',
                             content_type='text/plain',
                             data='foo')
        notify(ObjectModifiedEvent(document))

        self.assertEquals(
            DOCX_CHECKSUM,
            bumblebee_utils.get_document_checksum(document))
