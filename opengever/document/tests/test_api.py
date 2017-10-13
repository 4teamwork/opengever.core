from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


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
