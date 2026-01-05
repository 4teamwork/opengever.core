from base64 import b64encode
from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.mail.mail import OGMail
from opengever.mail.tests import MAIL_DATA
from opengever.private.interfaces import IPrivateFolderQuotaSettings
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from opengever.testing import IntegrationTestCase
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.MimetypesRegistry.MimeTypeItem import MimeTypeItem
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

    def prepare_tus_upload(self, folder, browser, headers=None, upload_metadata=None):
        browser.open(
            folder.absolute_url() + '/@tus-upload',
            method='POST',
            headers=dict({
                "Accept": "application/json",
                "Tus-Resumable": "1.0.0",
                "Upload-Length": str(UPLOAD_LENGTH),
                "Upload-Metadata": upload_metadata or UPLOAD_METADATA,
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

    def assert_tus_upload_succeeds(self, folder, browser, headers=None, upload_metadata=None):
        location = self.prepare_tus_upload(folder, browser, headers=headers,
                                           upload_metadata=upload_metadata)
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
    def test_can_upload_file_if_document_has_no_file(self, browser):
        self.login(self.regular_user, browser)
        self.assert_tus_replace_succeeds(self.empty_document, browser)

    @browsing
    def test_cannot_replace_document_if_checked_out_by_other(self, browser):
        self.login(self.dossier_responsible, browser)
        self.checkout(self.document, browser)

        self.login(self.regular_user, browser)
        self.assert_tus_replace_fails(self.document, browser)

    @skipIf(
        datetime.now() < datetime(2026, 12, 1),
        "Lock verification temporary disabled, because it's not yet works correctly. "
        "Will be fixed with https://4teamwork.atlassian.net/browse/CA-5107",
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
                self.private_dossier, browser, code=403, reason='Forbidden')

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
                u'languages': set([u'de', u'en']),
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

    @browsing
    def test_determines_content_type_from_mimetype_registry(self, browser):

        class test_extension(MimeTypeItem):

            __name__ = "Test"
            mimetypes = ('test/test',)
            extensions = ('test',)
            binary = 0

        self.login(self.regular_user, browser)

        mtype = test_extension()
        mtr = getToolByName(self.dossier, 'mimetypes_registry')
        mtr.register(mtype)

        upload_metadata = UPLOAD_METADATA.replace(
            "filename dGVzdC50eHQ=", "filename {}".format(b64encode("test.test")))
        doc = self.assert_tus_upload_succeeds(
            self.dossier, browser, upload_metadata=upload_metadata)

        self.assertEqual('test/test', doc.content_type())

        mtr.unregister(mtype)
        doc = self.assert_tus_upload_succeeds(
            self.dossier, browser, upload_metadata=upload_metadata)
        self.assertEqual('text/plain', doc.content_type())

    @browsing
    def test_tus_upload_can_set_document_date(self, browser):
        self.login(self.regular_user, browser)
        upload_metadata = UPLOAD_METADATA + ',document_date MjAxNS0wOC0yMQ=='
        doc = self.assert_tus_upload_succeeds(self.dossier, browser, upload_metadata=upload_metadata)
        self.assertEqual(date(2015, 8, 21), doc.document_date)

    @browsing
    def test_tus_replace_does_not_update_document_date(self, browser):
        self.login(self.regular_user, browser)
        self.checkout(self.document, browser)

        current_date = self.document.document_date
        upload_metadata = UPLOAD_METADATA + ',document_date MjAxNS0wOC0yMQ=='
        self.assert_tus_replace_succeeds(self.document, browser, headers={"Upload-Metadata": upload_metadata})
        self.assertEqual(current_date, self.document.document_date)

    @browsing
    def test_add_additional_metadata_for_ogmail(self, browser):
        self.login(self.regular_user, browser)
        mail = create(Builder('mail').with_message(MAIL_DATA))
        mail_document_date_b64 = b64encode(mail.document_date.isoformat().encode()).decode()
        upload_metadata = UPLOAD_METADATA + ',document_date {}'.format(mail_document_date_b64)
        doc = self.assert_tus_upload_succeeds(
            self.dossier, browser, upload_metadata=upload_metadata
        )
        self.assertEqual(mail.document_date, doc.document_date)
