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

import jwt
import requests
import transaction


class TestOfficeconnectorAPI(FunctionalTestCase):
    """Simulate an OfficeConnector client."""

    layer = OPENGEVER_FUNCTIONAL_ZSERVER_TESTING

    def setUp(self):
        super(TestOfficeconnectorAPI, self).setUp()
        self.portal = self.layer['portal']

        self.api = RelativeSession(self.portal.absolute_url())
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

        self.open_subdossier = create(Builder('dossier')
                                      .within(self.open_dossier)
                                      .titled(u'Mein Subdossier'))

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

        self.mail_with_file_wf_open = create(Builder('mail')
                                             .titled(u'Mail 2')
                                             .within(self.open_dossier)
                                             .with_dummy_message())

        self.doc_with_file_wf_open_second = create(Builder('document')
                                                   .titled(u'docu-3')
                                                   .within(self.open_dossier)
                                                   .attach_file_containing(
                                                   self.original_file_content))

        self.doc_with_file_wf_open_second = create(Builder('document')
                                                   .titled(u'docu-4')
                                                   .within(
                                                       self.open_subdossier)
                                                   .attach_file_containing(
                                                   self.original_file_content))

        self.doc_without_file_wf_resolved = create(Builder('document')
                                                   .titled(u'docu-5')
                                                   .within(
                                                       self.resolved_dossier))

        self.doc_with_file_wf_resolved = create(Builder('document')
                                                .titled(u'docu-6')
                                                .within(self.resolved_dossier)
                                                .attach_file_containing(self.original_file_content))  # noqa

        self.doc_without_file_wf_inactive = create(Builder('document')
                                                   .titled(u'docu-7')
                                                   .within(
                                                       self.inactive_dossier))

        self.doc_with_file_wf_inactive = create(Builder('document')
                                                .titled(u'docu-8')
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
        path = '/'.join(path_segments)

        self.api.headers.update({
            'Accept': 'application/json',
        })

        response = self.api.get(path)
        return response

    def get_oc_url_response_status(self, document, action):
        return self.get_oc_url_response(document, action).status_code

    def get_oc_url_payload(self, document, action):
        return self.get_oc_url_response(document, action).json()

    def get_oc_url_jwt(self, document, action):
        response = self.get_oc_url_response(document, action)
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertIn('url', payload)
        return payload['url'].split(':')[-1]

    def get_oc_url_jwt_decoded(self, document, action):
        return jwt.decode(self.get_oc_url_jwt(document, action), verify=False)

    def get_oc_payload_response(self, payload):
        self.api.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            })

        response = self.api.post(
            '/oc_{}'.format(payload['action']),
            json=payload['documents'],
            )

        return response

    def get_oc_payload_response_status(self, token):
        return self.get_oc_payload_response(jwt).status_code

    def get_oc_payload_json(self, document, action):
        return self.get_oc_payload_response(document, action).json()

    def checkout_document(self, payload):
        self.api.headers.update({'Accept': 'text/html'})

        self.api.get(
            '/'.join((payload['document-url'],
                      payload['checkout'])) + '?_authenticator={}'
            .format(payload['csrf-token']),
            )

    def upload_document(self, payload, modified_file_content):
        self.api.headers.update({
            'Accept': 'text/html',
            })

        # Let requests handle the Content-Type as there is the boundary too
        del self.api.headers['Content-Type']

        data = {
            'form.widgets.file.action': 'replace',
            'form.buttons.upload': 'oc-file-upload',
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

        response = self.api.post(
            '/'.join((payload['document-url'], payload['upload-form'])),
            data=data,
            files=files,
            )

        # Ensure the upload was succesful
        self.assertEqual(204, response.status_code)

    def checkin_with_comment(self, payload, comment):
        self.api.headers.update({'Accept': 'text/html'})

        data = {
            'form.widgets.comment': self.test_comment,
            'form.buttons.button_checkin': 'Checkin',
            '_authenticator': payload['csrf-token'],
            }

        self.api.post(
            '/'.join((payload['document-url'],
                      payload['checkin-with-comment'],
                      )),
            data=data,
            )

    def test_returns_404_when_feature_disabled(self):
        self.assertEqual(404, self.get_oc_url_response_status(
            self.doc_without_file_wf_open, 'attach'))

        self.assertEqual(404, self.get_oc_url_response_status(
            self.doc_with_file_wf_open, 'attach'))

        self.assertEqual(404, self.get_oc_url_response_status(
            self.doc_without_file_wf_open, 'checkout'))

        self.assertEqual(404, self.get_oc_url_response_status(
            self.doc_with_file_wf_open, 'checkout'))

    def test_attach_to_outlook_url_without_file(self):
        self.enable_attach_to_outlook()
        self.assertEqual(404, self.get_oc_url_response_status(
            self.doc_without_file_wf_open, 'attach'))

    def test_attach_to_outlook_url_with_file(self):
        self.enable_attach_to_outlook()
        self.assertEqual(200, self.get_oc_url_response_status(
            self.doc_with_file_wf_open, 'attach'))

        payload = self.get_oc_url_payload(self.doc_with_file_wf_open, 'attach')
        self.assertIn('url', payload)

        token = self.get_oc_url_jwt_decoded(
            self.doc_with_file_wf_open, 'attach')
        self.assertIn('url', token)
        self.assertIn('documents', token)
        self.assertIn(api.content.get_uuid(
            self.doc_with_file_wf_open), token['documents'])
        self.assertIn('/oc_attach', token['url'])
        self.assertEqual(token['action'], 'attach')
        self.assertEqual(TEST_USER_ID, token['sub'])

    @browsing
    def test_attach_to_outlook_payload_with_file_and_open_dossier(self, browser):  # noqa
        self.enable_attach_to_outlook()
        payload = self.get_oc_url_jwt_decoded(
            self.doc_with_file_wf_open, 'attach')

        self.assertIn('documents', payload)
        self.assertIn(api.content.get_uuid(
            self.doc_with_file_wf_open), payload['documents'])

        self.assertIn('action', payload)
        self.assertEqual('attach', payload['action'])

        # Test we can actually fetch an action payload based on the JWT payload
        response = self.get_oc_payload_response(payload)
        self.assertEqual(200, response.status_code)

        payload = response.json()
        self.assertEqual(1, len(payload))
        payload = payload[0]

        self.assertIn('bcc', payload)
        bcc = IEmailAddress(
            self.request).get_email_for_object(self.open_dossier)
        self.assertEqual(bcc, payload['bcc'])

        self.assertIn('title', payload)
        self.assertEqual(
            self.doc_with_file_wf_open.title_or_id(), payload['title'])

        # Test there is also a journal entry from the attach action
        browser.login()
        browser.open(
            self.doc_with_file_wf_open, view='tabbedview_view-journal')
        journal_entry = browser.css('.listing').first.lists()[1]
        self.assertEqual(
            journal_entry[1], 'Dokument mit Mailprogramm versendet')

        # Test there is also a journal entry in the dossier
        browser.login()
        browser.open(self.open_dossier, view='tabbedview_view-journal')
        journal_entry = browser.css('.listing').first.lists()[1]
        self.assertEqual(
            journal_entry[1], 'Dokument im Dossier mit Mailprogramm versendet')

    @browsing
    def test_attach_to_outlook_payload_with_file_and_resolved_dossier(self, browser):  # noqa
        self.enable_attach_to_outlook()
        payload = self.get_oc_url_jwt_decoded(
            self.doc_with_file_wf_resolved, 'attach')

        self.assertIn('documents', payload)

        self.assertIn('action', payload)
        self.assertEqual('attach', payload['action'])

        # Test we can actually fetch an action payload based on the JWT payload
        response = self.get_oc_payload_response(payload)
        self.assertEqual(200, response.status_code)

        payload = response.json()
        self.assertEqual(1, len(payload))
        payload = payload[0]

        self.assertNotIn('bcc', payload)

        self.assertIn('title', payload)
        self.assertEqual(
            self.doc_with_file_wf_resolved.title_or_id(), payload['title'])

        # Test there is also a journal entry from the attach action
        browser.login()
        browser.open(
            self.doc_with_file_wf_resolved, view='tabbedview_view-journal')
        journal_entry = browser.css('.listing').first.lists()[1]
        self.assertEqual(
            journal_entry[1], 'Dokument mit Mailprogramm versendet')

        # Test there is also a journal entry in the dossier
        browser.login()
        browser.open(self.resolved_dossier, view='tabbedview_view-journal')
        journal_entry = browser.css('.listing').first.lists()[1]
        self.assertEqual(
            journal_entry[1], 'Dokument im Dossier mit Mailprogramm versendet')

    @browsing
    def test_attach_to_outlook_payload_with_file_and_inactive_dossier(self, browser):  # noqa
        self.enable_attach_to_outlook()
        payload = self.get_oc_url_jwt_decoded(
            self.doc_with_file_wf_inactive, 'attach')

        self.assertIn('documents', payload)

        # Test we can actually fetch an action payload based on the JWT payload
        response = self.get_oc_payload_response(payload)
        self.assertEqual(200, response.status_code)

        payload = response.json()
        self.assertEqual(1, len(payload))
        payload = payload[0]

        self.assertNotIn('bcc', payload)

        self.assertIn('title', payload)
        self.assertEqual(
            self.doc_with_file_wf_inactive.title_or_id(), payload['title'])

        # Test there is also a journal entry from the attach action
        browser.login()
        browser.open(
            self.doc_with_file_wf_inactive, view='tabbedview_view-journal')
        journal_entry = browser.css('.listing').first.lists()[1]
        self.assertEqual(
            journal_entry[1], 'Dokument mit Mailprogramm versendet')

        # Test there is also a journal entry in the dossier
        browser.login()
        browser.open(self.inactive_dossier, view='tabbedview_view-journal')
        journal_entry = browser.css('.listing').first.lists()[1]
        self.assertEqual(
            journal_entry[1], 'Dokument im Dossier mit Mailprogramm versendet')

    def test_attach_to_outlook_one(self):
        self.enable_attach_to_outlook()
        payload = self.get_oc_url_jwt_decoded(
            self.doc_with_file_wf_open, 'attach')

        self.assertIn('documents', payload)

        # Test we can actually fetch an action payload based on the JWT payload
        response = self.get_oc_payload_response(payload)
        self.assertEqual(200, response.status_code)

        payload = response.json()
        self.assertEqual(1, len(payload))
        payload = payload[0]

        content_type = payload['content-type']
        filename = payload['filename']

        # Test fetching the indicated file
        self.api.headers.update({'Accept': content_type})
        response = self.api.get(
            '/'.join((payload['document-url'], payload['download'])))

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['content-type'], content_type) # noqa
        self.assertEqual(
            response.headers['content-disposition'],
            'attachment; filename="{}"'.format(filename))

    @browsing
    def test_attach_to_outlook_multiple(self, browser):
        self.enable_attach_to_outlook()
        browser.login().open(
            self.open_dossier, view='tabbedview_view-documents')

        document_checkboxes = browser.css("input[type='checkbox']")
        self.assertEqual(5, len(document_checkboxes))

        self.api.headers.update({
            'Accept': 'application/json',
            })

        site_id = api.portal.get().id
        path_segments = [
            s for s
            in self.open_dossier.getPhysicalPath()
            if s != site_id
            ]
        path_segments.append('attributes')
        path = '/'.join(path_segments)

        bcc = self.api.get(path).json()['email']

        document_paths = []
        for checkbox in document_checkboxes:
            document_paths.append(checkbox.get('value'))

        self.api.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            })

        token = self.api.post(
            '/officeconnector_attach_url',
            json=dict(
                documents=document_paths,
                bcc=bcc,
                ),
            ).json()

        payload = jwt.decode(token['url'].split(':')[-1], verify=False)

        # Test we actually get the bcc parametre back for OC to handle
        self.assertIn('bcc', payload)
        self.assertIn(bcc, payload['bcc'])

        # Test we can actually fetch an action payload based on the JWT payload
        response = self.get_oc_payload_response(payload)
        self.assertEqual(200, response.status_code)

        payload = response.json()
        self.assertEqual(4, len(payload))

        for document in payload:
            # Test there is also a journal entry from the attach action
            doc_path = '/' + '/'.join(document['document-url'].split('/')[4:])
            doc = api.content.get(doc_path)
            browser.login()
            browser.open(doc, view='tabbedview_view-journal')
            journal_entry = browser.css('.listing').first.lists()[1]
            self.assertEqual(
                journal_entry[1], 'Dokument mit Mailprogramm versendet')

            # Test there is also a journal entry in the dossier
            browser.login()
            browser.open(
                doc.get_parent_dossier(), view='tabbedview_view-journal')
            journal_entry = browser.css('.listing').first.lists()[1]
            self.assertEqual(
                journal_entry[1],
                'Dokument im Dossier mit Mailprogramm versendet')

            # Test the documents are logged in the same dossier journal entry
            self.assertIn(doc.title_or_id(), journal_entry[4])

            # Test fetching the indicated file
            content_type = document['content-type']
            filename = document['filename']

            self.api.headers.update({'Accept': content_type})
            response = self.api.get(
                '/'.join((document['document-url'], document['download'])))

            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['content-type'], content_type)
            self.assertEqual(
                response.headers['content-disposition'],
                'attachment; filename="{}"'.format(filename))

    def test_attach_mail_to_outlook_uses_original_message(self):
        mail = create(Builder('mail')
                      .titled(u'Mail')
                      .within(self.open_dossier)
                      .with_dummy_message()
                      .with_dummy_original_message())

        response = requests.post(
            '{}/oc_attach'.format(self.portal.absolute_url()),
            headers={'Accept': 'application/json'},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
            json=[mail.UID()],
        )

        data = response.json()[0]
        self.assertEqual('application/vnd.ms-outlook', data.get('content-type'))
        self.assertEqual('dummy.msg', data.get('filename'))
        self.assertEqual('@@download/original_message', data.get('download'))

    def test_attach_mail_to_outlook_uses_message_if_no_original_message_is_available(self):
        mail = create(Builder('mail')
                      .titled(u'Mail')
                      .within(self.open_dossier)
                      .with_dummy_message())

        response = requests.post(
            '{}/oc_attach'.format(self.portal.absolute_url()),
            headers={'Accept': 'application/json'},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
            json=[mail.UID()],
        )

        data = response.json()[0]
        self.assertEqual('message/rfc822', data.get('content-type'))
        self.assertEqual('mail.eml', data.get('filename'))
        self.assertEqual('download', data.get('download'))

    def test_document_checkout_url_without_file(self):
        self.enable_oc_checkout()
        self.assertEqual(404, self.get_oc_url_response_status(
            self.doc_without_file_wf_open, 'checkout'))

    def test_document_checkout_payload_without_file(self):
        self.enable_oc_checkout()
        self.assertEqual(404, self.get_oc_url_response_status(
            self.doc_without_file_wf_open, 'checkout'))

    def test_document_checkout_url_with_file(self):
        self.enable_oc_checkout()
        self.assertEqual(200, self.get_oc_url_response_status(
            self.doc_with_file_wf_open, 'checkout'))

        payload = self.get_oc_url_payload(
            self.doc_with_file_wf_open, 'checkout')
        self.assertIn('url', payload)

        token = self.get_oc_url_jwt_decoded(
            self.doc_with_file_wf_open, 'checkout')

        self.assertIn('url', token)
        self.assertIn('/oc_checkout', token['url'])
        self.assertIn('documents', token)
        self.assertEqual(token['action'], 'checkout')
        self.assertEqual(TEST_USER_ID, token['sub'])

    def test_document_checkout_payload_with_file(self):
        self.enable_oc_checkout()
        payload = self.get_oc_url_jwt_decoded(
            self.doc_with_file_wf_open, 'checkout')

        self.assertIn('documents', payload)
        # Test we can actually fetch an action payload based on the JWT payload
        response = self.get_oc_payload_response(payload)
        self.assertEqual(200, response.status_code)

        payload = response.json()
        self.assertEqual(1, len(payload))
        payload = payload[0]

        self.assertIn('csrf-token', payload)
        self.assertIn('download', payload)
        self.assertEqual(
            self.doc_with_file_wf_open.file.contentType,
            payload['content-type'])
        self.assertEqual(
            self.doc_with_file_wf_open.absolute_url(),
            payload['document-url'])
        self.assertEqual(
            self.doc_with_file_wf_open.get_filename(), payload['filename'])

    @browsing
    def test_document_checkout(self, browser):
        # Enable the OC checkout feature
        self.enable_oc_checkout()

        # Grab the OC URL
        payload = self.get_oc_url_jwt_decoded(
            self.doc_with_file_wf_open, 'checkout')

        self.assertIn('documents', payload)

        # Test we can actually fetch an action payload based on the JWT payload
        response = self.get_oc_payload_response(payload)
        self.assertEqual(200, response.status_code)

        payload = response.json()
        self.assertEqual(1, len(payload))
        payload = payload[0]

        # Test fetching the indicated file
        self.api.headers.update({'Accept': payload['content-type']})
        response = self.api.get(
            '/'.join((payload['document-url'], payload['download'])))

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            response.headers['content-type'], payload['content-type'])
        self.assertEqual(
            response.headers['content-disposition'],
            'attachment; filename="{}"'.format(payload['filename']))
        self.assertEqual(response.content, self.original_file_content)

        # Test we can perform a checkout based on the action payload
        self.checkout_document(payload)

        browser.login()
        self.assertTrue(browser.open(self.doc_with_file_wf_open)
                        .css('.checked_out_viewlet'))

        # Test there is also a journal entry from the checkout
        browser.open(
            self.doc_with_file_wf_open, view='tabbedview_view-journal')
        journal_entry = browser.css('.listing').first.lists()[1]
        self.assertEqual(journal_entry[1], 'Dokument ausgecheckt')

    @browsing
    def test_document_checkin_without_comment(self, browser):
        # Enable the OC checkout feature
        self.enable_oc_checkout()

        # Grab the OC URL
        payload = self.get_oc_url_jwt_decoded(
            self.doc_with_file_wf_open, 'checkout')

        self.assertIn('documents', payload)

        # Test we can actually fetch an action payload based on the JWT payload
        response = self.get_oc_payload_response(payload)
        self.assertEqual(200, response.status_code)

        payload = response.json()
        self.assertEqual(1, len(payload))
        payload = payload[0]

        # Checkout the document based on the action payload
        self.checkout_document(payload)

        # Test we can upload a new version of the file
        self.upload_document(payload, self.modified_file_content)

        # Test the uploaded new file is now properly the working copy
        self.api.headers.update({'Accept': payload['content-type']})
        response = self.api.get(
            '/'.join((payload['document-url'], payload['download'])))

        self.assertEqual(response.content, self.modified_file_content)

        # Check the document in without a comment
        self.api.get(
            '/'.join((payload['document-url'],
                      payload['checkin-without-comment']))
            + '?_authenticator={}'.format(payload['csrf-token']))

        # Test the journal entry from the commentless checkin
        browser.login()
        browser.open(
            self.doc_with_file_wf_open, view='tabbedview_view-journal')
        journal_entry = browser.css('.listing').first.lists()[1]

        self.assertEqual(journal_entry[1], 'Dokument eingecheckt')

        # Test the checked in version is the uploaded version
        self.api.headers.update({'Accept': payload['content-type']})
        response = self.api.get(
            '/'.join((payload['document-url'], 'download_file_version')))

        self.assertEqual(response.content, self.modified_file_content)

    @browsing
    def test_document_checkin_with_comment(self, browser):
        # Enable the OC checkout feature
        self.enable_oc_checkout()

        # Grab the OC URL
        payload = self.get_oc_url_jwt_decoded(
            self.doc_with_file_wf_open, 'checkout')

        self.assertIn('documents', payload)

        # Test we can actually fetch an action payload based on the JWT payload
        response = self.get_oc_payload_response(payload)
        self.assertEqual(200, response.status_code)

        payload = response.json()
        self.assertEqual(1, len(payload))
        payload = payload[0]

        # Perform a checkout based on the action payload
        self.checkout_document(payload)

        # Upload a new version of the file
        self.upload_document(payload, self.modified_file_content)

        # Check the document in with a comment
        self.checkin_with_comment(payload, self.test_comment)

        # Test the journal entries from the checkin with a comment
        browser.login()
        browser.open(
            self.doc_with_file_wf_open, view='tabbedview_view-journal')
        journal_entry = browser.css('.listing').first.lists()[1]

        self.assertEqual(journal_entry[1], 'Dokument eingecheckt')
        self.assertEqual(journal_entry[3], self.test_comment)

        # Test the uploaded new file is now properly the latest version
        self.api.headers.update({'Accept': payload['content-type']})
        response = self.api.get(
            '/'.join((payload['document-url'], payload['download'])))

        self.assertEqual(response.content, self.modified_file_content)
