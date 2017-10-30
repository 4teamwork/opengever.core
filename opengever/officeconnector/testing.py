from opengever.journal.handlers import DOCUMENT_CHECKED_OUT
from opengever.testing import IntegrationTestCase
from plone import api
from time import time
from xml.etree import ElementTree as ET
from zope.component import getMultiAdapter
import json
import jwt


class OCIntegrationTestCase(IntegrationTestCase):
    """Extend IntegrationTestCase with Office Connector specific helpers."""

    def fetch_document_attach_oc_url(self, browser, document):
        browser.raise_http_errors = False

        headers = {
            'Accept': 'application/json',
        }

        return browser.open(document, headers=headers, view='officeconnector_attach_url').json.get('url', None)

    def fetch_document_checkout_oc_url(self, browser, document):
        browser.raise_http_errors = False

        headers = {
            'Accept': 'application/json',
        }

        return browser.open(document, headers=headers, view='officeconnector_checkout_url').json.get('url', None)

    def fetch_dossier_bcc(self, browser, dossier):
        browser.raise_http_errors = False

        headers = {
            'Accept': 'application/json',
        }

        return browser.open(dossier, headers=headers, view='attributes').json.get('email', None)

    def fetch_dossier_multiattach_oc_url(self, browser, dossier, documents, bcc):
        browser.raise_http_errors = False

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        data = dict(
            bcc=bcc,
            documents=json.dumps(['/'.join(doc.getPhysicalPath()) for doc in documents]),
            )

        return browser.open(self.portal, method='POST', headers=headers, data=data, view='officeconnector_attach_url').json.get('url', None)

    def validate_checkout_token(self, oc_url):
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, verify=False)
        self.assertEquals('checkout', token.get('action', None))

        url = token.get('url', None)
        self.assertTrue(url)

        documents = token.get('documents', [])
        self.assertEquals(1, len(documents))
        self.assertEquals(api.content.get_uuid(self.document), documents[0])

        user = token.get('sub', None)
        self.assertEquals(self.regular_user.id, user)

        expiry = int(token.get('exp', 0))
        self.assertTrue(int(time()) < expiry)

        return (raw_token, token, )

    def fetch_document_checkout_payloads(self, browser, token):
        browser.raise_http_errors = False

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        data = json.dumps(token.get('documents', []))

        return browser.open(self.portal, method='POST', data=data, headers=headers, view='oc_checkout').json

    def validate_checkout_payload(self, payload, document):
        checkin_with_comment = payload.get('checkin-with-comment', None)
        self.assertTrue(checkin_with_comment)
        self.assertEquals('@@checkin_document', checkin_with_comment)

        checkin_without_comment = payload.get('checkin-without-comment', None)
        self.assertTrue(checkin_without_comment)
        self.assertEquals('checkin_without_comment', checkin_without_comment)

        checkout = payload.get('checkout', None)
        self.assertTrue(checkout)
        self.assertEquals('@@checkout_documents', checkout)

        content_type = payload.get('content-type', None)
        self.assertTrue(content_type)
        self.assertEquals(document.content_type(), content_type)

        csrf_token = payload.get('csrf-token', None)
        self.assertTrue(csrf_token)

        document_url = payload.get('document-url', None)
        self.assertTrue(document_url)
        self.assertEquals(document.absolute_url(), document_url)

        download = payload.get('download', None)
        self.assertTrue(download)
        self.assertEquals('download', download)

        filename = payload.get('filename', None)
        self.assertTrue(filename)
        self.assertEquals(document.get_filename(), filename)

        upload_api = payload.get('upload-api', None)
        self.assertFalse(upload_api)

        upload_form = payload.get('upload-form', None)
        self.assertTrue(upload_form)
        self.assertEquals('file_upload', upload_form)

    def checkout_document(self, browser, token, payload, document):
        """Logs out, uses the JWT to check out the document and logs back in."""
        self.assertFalse(document.checked_out_by())

        current_user = api.user.get_current()
        browser.logout()

        browser.raise_http_errors = False

        headers = {
            'Accept': 'text/html',
            'Authorization': ' '.join(('Bearer', token, )),
        }

        browser.open(document, headers=headers, view=payload.get('checkout'), send_authenticator=True)

        self.login(current_user, browser)
        self.assertEquals(current_user.id, document.checked_out_by())
        self.assert_journal_entry(document, DOCUMENT_CHECKED_OUT, u'Document checked out')

    def lock_document(self, browser, token, document):
        """Logs out, uses the JWT to WebDAV lock the document and logs back in."""
        lock_manager = getMultiAdapter((document, self.request), name='plone_lock_info')
        self.assertFalse(lock_manager.is_locked())

        current_user = api.user.get_current()
        browser.logout()

        browser.raise_http_errors = False

        headers = {
            'Authorization': ' '.join(('Bearer', token, )),
            'Content-Type': 'text/xml; charset="utf-8"',
            'Depth': '0',
            'Timeout': 'Infinite, Second-4100000000',
            }

        data = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<d:lockinfo xmlns:d="DAV:">\n'
            '  <d:lockscope><d:exclusive/></d:lockscope>\n'
            '  <d:locktype><d:write/></d:locktype>\n'
            '  <d:owner>\n'
            '  <d:href>Office Connector</d:href>\n'
            '  </d:owner>\n'
            '</d:lockinfo>'
            )

        browser.webdav('LOCK', document, headers=headers, data=data)
        self.assertEquals(200, browser.status_code)
        self.assertTrue(lock_manager.is_locked())

        try:
            lock_token = ET.fromstring(browser.contents).find('./d:lockdiscovery/d:activelock/d:locktoken/', {'d': 'DAV:'}).text
        except ET.ParseError:
            lock_token = None
        self.assertTrue(lock_token)

        self.login(current_user, browser)

        return lock_token

    def download_document(self, browser, token, payload, document):
        current_user = api.user.get_current()
        browser.logout()

        browser.raise_http_errors = False

        headers = {
            'Accept': document.content_type(),
            'Authorization': ' '.join(('Bearer', token, )),
        }

        file_contents = browser.open(document, headers=headers, view=payload.get('download')).contents
        self.assertTrue(file_contents)

        self.login(current_user, browser)

        return file_contents

    def upload_document(self, browser, token, payload, document, new_file):
        import pdb; pdb.set_trace()
        current_user = api.user.get_current()
        browser.logout()

        headers = {
            'Accept': 'text/html',
            'Authorization': ' '.join(('Bearer', token, )),
        }

        data = {
            'form.widgets.file.action': 'replace',
            'form.buttons.upload': 'oc-file-upload',
            }

        # files = {
        #     'form.widgets.file': (
        #         document.basename,
        #         new_file,
        #         document.content_type,
        #     )
        # }
        import pdb; pdb.set_trace()
        browser.open(document, headers=headers, view=payload.get('upload-form')).forms
        browser.raise_http_errors = False
        browser.open(document, headers=headers, method='POST', data=data, view=payload.get('upload-form'), send_authenticator=True)
        self.login(current_user, browser)

    def unlock_document(self, browser, document):
        pass

    def checkin_document(self, browser, document, comment=None):
        pass
