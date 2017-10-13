from ftw.testbrowser import browsing
from opengever.document.document import Document
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import IntegrationTestCase
from plone.namedfile.file import NamedBlobFile
from zope.component import getMultiAdapter


class TestDocumentAPI(IntegrationTestCase):

    @browsing
    def test_get_oaw_init_labels_on_shadow_document(self, browser):
        self.login(self.dossier_responsible, browser)

        label_url = '/'.join((
            self.shadow_document.absolute_url(),
            'oaw_init_labels',
            ))

        browser.open(
            label_url,
            headers={
                'Accept': 'application/json',
            },
        )

        labels = browser.json

        self.assertIn(u'message', labels)
        self.assertTrue(labels.get(u'message', None))

        self.assertIn(u'title', labels)
        self.assertTrue(labels.get(u'title', None))

    @browsing
    def test_get_oaw_init_labels_on_normal_document(self, browser):
        self.login(self.dossier_responsible, browser)

        label_url = '/'.join((
            self.document.absolute_url(),
            'oaw_init_labels',
            ))

        with browser.expect_http_error(code=403, reason='Forbidden'):
            browser.open(
                label_url,
                headers={
                    'Accept': 'application/json',
                },
            )

    @browsing
    def test_get_oaw_retry_abort_labels_on_shadow_document(self, browser):
        self.login(self.dossier_responsible, browser)

        label_url = '/'.join((
            self.shadow_document.absolute_url(),
            'oaw_retry_abort_labels',
            ))

        browser.open(
            label_url,
            headers={
                'Accept': 'application/json',
            },
        )

        labels = browser.json

        self.assertIn(u'abort', labels)
        self.assertTrue(labels.get(u'abort', None))

        self.assertIn(u'retry', labels)
        self.assertTrue(labels.get(u'retry', None))

    @browsing
    def test_get_oaw_retry_abort_labels_on_normal_document(self, browser):
        self.login(self.dossier_responsible, browser)

        label_url = '/'.join((
            self.document.absolute_url(),
            'oaw_retry_abort_labels',
            ))

        with browser.expect_http_error(code=403, reason='Forbidden'):
            browser.open(
                label_url,
                headers={
                    'Accept': 'application/json',
                },
            )

    @browsing
    def test_get_shadow_document_deletion_message_on_shadow_document(self, browser):
        self.login(self.dossier_responsible, browser)

        label_url = '/'.join((
            self.shadow_document.absolute_url(),
            'delete_confirm',
            ))

        browser.open(
            label_url,
            headers={
                'Accept': 'application/json',
            },
        )

        labels = browser.json

        self.assertIn(u'label_no', labels)
        self.assertTrue(labels.get(u'label_no', None))

        self.assertIn(u'label_yes', labels)
        self.assertTrue(labels.get(u'label_yes', None))

        self.assertIn(u'message', labels)
        self.assertTrue(labels.get(u'message', None))

        self.assertIn(u'title', labels)
        self.assertTrue(labels.get(u'title', None))

    @browsing
    def test_get_shadow_document_deletion_message_on_normal_document(self, browser):
        self.login(self.dossier_responsible, browser)

        label_url = '/'.join((
            self.document.absolute_url(),
            'delete_confirm',
            ))

        with browser.expect_http_error(code=403, reason='Forbidden'):
            browser.open(
                label_url,
                headers={
                    'Accept': 'application/json',
                },
            )

    @browsing
    def test_shadow_document_can_be_deleted_by_owner(self, browser):
        self.login(self.dossier_responsible, browser)

        deletion_url = '/'.join((
            self.shadow_document.absolute_url(),
            'delete_shadow_document',
            ))

        browser.open(
            deletion_url,
            method='DELETE',
            headers={
                'Accept': 'application/json',
            },
        )

        self.assertFalse([doc for doc in self.dossier.objectValues() if isinstance(doc, Document) and doc.is_shadow_document()])

    @browsing
    def test_shadow_document_cannot_be_deleted_by_another_user(self, browser):
        self.login(self.dossier_responsible, browser)

        deletion_url = '/'.join((
            self.shadow_document.absolute_url(),
            'delete_shadow_document',
            ))

        self.login(self.regular_user, browser)

        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open(
                deletion_url,
                method='DELETE',
                headers={
                    'Accept': 'application/json',
                },
            )

        self.login(self.dossier_responsible, browser)
        self.assertTrue(self.shadow_document)

    @browsing
    def test_shadow_document_can_be_deleted_by_portal_manager(self, browser):
        self.login(self.dossier_responsible, browser)

        deletion_url = '/'.join((
            self.shadow_document.absolute_url(),
            'delete_shadow_document',
            ))

        self.login(self.manager, browser)

        browser.open(
            deletion_url,
            method='DELETE',
            headers={
                'Accept': 'application/json',
            },
        )

        self.assertFalse([doc for doc in self.dossier.objectValues() if isinstance(doc, Document) and doc.is_shadow_document()])

    @browsing
    def test_normal_document_cannot_be_deleted(self, browser):
        self.login(self.dossier_responsible, browser)

        deletion_url = '/'.join((
            self.document.absolute_url(),
            'delete_shadow_document',
            ))

        self.login(self.regular_user, browser)

        with browser.expect_http_error(code=403, reason='Forbidden'):
            browser.open(
                deletion_url,
                method='DELETE',
                headers={
                    'Accept': 'application/json',
                },
            )

        self.assertTrue(self.document)

    @browsing
    def test_shadow_document_with_a_file_cannot_be_deleted(self, browser):
        self.login(self.dossier_responsible, browser)

        field = IDocumentSchema['file']
        uploaded_file = NamedBlobFile('bla bla', filename=u'test.txt')
        field.set(self.shadow_document, uploaded_file)

        self.assertEquals(0, self.shadow_document.version_id)

        deletion_url = '/'.join((
            self.shadow_document.absolute_url(),
            'delete_shadow_document',
            ))

        with browser.expect_http_error(code=403, reason='Forbidden'):
            browser.open(
                deletion_url,
                method='DELETE',
                headers={
                    'Accept': 'application/json',
                },
            )

        self.assertTrue(self.shadow_document)

    @browsing
    def test_shadow_document_with_versions_cannot_be_deleted(self, browser):
        self.login(self.dossier_responsible, browser)

        getMultiAdapter((self.shadow_document, self.shadow_document.REQUEST), ICheckinCheckoutManager).checkout()

        field = IDocumentSchema['file']
        uploaded_file = NamedBlobFile('bla bla', filename=u'test.txt')
        field.set(self.shadow_document, uploaded_file)

        getMultiAdapter((self.shadow_document, self.shadow_document.REQUEST), ICheckinCheckoutManager).checkin()

        self.assertNotEquals(0, self.shadow_document.version_id)

        deletion_url = '/'.join((
            self.shadow_document.absolute_url(),
            'delete_shadow_document',
            ))

        with browser.expect_http_error(code=403, reason='Forbidden'):
            browser.open(
                deletion_url,
                method='DELETE',
                headers={
                    'Accept': 'application/json',
                },
            )

        self.assertTrue(self.shadow_document)
