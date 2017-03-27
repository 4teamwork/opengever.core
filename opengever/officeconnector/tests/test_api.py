from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.interfaces import IEmailAddress
from ftw.testbrowser import browsing
from opengever.api.testing import RelativeSession
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ZSERVER_TESTING
from opengever.officeconnector.interfaces import IOfficeConnectorSettings
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD

import json
import jwt
import transaction


class TestOfficeconnectorAPI(FunctionalTestCase):
    """Simulate an OfficeConnector client."""

    layer = OPENGEVER_FUNCTIONAL_ZSERVER_TESTING

    def setUp(self):
        super(TestOfficeconnectorAPI, self).setUp()
        self.portal = self.layer['portal']

        self.api = RelativeSession(self.portal.absolute_url())
        self.api.headers.update({'Accept': 'application/json'})
        self.api.auth = (TEST_USER_NAME, TEST_USER_PASSWORD)

        self.original_file_content = u'original file content'
        self.modified_file_content = u'modified file content'
        self.test_comment = 'Test Comment'

        self.repo = create(Builder('repository_root')
                           .having(id='ordnungssystem',
                                   title_de=u'Ordnungssystem',
                                   title_fr=u'Syst\xe8me de classement'))

        self.repofolder = create(Builder('repository')
                                 .within(self.repo)
                                 .having(title_de=u'Ordnungsposition',
                                         title_fr=u'Position'))

        self.open_dossier = create(Builder('dossier')
                                   .within(self.repofolder)
                                   .titled(u'Mein Dossier'))

        self.resolved_dossier = create(Builder('dossier')
                                       .within(self.repofolder)
                                       .titled(u'Abgeschlossenes Dossier')
                                       .in_state('dossier-state-resolved'))

        self.inactive_dossier = create(Builder('dossier')
                                       .within(self.repofolder)
                                       .titled(u'Inaktives Dossier')
                                       .in_state('dossier-state-inactive'))

        # We rely on the creation order of these documents for the tests!
        # ZServer craps out if you have non-ascii in the document titles!
        self.doc_without_file_wf_open = create(Builder('document')
                                               .titled(u'docu-1')
                                               .within(self.open_dossier))

        self.doc_with_file_wf_open = create(Builder('document')
                                            .titled(u'docu-2')
                                            .within(self.open_dossier)
                                            .attach_file_containing(
                                                self.original_file_content))

        self.doc_with_file_wf_open_second = create(Builder('document')
                                                   .titled(u'docu-3')
                                                   .within(self.open_dossier)
                                                   .attach_file_containing(
                                                   self.original_file_content))

        self.doc_without_file_wf_resolved = create(Builder('document')
                                                   .titled(u'docu-4')
                                                   .within(
                                                       self.resolved_dossier))

        self.doc_with_file_wf_resolved = create(Builder('document')
                                                .titled(u'docu-5')
                                                .within(self.resolved_dossier)
                                                .attach_file_containing(self.original_file_content))  # noqa

        self.doc_without_file_wf_inactive = create(Builder('document')
                                                   .titled(u'docu-6')
                                                   .within(
                                                       self.inactive_dossier))

        self.doc_with_file_wf_inactive = create(Builder('document')
                                                .titled(u'docu-7')
                                                .within(self.inactive_dossier)
                                                .attach_file_containing(self.original_file_content))  # noqa

        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')
        lang_tool.supported_langs = ['fr-ch', 'de-ch']

        transaction.commit()

    def enable_attach_to_outlook(self):
        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeConnectorSettings)
        transaction.commit()

    def enable_oc_checkout(self):
        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)
        transaction.commit()

    def get_oc_url_response(self, document, action):
        # The requests based api tester expects its paths to start from the
        # site root so we strip out the site id from the physical path.
        site_id = api.portal.get().id
        path_segments = [s for s in document.getPhysicalPath() if s != site_id]
        path_segments.append('officeconnector_{}_url'.format(action))
        return self.api.get('/'.join(path_segments))

    def get_oc_url_response_status(self, document, action):
        return self.get_oc_url_response(document, action).status_code

    def get_oc_url_payload(self, document, action):
        return self.get_oc_url_response(document, action).json()

    def get_oc_url_jwt(self, document, action):
        payload = self.get_oc_url_response(document, action).json()
        return jwt.decode(payload['url'].split(':')[-1], verify=False)

    def get_oc_payload_response(self, document, action):
        return self.api.get(
            '/oc_{}/'.format(action)
            + api.content.get_uuid(document))

    def get_oc_payload_response_status(self, document, action):
        return self.get_oc_payload_response(document, action).status_code

    def get_oc_payload_json(self, document, action):
        return self.get_oc_payload_response(document, action).json()

    def checkout_document(self, payload):
        self.api.headers.update({'Accept': 'text/html'})
        self.api.get('/'.join((payload['document-url'], payload['checkout'])) + '?_authenticator={}'.format(payload['csrf-token'])) # noqa

    def upload_document(self, payload, modified_file_content):
        self.api.headers.update({'Accept': 'text/html'})
        data = {
            'form.widgets.file.action': 'replace',
            'form.buttons.save': 'Save',
            '_authenticator': payload['csrf-token'],
            }

        # The DATA in the file tuple needs to be seekable
        # The order within the file tuple matters if the file is not a file
        files = {
            'form.widgets.file': (
                payload['filename'],
                str(modified_file_content),
                payload['content-type'],
                ),
            }

        self.api.post(
            '/'.join((payload['document-url'], payload['upload-form'])),
            data=data,
            files=files,
            )

    def checkin_with_comment(self, payload, comment):
        self.api.headers.update({'Accept': 'text/html'})

        data = {
            'form.widgets.comment': self.test_comment,
            'form.buttons.button_checkin': 'Checkin',
            '_authenticator': payload['csrf-token'],
            }

        self.api.post(
            '/'.join((payload['document-url'], payload['checkin-with-comment'])),  # noqa
            data=data,
            )

    def test_returns_404_when_feature_disabled(self):
        self.assertEquals(404, self.get_oc_url_response_status(self.doc_without_file_wf_open, 'attach')) # noqa
        self.assertEquals(404, self.get_oc_url_response_status(self.doc_with_file_wf_open, 'attach')) # noqa
        self.assertEquals(404, self.get_oc_url_response_status(self.doc_without_file_wf_open, 'checkout')) # noqa
        self.assertEquals(404, self.get_oc_url_response_status(self.doc_with_file_wf_open, 'checkout')) # noqa

    def test_attach_to_outlook_url_without_file(self):
        self.enable_attach_to_outlook()
        self.assertEquals(404, self.get_oc_url_response_status(self.doc_without_file_wf_open, 'attach')) # noqa

    def test_attach_to_outlook_payload_without_file(self):
        self.enable_attach_to_outlook()
        self.assertEquals(404, self.get_oc_payload_response_status(self.doc_without_file_wf_open, 'attach')) # noqa

    def test_attach_to_outlook_url_with_file(self):
        self.enable_attach_to_outlook()
        self.assertEquals(200, self.get_oc_url_response_status(self.doc_with_file_wf_open, 'attach')) # noqa

        payload = self.get_oc_url_payload(self.doc_with_file_wf_open, 'attach') # noqa
        self.assertIn('url', payload)

        token = self.get_oc_url_jwt(self.doc_with_file_wf_open, 'attach') # noqa
        self.assertIn('url', token)
        self.assertNotIn('documents', token)
        self.assertIn('/oc_attach', token['url'])
        self.assertEquals(token['action'], 'attach')
        self.assertEquals(TEST_USER_ID, token['sub'])

    @browsing
    def test_attach_to_outlook_payload_with_file_and_open_dossier(self, browser):  # noqa
        self.enable_attach_to_outlook()
        token = self.get_oc_url_jwt(self.doc_with_file_wf_open, 'attach')

        self.assertNotIn('documents', token)

        # Test we can actually fetch an action payload based on the URL JWT
        response = self.api.get(token['url'])
        self.assertEquals(200, response.status_code)

        payload = response.json()

        self.assertIn('bcc', payload)
        bcc = IEmailAddress(
            self.request).get_email_for_object(self.open_dossier)
        self.assertEquals(bcc, payload['bcc'])

        # Test there is also a journal entry from the attach action
        browser.login()
        browser.open(self.doc_with_file_wf_open, view='tabbedview_view-journal') # noqa
        journal_entry = browser.css('.listing').first.lists()[1]
        self.assertEquals(journal_entry[1], 'Dokument mit Mailprogramm versendet')  # noqa

    @browsing
    def test_attach_to_outlook_payload_with_file_and_resolved_dossier(self, browser):  # noqa
        self.enable_attach_to_outlook()
        token = self.get_oc_url_jwt(self.doc_with_file_wf_resolved, 'attach')

        self.assertNotIn('documents', token)

        # Test we can actually fetch an action payload based on the URL JWT
        response = self.api.get(token['url'])
        self.assertEquals(200, response.status_code)

        payload = response.json()

        self.assertNotIn('bcc', payload)

        # Test there is also a journal entry from the attach action
        browser.login()
        browser.open(self.doc_with_file_wf_resolved, view='tabbedview_view-journal') # noqa
        journal_entry = browser.css('.listing').first.lists()[1]
        self.assertEquals(journal_entry[1], 'Dokument mit Mailprogramm versendet')  # noqa

    @browsing
    def test_attach_to_outlook_payload_with_file_and_inactive_dossier(self, browser):  # noqa
        self.enable_attach_to_outlook()
        token = self.get_oc_url_jwt(self.doc_with_file_wf_inactive, 'attach')

        self.assertNotIn('documents', token)

        # Test we can actually fetch an action payload based on the URL JWT
        response = self.api.get(token['url'])
        self.assertEquals(200, response.status_code)

        payload = response.json()

        self.assertNotIn('bcc', payload)

        # Test there is also a journal entry from the attach action
        browser.login()
        browser.open(self.doc_with_file_wf_inactive, view='tabbedview_view-journal') # noqa
        journal_entry = browser.css('.listing').first.lists()[1]
        self.assertEquals(journal_entry[1], 'Dokument mit Mailprogramm versendet')  # noqa

    def test_attach_to_outlook_get(self):
        self.enable_attach_to_outlook()
        token = self.get_oc_url_jwt(self.doc_with_file_wf_open, 'attach') # noqa

        self.assertNotIn('documents', token)

        # Test we can actually fetch an action payload based on the URL JWT
        payload = self.api.get(token['url']).json()

        content_type = payload['content-type']
        filename = payload['filename']

        # Test fetching the indicated file
        self.api.headers.update({'Accept': content_type})
        response = self.api.get('/'.join((payload['document-url'], payload['download']))) # noqa

        self.assertEquals(200, response.status_code)
        self.assertEquals(response.headers['content-type'], content_type) # noqa
        self.assertEquals(response.headers['content-disposition'], 'attachment; filename="{}"'.format(filename)) # noqa

    @browsing
    def test_attach_to_outlook_post(self, browser):
        self.enable_attach_to_outlook()
        browser.login().open(
            self.open_dossier, view='tabbedview_view-documents')

        document_checkboxes = browser.css("input[type='checkbox']")
        self.assertEquals(3, len(document_checkboxes))

        document_paths = []
        for checkbox in document_checkboxes:
            document_paths.append(checkbox.get('value'))

        self.api.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            })

        token = self.api.post(
            '/officeconnector_attach_url',
            data=json.dumps(document_paths),
            ).json()

        payload = jwt.decode(token['url'].split(':')[-1], verify=False)

        self.assertEquals(2, len(payload['documents']))

        for document in payload['documents']:
            # Test we can actually fetch an action payload based on the URL JWT
            self.api.headers.update({'Accept': 'application/json'})
            action = self.api.get('/'.join((
                payload['url'],
                document,
                ))).json()

            content_type = action['content-type']
            filename = action['filename']

            # Test fetching the indicated file
            self.api.headers.update({'Accept': content_type})
            response = self.api.get('/'.join((action['document-url'], action['download']))) # noqa

            self.assertEquals(200, response.status_code)
            self.assertEquals(response.headers['content-type'], content_type) # noqa
            self.assertEquals(response.headers['content-disposition'], 'attachment; filename="{}"'.format(filename)) # noqa

    def test_document_checkout_url_without_file(self):
        self.enable_oc_checkout()
        self.assertEquals(404, self.get_oc_url_response_status(self.doc_without_file_wf_open, 'checkout')) # noqa

    def test_document_checkout_payload_without_file(self):
        self.enable_oc_checkout()
        self.assertEquals(404, self.get_oc_url_response_status(self.doc_without_file_wf_open, 'checkout')) # noqa

    def test_document_checkout_url_with_file(self):
        self.enable_oc_checkout()
        self.assertEquals(200, self.get_oc_url_response_status(self.doc_with_file_wf_open, 'checkout')) # noqa

        payload = self.get_oc_url_payload(self.doc_with_file_wf_open, 'checkout') # noqa
        self.assertIn('url', payload)

        token = self.get_oc_url_jwt(self.doc_with_file_wf_open, 'checkout') # noqa

        self.assertIn('url', token)
        self.assertIn('/oc_checkout', token['url'])
        self.assertNotIn('documents', token)
        self.assertEquals(token['action'], 'checkout')
        self.assertEquals(TEST_USER_ID, token['sub'])

    def test_document_checkout_payload_with_file(self):
        self.enable_oc_checkout()
        token = self.get_oc_url_jwt(self.doc_with_file_wf_open, 'checkout') # noqa

        self.assertNotIn('documents', token)
        # Test we can actually fetch an action payload based on the URL JWT
        response = self.api.get(token['url'])
        self.assertEquals(200, response.status_code)

        payload = response.json()
        self.assertIn('csrf-token', payload)
        self.assertIn('download', payload)
        self.assertEquals(self.doc_with_file_wf_open.file.contentType, payload['content-type']) # noqa
        self.assertEquals(self.doc_with_file_wf_open.absolute_url(), payload['document-url']) # noqa
        self.assertEquals(self.doc_with_file_wf_open.get_filename(), payload['filename']) # noqa

    @browsing
    def test_document_checkout(self, browser):
        # Enable the OC checkout feature
        self.enable_oc_checkout()

        # Grab the OC URL
        token = self.get_oc_url_jwt(self.doc_with_file_wf_open, 'checkout') # noqa

        self.assertNotIn('documents', token)

        # Grab the action payload based on the OC URL
        payload = self.api.get(token['url']).json()

        # Test fetching the indicated file
        self.api.headers.update({'Accept': payload['content-type']})
        response = self.api.get('/'.join((payload['document-url'], payload['download']))) # noqa

        self.assertEquals(200, response.status_code)
        self.assertEquals(response.headers['content-type'], payload['content-type']) # noqa
        self.assertEquals(response.headers['content-disposition'], 'attachment; filename="{}"'.format(payload['filename'])) # noqa
        self.assertEquals(response.content, self.original_file_content)

        # Test we can perform a checkout based on the action payload
        self.checkout_document(payload)

        browser.login()
        self.assertTrue(browser.open(self.doc_with_file_wf_open).css('.checked_out_viewlet')) # noqa

        # Test there is also a journal entry from the checkout
        browser.open(self.doc_with_file_wf_open, view='tabbedview_view-journal') # noqa
        journal_entry = browser.css('.listing').first.lists()[1]
        self.assertEquals(journal_entry[1], 'Dokument ausgecheckt')

    @browsing
    def test_document_checkin_without_comment(self, browser):
        # Enable the OC checkout feature
        self.enable_oc_checkout()

        # Grab the OC URL
        token = self.get_oc_url_jwt(self.doc_with_file_wf_open, 'checkout') # noqa

        self.assertNotIn('documents', token)

        # Grab the action payload based on the OC URL
        payload = self.api.get(token['url']).json()

        # Checkout the document based on the action payload
        self.checkout_document(payload)

        # Test we can upload a new version of the file
        self.upload_document(payload, self.modified_file_content)

        # Test the uploaded new file is now properly the working copy
        self.api.headers.update({'Accept': payload['content-type']})
        response = self.api.get('/'.join((payload['document-url'], payload['download']))) # noqa

        self.assertEquals(response.content, self.modified_file_content)

        # Check the document in without a comment
        self.api.get('/'.join((payload['document-url'], payload['checkin-without-comment'])) + '?_authenticator={}'.format(payload['csrf-token'])) # noqa

        # Test the journal entry from the commentless checkin
        browser.login()
        browser.open(self.doc_with_file_wf_open, view='tabbedview_view-journal') # noqa
        journal_entry = browser.css('.listing').first.lists()[1]

        self.assertEquals(journal_entry[1], 'Dokument eingecheckt')

        # Test the checked in version is the uploaded version
        self.api.headers.update({'Accept': payload['content-type']})
        response = self.api.get('/'.join((payload['document-url'], 'download_file_version'))) # noqa

        self.assertEquals(response.content, self.modified_file_content)

    @browsing
    def test_document_checkin_with_comment(self, browser):
        # Enable the OC checkout feature
        self.enable_oc_checkout()

        # Grab the OC URL
        token = self.get_oc_url_jwt(self.doc_with_file_wf_open, 'checkout') # noqa

        self.assertNotIn('documents', token)

        # Grab the action payload based on the OC URL
        payload = self.api.get(token['url']).json()

        # Perform a checkout based on the action payload
        self.checkout_document(payload)

        # Upload a new version of the file
        self.upload_document(payload, self.modified_file_content)

        # Check the document in with a comment
        self.checkin_with_comment(payload, self.test_comment)

        # Test the journal entries from the checkin with a comment
        browser.login()
        browser.open(self.doc_with_file_wf_open, view='tabbedview_view-journal') # noqa
        journal_entry = browser.css('.listing').first.lists()[1]

        self.assertEquals(journal_entry[1], 'Dokument eingecheckt')
        self.assertEquals(journal_entry[3], self.test_comment)

        # Test the uploaded new file is now properly the latest version
        self.api.headers.update({'Accept': payload['content-type']})
        response = self.api.get('/'.join((payload['document-url'], payload['download']))) # noqa

        self.assertEquals(response.content, self.modified_file_content)
