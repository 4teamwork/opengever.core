from datetime import datetime
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from six import BytesIO
from unittest import skipIf

UPLOAD_DATA = b"abcdefgh"
UPLOAD_LENGTH = len(UPLOAD_DATA)
UPLOAD_METADATA = 'filename dGVzdC50eHQ=,content-type dGV4dC9wbGFpbg=='


class TestTUSUpload(IntegrationTestCase):

    def setUp(self):
        super(TestTUSUpload, self).setUp()

    def prepare_tus_replace(self, doc, browser, headers=None):
        browser.open(
            doc.absolute_url() + '/@tus-replace',
            method='POST',
            headers=dict({
                "Accept": "application/json",
                "Tus-Resumable": "1.0.0",
                "Upload-Length": str(UPLOAD_LENGTH),
                "Upload-Metadata": UPLOAD_METADATA,
            }, **headers or {}),
        )
        self.assertEqual(browser.status_code, 201)
        return browser.headers.get('Location')

    def assert_tus_replace_succeeds(self, doc, browser, headers=None):
        location = self.prepare_tus_replace(doc, browser, headers=headers)
        browser.open(
            location,
            method='PATCH',
            headers=dict({
                "Accept": "application/json",
                "Content-Type": "application/offset+octet-stream",
                "Upload-Offset": "0",
                "Tus-Resumable": "1.0.0",
            }, **headers or {}),
            data=BytesIO(UPLOAD_DATA),
        )
        self.assertEqual(browser.status_code, 204)

    def assert_tus_replace_fails(self, doc, browser, headers=None, code=403,
                                 reason='Forbidden'):
        location = self.prepare_tus_replace(doc, browser, headers=headers)
        with browser.expect_http_error(code=code, reason=reason):
            browser.open(
                location,
                method='PATCH',
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/offset+octet-stream",
                    "Upload-Offset": "0",
                    "Tus-Resumable": "1.0.0",
                },
                data=BytesIO(UPLOAD_DATA),
            )

    def checkout(self, doc, browser):
        browser.open(
            doc.absolute_url() + '/@checkout', method='POST',
            headers={"Accept": "application/json"},
        )
        self.assertEqual(browser.status_code, 204)

    def lock(self, doc, browser):
        browser.open(
            self.document.absolute_url() + '/@lock', method='POST',
            headers={"Accept": "application/json"},
        )
        self.assertEqual(browser.status_code, 200)
        return browser.json[u'token']

    @browsing
    def test_can_replace_document_if_checked_out(self, browser):
        self.login(self.regular_user, browser)
        self.checkout(self.document, browser)

        self.assert_tus_replace_succeeds(self.document, browser)

    @browsing
    def test_can_replace_document_if_checked_out_and_locked(self, browser):
        self.login(self.regular_user, browser)
        self.checkout(self.document, browser)
        token = self.lock(self.document, browser)

        self.assert_tus_replace_succeeds(
            self.document, browser, headers={'Lock-Token': token})

    @browsing
    def test_cannot_replace_document_if_not_checked_out(self, browser):
        self.login(self.regular_user, browser)
        self.assert_tus_replace_fails(self.document, browser)

    @browsing
    def test_cannot_replace_document_if_checked_out_by_other(self, browser):
        self.login(self.dossier_responsible, browser)
        self.checkout(self.document, browser)

        self.login(self.regular_user, browser)
        self.assert_tus_replace_fails(self.document, browser)

    @skipIf(
        datetime.now() < datetime(2021, 9, 11),
        "Lock verification temporary disabled, because it's not yet supported "
        "by Office Connector",
    )
    @browsing
    def test_cannot_replace_document_if_lock_token_not_provided(self, browser):
        self.login(self.regular_user, browser)
        self.checkout(self.document, browser)
        self.lock(self.document, browser)

        self.assert_tus_replace_fails(self.document, browser)

    @browsing
    def test_can_replace_proposal_if_docx(self, browser):
        self.login(self.administrator, browser)
        self.checkout(self.proposal_template, browser)

        self.assert_tus_replace_succeeds(
            self.proposal_template, browser,
            headers={
                'Upload-Metadata':
                    'filename dGVzdC5kb2N4,content-type dGV4dC9wbGFpbg==',
            },
        )

    @browsing
    def test_cannot_replace_proposal_if_not_docx(self, browser):
        self.login(self.administrator, browser)
        self.checkout(self.proposal_template, browser)

        self.assert_tus_replace_fails(
            self.proposal_template, browser, code=400, reason='Bad Request')
