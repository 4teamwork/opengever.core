from base64 import b64encode
from contextlib import contextmanager
from datetime import datetime
from opengever.journal.handlers import DOCUMENT_ATTACHED
from opengever.journal.handlers import DOCUMENT_CHECKED_IN
from opengever.journal.handlers import DOCUMENT_CHECKED_OUT
from opengever.journal.tests.utils import get_journal_entry
from opengever.testing import IntegrationTestCase
from opengever.testing.fixtures import JWT_SECRET
from os import fstat
from os.path import basename
from plone import api
from requests_toolbelt.multipart.encoder import MultipartEncoder
from xml.etree import ElementTree as ET
from zope.component import getMultiAdapter
import json


# Sufficiently far in the future to keep yielding valid auth JWT
FREEZE_DATE = datetime(2100, 8, 3, 15, 25)

JWT_SIGNING_SECRET_PLONE = '/'.join((JWT_SECRET, 'plone', 'acl_users', 'jwt_auth'))
JWT_SIGNING_SECRET_ZOPE = '/'.join((JWT_SECRET, 'acl_users', 'jwt_auth'))


class OCIntegrationTestCase(IntegrationTestCase):
    """Extend IntegrationTestCase with Office Connector specific helpers."""

    @contextmanager
    def as_officeconnector(self, browser):
        current_user = api.user.get_current()
        try:
            yield browser.logout()
        finally:
            self.login(current_user, browser)

    def fetch_document_attach_oc_url(self, browser, document):
        headers = {
            'Accept': 'application/json',
            }

        url = browser.open(
            document,
            headers=headers,
            view='officeconnector_attach_url',
            ).json.get('url', None)

        return url

    def fetch_document_checkout_oc_url(self, browser, document):
        headers = {
            'Accept': 'application/json',
            }

        url = browser.open(
            document,
            headers=headers,
            view='officeconnector_checkout_url',
            ).json.get('url', None)

        return url

    def fetch_document_oneoffixx_oc_url(self, browser, document):
        headers = {
            'Accept': 'application/json',
            }

        url = browser.open(
            document,
            headers=headers,
            view='officeconnector_oneoffixx_url',
            ).json.get('url', None)

        return url

    def fetch_dossier_bcc(self, browser, dossier):
        headers = {
            'Accept': 'application/json',
            }

        email = browser.open(
            dossier,
            headers=headers,
            view='attributes',
            ).json.get('email', None)

        return email

    def fetch_dossier_multiattach_oc_url(self, browser, dossier, documents, bcc):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            }

        data = json.dumps(dict(
            bcc=bcc,
            documents=['/'.join(doc.getPhysicalPath()) for doc in documents],
            ))

        url = browser.open(
            self.portal,
            data=data,
            headers=headers,
            method='POST',
            view='officeconnector_attach_url',
            ).json.get('url', None)

        return url

    def fetch_document_attach_payloads(self, browser, raw_token, token):
        with self.as_officeconnector(browser):
            headers = {
                'Accept': 'application/json',
                'Authorization': ' '.join(('Bearer', raw_token, )),
                'Content-Type': 'application/json',
            }
            uuids = token.get('documents', [])
            data = json.dumps(uuids)

            payloads = browser.open(
                self.portal,
                method='POST',
                data=data,
                headers=headers,
                view='oc_attach',
                ).json

        for payload in payloads:
            self.assertTrue(payload.get('csrf-token'))
            # Provide a static CSRF token for testing purposes
            payload['csrf-token'] = u'86ecf9b4135514f8c94c61ce336a4b98b4aaed8a'

        for uuid in uuids:
            self.assert_journal_entry(
                api.content.get(UID=uuid),
                DOCUMENT_ATTACHED,
                u'Document attached to email via OfficeConnector',
                )

        return payloads

    def fetch_document_checkout_payloads(self, browser, raw_token, token):
        with self.as_officeconnector(browser):
            headers = {
                'Accept': 'application/json',
                'Authorization': ' '.join(('Bearer', raw_token, )),
                'Content-Type': 'application/json',
            }

            data = json.dumps(token.get('documents', []))

        payloads = browser.open(
            self.portal,
            method='POST',
            data=data,
            headers=headers,
            view='oc_checkout',
            ).json

        return payloads

    def fetch_document_oneoffixx_payloads(self, browser, raw_token, token):
        with self.as_officeconnector(browser):
            headers = {
                'Accept': 'application/json',
                'Authorization': ' '.join(('Bearer', raw_token, )),
                'Content-Type': 'application/json',
            }

            data = json.dumps(token.get('documents', []))

        payloads = browser.open(
            self.portal,
            method='POST',
            data=data,
            headers=headers,
            view='oc_oneoffixx',
            ).json

        return payloads

    def checkout_document(self, browser, raw_token, payload, document):
        """Logs out, uses JWT to check out the document via the RESTAPI and logs back in."""
        self.assertFalse(document.checked_out_by())

        with self.as_officeconnector(browser):
            headers = {
                'Accept': 'application/json',
                'Authorization': ' '.join(('Bearer', raw_token, )),
            }

            browser.open(document, view=payload.get('checkout'), method='POST', headers=headers)

        self.assertEqual(204, browser.status_code)
        self.assertTrue(document.checked_out_by())
        self.assertEqual(api.user.get_current().id, document.checked_out_by())
        self.assert_journal_entry(document, DOCUMENT_CHECKED_OUT, u'Document checked out')

    def lock_document(self, browser, raw_token, payload, document):
        """Logs out, uses JWT to WebDAV lock the document and logs back in."""
        lock_manager = getMultiAdapter((document, self.request), name='plone_lock_info')
        self.assertFalse(lock_manager.is_locked())

        with self.as_officeconnector(browser):
            headers = {
                'Authorization': ' '.join(('Bearer', raw_token, )),
                'Accept': 'application/json',
            }
            browser.open(document, view=payload.get('lock'), method='POST', headers=headers)

        self.assertEquals(200, browser.status_code)
        self.assertTrue(lock_manager.is_locked())

    def download_document(self, browser, raw_token, payload):
        with self.as_officeconnector(browser):
            headers = {
                'Accept': payload.get('content-type'),
                'Authorization': ' '.join(('Bearer', raw_token, )),
            }

            file_contents = browser.open(
                payload.get('document-url'),
                headers=headers,
                view=payload.get('download'),
                ).contents
            self.assertTrue(file_contents)

        return file_contents

    def download_oneoffixx_xml(self, browser, raw_token, payload):
        with self.as_officeconnector(browser):
            headers = {
                'Accept': 'application/xml',
                'Authorization': ' '.join(('Bearer', raw_token, )),
            }

            file_contents = browser.open(
                payload.get('document-url'),
                headers=headers,
                view=payload.get('connect-xml'),
                ).contents
            self.assertTrue(file_contents)

        return file_contents

    def upload_document(self, browser, raw_token, payload, document, new_file):
        with self.as_officeconnector(browser):
            filename = b64encode(basename(new_file.name))
            content_type = b64encode(payload.get('content-type'))
            headers = {
                'Accept': 'application/json',
                'Authorization': ' '.join(('Bearer', raw_token, )),
                'Tus-Resumable': '1.0.0',
                'Upload-Length': str(fstat(new_file.fileno()).st_size),
                'Upload-Metadata': 'filename {},content-type {}'.format(filename, content_type),
            }
            browser.open(document, view=payload.get('upload'), method='POST', headers=headers)
            self.assertEquals(201, browser.status_code)

            upload_url = browser.headers.get('location')
            headers = {
                'Accept': 'application/json',
                'Authorization': ' '.join(('Bearer', raw_token, )),
                'Tus-Resumable': '1.0.0',
                'Upload-Offset': '0',
                'Content-Type': 'application/offset+octet-stream',
            }
            browser.open(upload_url, method='PATCH', data=new_file.read(), headers=headers)
            self.assertEquals(204, browser.status_code)

    def unlock_document(self, browser, raw_token, payload, document):
        lock_manager = getMultiAdapter((document, self.request), name='plone_lock_info')
        self.assertTrue(lock_manager.is_locked())

        with self.as_officeconnector(browser):
            headers = {
                'Accept': 'application/json',
                'Authorization': ' '.join(('Bearer', raw_token, )),
                }
            browser.open(document, view=payload.get('unlock'), method='POST', headers=headers)
            self.assertEquals(200, browser.status_code)
            self.assertFalse(browser.json.get('locked', True))
            self.assertFalse(lock_manager.is_locked())

    def checkin_document(self, browser, raw_token, payload, document, comment=None):
        self.assertTrue(document.is_checked_out())

        with self.as_officeconnector(browser):
            headers = {
                'Accept': 'application/json',
                'Authorization': ' '.join(('Bearer', raw_token, )),
                'Content-Type': 'application/json',
            }

            browser.open(
                document,
                view=payload.get('checkin'),
                method='POST',
                headers=headers,
                data=json.dumps({'comment': comment}),
            )

        self.assert_journal_entry(document, DOCUMENT_CHECKED_IN, u'Document checked in')

        journal_comments = get_journal_entry(document).get('comments')

        if comment:
            self.assertTrue(journal_comments)
        else:
            self.assertFalse(journal_comments)

        self.assertEquals(204, browser.status_code)
        self.assertFalse(document.is_checked_out())
