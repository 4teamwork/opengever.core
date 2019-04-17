from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.bumblebee.tests.helpers import asset as bumblebee_asset
from ftw.bumblebee.tests.helpers import DOCX_CHECKSUM
from ftw.bumblebee.tests.helpers import get_queue
from ftw.testbrowser import browsing
from opengever.testing import assets
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from opengever.testing.helpers import create_document_version
from plone.namedfile.file import NamedBlobFile
from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone.uuid.interfaces import IUUID


class TestBumblebeeIntegrationWithDisabledFeature(IntegrationTestCase):
    """Test integration of ftw.bumblebee."""

    def test_bumblebee_checksum_is_calculated_for_opengever_docs(self):
        self.login(self.dossier_responsible)

        self.assertEquals(
            DOCX_CHECKSUM,
            IBumblebeeDocument(self.document).get_checksum(),
            )

    def test_opengever_documents_have_a_primary_field(self):
        self.login(self.dossier_responsible)
        fieldinfo = IPrimaryFieldInfo(self.document)

        self.assertEqual('file', fieldinfo.fieldname)

    @browsing
    def test_document_preview_is_hidden(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.visit(self.document, view='tabbedview_view-overview')

        self.assertEqual(0, len(browser.css('.documentPreview')))


class TestBumblebeeIntegrationWithEnabledFeature(IntegrationTestCase):

    features = ('bumblebee', )
    maxDiff = None

    @browsing
    def test_document_preview_is_visible(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.visit(self.document, view='tabbedview_view-overview')

        self.assertEqual(1, len(browser.css('.documentPreview')))

    @browsing
    def test_link_previews_to_bumblebee_overlay_document(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.visit(self.document, view="tabbedview_view-overview")

        preview_element = browser.css('.documentPreview .showroom-item')
        url = preview_element.first.get('data-showroom-target')

        self.assertTrue(url.endswith('@@bumblebee-overlay-document'))

    def test_does_not_queue_bumblebee_storing_if_not_digitally_available(self):
        self.login(self.dossier_responsible)

        create(Builder('document').within(self.dossier))
        queue = get_queue()

        self.assertEquals(0, len(queue), 'Expected no job in the queue.')

    def test_prevents_checked_out_document_checksum_update(self):
        self.login(self.dossier_responsible)
        self.checkout_document(self.document)

        self.assertEquals(
            DOCX_CHECKSUM,
            IBumblebeeDocument(self.document).get_checksum(),
            )

        self.document.update_file(
            'foo',
            content_type='text/plain',
            filename=u'foo.txt',
            )

        IBumblebeeDocument(self.document).handle_modified()

        self.assertEquals(
            DOCX_CHECKSUM,
            IBumblebeeDocument(self.document).get_checksum(),
            )

    def test_queues_bumblebee_storing_after_document_checkin(self):
        self.login(self.dossier_responsible)

        self.checkout_document(self.subdocument)
        queue = get_queue()
        queue.reset()

        self.subdocument.update_file(
            bumblebee_asset('example.docx').bytes(),
            content_type='text/plain',
            filename=u'example.docx',
            )

        self.checkin_document(self.subdocument)

        self.assertEquals(1, len(queue), 'Expected 1 job in the queue.')

        expected_job = {
            'application': 'local',
            'file_url': (
                'http://nohost/plone/bumblebee_download?checksum={}&uuid={}'
                .format(DOCX_CHECKSUM, IUUID(self.subdocument))
                ),
            'salt': IUUID(self.subdocument),
            'checksum': DOCX_CHECKSUM,
            'deferred': False,
            'url': (
                '/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen'
                '/dossier-1/dossier-2/document-22/bumblebee_trigger_storing'
                ),
            }

        found_job, = queue.queue

        self.assertDictEqual(expected_job, found_job)

    def test_queues_bumblebee_storing_after_revert_to_previous_version(self):
        self.login(self.dossier_responsible)

        self.subdocument.update_file(
            'foo',
            content_type='text/plain',
            filename=u'foo.txt',
            )

        create_document_version(
            self.subdocument,
            1,
            data=bumblebee_asset('example.docx').bytes(),
            )

        create_document_version(self.subdocument, 2)

        queue = get_queue()
        queue.reset()

        manager = self.get_checkout_manager(self.subdocument)
        manager.revert_to_version(1)

        self.assertEquals(1, len(queue), 'Expected 1 job in the queue.')

        expected_job = {
            'application': 'local',
            'file_url': (
                'http://nohost/plone/bumblebee_download?checksum={}&uuid={}'
                .format(DOCX_CHECKSUM, IUUID(self.subdocument))
                ),
            'salt': IUUID(self.subdocument),
            'checksum': DOCX_CHECKSUM,
            'deferred': False,
            'url': (
                '/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen'
                '/dossier-1/dossier-2/document-22/bumblebee_trigger_storing'
                ),
            }

        found_job, = queue.queue

        self.assertDictEqual(expected_job, found_job)

    def test_updates_checksum_after_docproperty_update(self):
        self.activate_feature('doc-properties')
        self.login(self.dossier_responsible)

        self.checkout_document(self.document)

        self.document.file = NamedBlobFile(
            data=assets.load(u'with_gever_properties_update.docx'),
            filename=u'with_gever_properties.docx',
            )

        checksum_before = IBumblebeeDocument(self.document).update_checksum()

        self.checkin_document(self.document)

        self.assertNotEqual(
            checksum_before,
            IBumblebeeDocument(self.document).get_checksum(),
            'Document checksum not updated after docproperties update.',
            )

        self.assertNotEqual(
            checksum_before,
            obj2brain(self.document).bumblebee_checksum,
            'Document checksum not updated after docproperties update.',
            )
