from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.bumblebee.tests.helpers import asset as bumblebee_asset
from ftw.bumblebee.tests.helpers import DOCX_CHECKSUM
from ftw.bumblebee.tests.helpers import get_queue
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.dossier.interfaces import ITemplateFolderProperties
from opengever.testing import assets
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from opengever.testing.helpers import create_document_version
from plone import api
from plone.namedfile.file import NamedBlobFile
from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone.uuid.interfaces import IUUID
from zope.component import getMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from opengever.testing import IntegrationTestCase


class TestBumblebeeIntegrationWithDisabledFeature(IntegrationTestCase):
    """Test integration of ftw.bumblebee."""

    def test_bumblebee_checksum_is_calculated_for_opengever_docs(self):
        self.login(self.dossier_responsible)

        self.assertEquals(
            DOCX_CHECKSUM,
            IBumblebeeDocument(self.document).get_checksum())

    def test_opengever_documents_have_a_primary_field(self):
        self.login(self.dossier_responsible)

        fieldinfo = IPrimaryFieldInfo(self.document)
        self.assertEqual('file', fieldinfo.fieldname)

    @browsing
    def test_document_preview_is_hidden(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.visit(self.document, view='tabbedview_view-overview')
        self.assertEqual(0, len(browser.css('.documentPreview')))


class TestBumblebeeIntegrationWithEnabledFeature(FunctionalTestCase):

    maxDiff = None
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

        preview_element = browser.css('.documentPreview .showroom-item')
        self.assertEqual(
            'http://nohost/plone/dossier-1/document-1/@@bumblebee-overlay-document',
            preview_element.first.get('data-showroom-target'))

    def test_does_not_queue_bumblebee_storing_if_not_digitally_available(self):
        create(Builder('document'))
        queue = get_queue()
        self.assertEquals(0, len(queue), 'Expected no job in the queue.')

    def test_prevents_checked_out_document_checksum_update(self):
        document = create(Builder('document')
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx')
                          .checked_out())

        self.assertEquals(
            DOCX_CHECKSUM,
            IBumblebeeDocument(document).get_checksum())

        document.update_file('foo',
                             content_type='text/plain',
                             filename=u'foo.txt')
        notify(ObjectModifiedEvent(document))

        self.assertEquals(
            DOCX_CHECKSUM,
            IBumblebeeDocument(document).get_checksum())

    def test_queues_bumblebee_storing_after_document_checkin(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              'foo',
                              u'example.docx')
                          .checked_out())
        queue = get_queue()
        queue.reset()

        document.update_file(bumblebee_asset('example.docx').bytes(),
                             content_type='text/plain',
                             filename=u'example.docx')
        manager = getMultiAdapter((document, self.portal.REQUEST),
                                  ICheckinCheckoutManager)
        manager.checkin()

        self.assertEquals(1, len(queue), 'Expected 1 job in the queue.')
        job, = queue.queue

        self.assertDictEqual(
            {'application': 'local',
             'file_url': ('http://nohost/plone/bumblebee_download' +
                          '?checksum={}'.format(DOCX_CHECKSUM) +
                          '&uuid={}'.format(IUUID(document))),
             'salt': IUUID(document),
             'checksum': DOCX_CHECKSUM,
             'deferred': False,
             'url': '/plone/dossier-1/document-1/bumblebee_trigger_storing'},
            job)

    def test_queues_bumblebee_storing_after_revert_to_previous_version(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing('bar', u'example.docx'))

        document.file = NamedBlobFile(data='foo', filename=u'example.docx')

        create_document_version(document, 1,
                                data=bumblebee_asset('example.docx').bytes())
        create_document_version(document, 2)
        queue = get_queue()
        queue.reset()

        manager = getMultiAdapter((document, self.portal.REQUEST),
                                  ICheckinCheckoutManager)
        manager.revert_to_version(1)

        self.assertEquals(1, len(queue), 'Expected 1 job in the queue.')
        job, = queue.queue

        self.assertDictEqual(
            {'application': 'local',
             'file_url': ('http://nohost/plone/bumblebee_download' +
                          '?checksum={}'.format(DOCX_CHECKSUM) +
                          '&uuid={}'.format(IUUID(document))),
             'salt': IUUID(document),
             'checksum': DOCX_CHECKSUM,
             'deferred': False,
             'url': '/plone/dossier-1/document-1/bumblebee_trigger_storing'},
            job)

    @browsing
    def test_updates_checksum_and_queue_storing_after_docproperty_update(self, browser):
        api.portal.set_registry_record('create_doc_properties',
                                       interface=ITemplateFolderProperties,
                                       value=True)

        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .checked_out()
                          .with_asset_file('with_gever_properties.docx'))

        # update
        document.file = NamedBlobFile(
            data=assets.load(u'with_gever_properties_update.docx'),
            filename=u'with_gever_properties.docx')
        checksum_before = IBumblebeeDocument(document).update_checksum()

        browser.login().open(document)
        browser.click_on('without comment')

        self.assertNotEqual(
            checksum_before, IBumblebeeDocument(document).get_checksum(),
            'Document checksum not updated after docproperties update.')
        self.assertNotEqual(
            checksum_before, obj2brain(document).bumblebee_checksum,
            'Document checksum not updated after docproperties update.')
