from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.private.interfaces import IPrivateFolderQuotaSettings
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from opengever.testing import IntegrationTestCase
from plone import api
from six import BytesIO
from unittest import skipIf


UPLOAD_DATA = b"abcdefgh"
UPLOAD_LENGTH = len(UPLOAD_DATA)
UPLOAD_METADATA = 'filename dGVzdC50eHQ=,content-type dGV4dC9wbGFpbg==,@type b3BlbmdldmVyLmRvY3VtZW50LmRvY3VtZW50'


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

    def prepare_tus_upload(self, folder, browser, headers=None):
        browser.open(
            folder.absolute_url() + '/@tus-upload',
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

    def assert_tus_upload_fails(self, folder, browser, headers=None, code=403,
                                 reason='Forbidden'):
        location = self.prepare_tus_upload(folder, browser, headers=headers)
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

    def assert_tus_upload_succeeds(self, folder, browser, headers=None):
        location = self.prepare_tus_upload(folder, browser, headers=headers)
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
        self.assertEqual(browser.status_code, 204)
        location = browser.headers['location']
        doc_id = location.replace(folder.absolute_url(), '').lstrip('/')
        doc = folder.restrictedTraverse(doc_id)
        return doc

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
        datetime.now() < datetime(2022, 9, 11),
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

    @browsing
    def test_raises_if_quota_is_exceeded(self, browser):
        self.login(self.regular_user, browser)

        api.portal.set_registry_record(interface=IPrivateFolderQuotaSettings,
                                       name='size_hard_limit', value=1)

        with self.observe_children(self.private_dossier) as children:
            self.assert_tus_upload_fails(
                self.private_dossier, browser, code=507, reason='Insufficient Storage')

        self.assertEqual(0, len(children["added"]))

    @browsing
    def test_initializes_custom_properties_with_defaults_on_tus_upload(self, browser):
        self.login(self.regular_user, browser)

        PropertySheetSchemaStorage().clear()

        create(
            Builder('property_sheet_schema')
            .named('schema1')
            .assigned_to_slots(u'IDocument.default')
            .with_field(
                'textline', u'notrequired', u'Optional field with default', u'',
                required=False,
                default=u'Not required, still has default'
            )
            .with_field(
                'multiple_choice', u'languages', u'Languages', u'',
                required=True, values=[u'de', u'fr', u'en'],
                default={u'de', u'en'},
            )
        )

        doc = self.assert_tus_upload_succeeds(self.dossier, browser)
        expected_defaults = {
            u'IDocument.default': {
                u'languages': [u'de', u'en'],
                u'notrequired': u'Not required, still has default',
            },
        }
        self.assertEqual(
            expected_defaults,
            IDocumentCustomProperties(doc).custom_properties)

    @browsing
    def test_does_not_overwrite_existing_properties_on_tus_replace(self, browser):
        self.login(self.regular_user, browser)
        self.checkout(self.document, browser)

        PropertySheetSchemaStorage().clear()

        create(
            Builder('property_sheet_schema')
            .named('schema1')
            .assigned_to_slots(u'IDocument.default')
            .with_field(
                'textline', u'notrequired', u'Optional field with default', u'',
                required=False,
                default=u'Not required, still has default'
            )
            .with_field(
                'multiple_choice', u'languages', u'Languages', u'',
                required=True, values=[u'de', u'fr', u'en'],
                default={u'de', u'en'},
            )
        )

        IDocumentCustomProperties(self.document).custom_properties = {
            u'IDocument.default': {
                u'notrequired': u'This is an actual value, not a default',
            },
        }
        self.assert_tus_replace_succeeds(self.document, browser)
        expected_defaults = {
            u'IDocument.default': {
                u'notrequired': u'This is an actual value, not a default',
            },
        }
        self.assertEqual(
            expected_defaults,
            IDocumentCustomProperties(self.document).custom_properties)
