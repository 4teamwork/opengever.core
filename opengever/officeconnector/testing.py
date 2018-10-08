from contextlib import contextmanager
from datetime import datetime
from opengever.journal.handlers import DOCUMENT_ATTACHED
from opengever.journal.handlers import DOCUMENT_CHECKED_IN
from opengever.journal.handlers import DOCUMENT_CHECKED_OUT
from opengever.journal.tests.utils import get_journal_entry
from opengever.testing import IntegrationTestCase
from opengever.testing.fixtures import JWT_SECRET
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
        """Logs out, uses JWT to check out the document and logs back in."""
        self.assertFalse(document.checked_out_by())

        with self.as_officeconnector(browser):
            headers = {
                'Accept': 'text/html',
                'Authorization': ' '.join(('Bearer', raw_token, )),
            }

            browser.open(
                document,
                headers=headers,
                view=payload.get('checkout'),
                send_authenticator=True,
                )

        self.assertEquals(api.user.get_current().id, document.checked_out_by())
        self.assert_journal_entry(
            document,
            DOCUMENT_CHECKED_OUT,
            u'Document checked out',
            )

    def lock_document(self, browser, raw_token, document):
        """Logs out, uses JWT to WebDAV lock the document and logs back in."""
        lock_manager = getMultiAdapter(
            (document, self.request),
            name='plone_lock_info',
            )
        self.assertFalse(lock_manager.is_locked())

        with self.as_officeconnector(browser):
            headers = {
                'Authorization': ' '.join(('Bearer', raw_token, )),
                'Content-Type': 'text/xml; charset="utf-8"',
                'Depth': '0',
                'Timeout': 'Infinite, Second-4100000000',
                }

            data = (
                '<?xml version="1.0" encoding="utf-8"?>\n'
                '<D:lockinfo xmlns:D="DAV:">\n'
                '  <D:lockscope><D:exclusive/></D:lockscope>\n'
                '  <D:locktype><D:write/></D:locktype>\n'
                '  <D:owner>\n'
                '  <D:href>Office Connector</D:href>\n'
                '  </D:owner>\n'
                '</D:lockinfo>'
                )

            browser.webdav('LOCK', document, headers=headers, data=data)
            self.assertEquals(200, browser.status_code)
            self.assertTrue(lock_manager.is_locked())

            # Because of a Plone WebDav namespacing bug, the generated
            # XML is not valid and has to be corrected before parsing.
            # ftw.testbrowser does the correction when generating self.document
            contents = browser.contents.replace(
                '<D:href>', '<d:href>').replace('</D:href>', '</d:href>')

            lock_token = ET.fromstring(contents).find(
                './d:lockdiscovery/d:activelock/d:locktoken/',
                {'d': 'DAV:'},
                ).text

            self.assertTrue(lock_token)

        return lock_token

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
            encoder = MultipartEncoder({
                'form.widgets.file.action': 'replace',
                'form.buttons.upload': 'oc-file-upload',
                'form.widgets.file': (
                    basename(new_file.name),
                    new_file,
                    document.content_type(),
                    ),
                '_authenticator': payload.get('csrf-token'),
                })

            headers = {
                'Authorization': ' '.join(('Bearer', raw_token, )),
                'Content-Type': encoder.content_type,
            }
            browser.open(
                document,
                view=payload.get('upload-form'),
                method='POST',
                headers=headers,
                data=encoder.to_string(),
                )

            self.assertEquals(204, browser.status_code)

    def unlock_document(self, browser, raw_token, document, lock_token):
        lock_manager = getMultiAdapter(
            (document, self.request),
            name='plone_lock_info',
            )
        self.assertTrue(lock_manager.is_locked())

        with self.as_officeconnector(browser):
            headers = {
                'Authorization': ' '.join(('Bearer', raw_token, )),
                'Lock-Token': lock_token,
                }

            browser.open(
                document,
                method='UNLOCK',
                headers=headers,
                )

            self.assertEquals(204, browser.status_code)
            self.assertFalse(lock_manager.is_locked())

    def checkin_document(self, browser, raw_token, payload, document, comment=None):  # noqa
        with self.as_officeconnector(browser):
            headers = {
                'Authorization': ' '.join(('Bearer', raw_token, )),
            }

            if comment:
                encoder = MultipartEncoder({
                    'form.widgets.comment': comment,
                    'form.buttons.button_checkin': 'Checkin',
                    '_authenticator': payload.get('csrf-token'),
                    })

                headers['Content-Type'] = encoder.content_type

                browser.open(
                    document,
                    view=payload.get('checkin-with-comment'),
                    headers=headers,
                    method='POST',
                    data=encoder.to_string(),
                    )
            else:
                browser.open(
                    document,
                    headers=headers,
                    view=payload.get('checkin-without-comment'),
                    send_authenticator=True,
                    )

        self.assert_journal_entry(
            document,
            DOCUMENT_CHECKED_IN,
            u'Document checked in',
            )

        journal_comments = get_journal_entry(document).get('comments')
        if comment:
            self.assertTrue(journal_comments)
        else:
            self.assertFalse(journal_comments)

        self.assertEquals(200, browser.status_code)
