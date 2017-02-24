from ftw.builder import Builder
from ftw.builder import create
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
import transaction


class TestOfficeconnectorAPI(FunctionalTestCase):

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
        self.dossier = create(Builder('dossier')
                              .within(self.repofolder)
                              .titled(u'Mein Dossier'))
        # We rely on the creation order of these documents for the tests!
        # ZServer craps out if you have non-ascii in the document titles!
        self.document_without_attachment = create(Builder('document')
                                                  .titled(u'docu-1')
                                                  .within(self.dossier))
        self.document_with_attachment = create(Builder('document')
                                               .titled(u'docu-2')
                                               .within(self.dossier)
                                               .attach_file_containing(
                                                   self.original_file_content))

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

    def enable_checkout(self):
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

    def test_returns_404_when_feature_disabled(self):
        self.assertEquals(404, self.get_oc_url_response_status(self.document_without_attachment, 'attach')) # noqa
        self.assertEquals(404, self.get_oc_url_response_status(self.document_with_attachment, 'attach')) # noqa
        self.assertEquals(404, self.get_oc_url_response_status(self.document_without_attachment, 'checkout')) # noqa
        self.assertEquals(404, self.get_oc_url_response_status(self.document_with_attachment, 'checkout')) # noqa

    def test_attach_to_outlook_url_without_file(self):
        self.enable_attach_to_outlook()
        self.assertEquals(404, self.get_oc_url_response_status(self.document_without_attachment, 'attach')) # noqa

    def test_attach_to_outlook_payload_without_file(self):
        self.enable_attach_to_outlook()
        self.assertEquals(404, self.get_oc_payload_response_status(self.document_without_attachment, 'attach')) # noqa

    def test_attach_to_outlook_url_with_file(self):
        self.enable_attach_to_outlook()
        self.assertEquals(200, self.get_oc_url_response_status(self.document_with_attachment, 'attach')) # noqa

        payload = self.get_oc_url_payload(self.document_with_attachment, 'attach') # noqa
        self.assertTrue('url' in payload)

        token = self.get_oc_url_jwt(self.document_with_attachment, 'attach') # noqa
        self.assertTrue('url' in token)
        self.assertTrue('/oc_attach/' in token['url'])
        self.assertEquals(token['action'], 'attach')
        self.assertEquals(TEST_USER_ID, token['sub'])

    def test_attach_to_outlook_payload_with_file(self):
        self.enable_attach_to_outlook()
        token = self.get_oc_url_jwt(self.document_with_attachment, 'attach') # noqa

        # Test we can actually fetch an action payload based on the URL JWT
        response = self.api.get(token['url'])
        self.assertEquals(200, response.status_code)

        payload = response.json()
        self.assertTrue('csrf-token' in payload)
        self.assertTrue('download' in payload)
        self.assertEquals(self.document_with_attachment.file.contentType, payload['content-type']) # noqa
        self.assertEquals(self.document_with_attachment.absolute_url(), payload['document-url']) # noqa
        self.assertEquals(self.document_with_attachment.get_filename(), payload['filename']) # noqa

    def test_attach_to_outlook(self):
        self.enable_attach_to_outlook()
        token = self.get_oc_url_jwt(self.document_with_attachment, 'attach') # noqa

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

    def test_document_checkout_url_without_file(self):
        self.enable_checkout()
        self.assertEquals(404, self.get_oc_url_response_status(self.document_without_attachment, 'checkout')) # noqa

    def test_document_checkout_payload_without_file(self):
        self.enable_checkout()
        self.assertEquals(404, self.get_oc_url_response_status(self.document_without_attachment, 'checkout')) # noqa

    def test_document_checkout_url_with_file(self):
        self.enable_checkout()
        self.assertEquals(200, self.get_oc_url_response_status(self.document_with_attachment, 'checkout')) # noqa

        payload = self.get_oc_url_payload(self.document_with_attachment, 'checkout') # noqa
        self.assertTrue('url' in payload)

        token = self.get_oc_url_jwt(self.document_with_attachment, 'checkout') # noqa
        self.assertTrue('url' in token)
        self.assertTrue('/oc_checkout/' in token['url'])
        self.assertEquals(token['action'], 'checkout')
        self.assertEquals(TEST_USER_ID, token['sub'])

    def test_document_checkout_payload_with_file(self):
        self.enable_checkout()
        token = self.get_oc_url_jwt(self.document_with_attachment, 'checkout') # noqa

        # Test we can actually fetch an action payload based on the URL JWT
        response = self.api.get(token['url'])
        self.assertEquals(200, response.status_code)

        payload = response.json()
        self.assertTrue('csrf-token' in payload)
        self.assertTrue('download' in payload)
        self.assertEquals(self.document_with_attachment.file.contentType, payload['content-type']) # noqa
        self.assertEquals(self.document_with_attachment.absolute_url(), payload['document-url']) # noqa
        self.assertEquals(self.document_with_attachment.get_filename(), payload['filename']) # noqa

    @browsing
    def test_document_checkout(self, browser):
        self.enable_checkout()
        token = self.get_oc_url_jwt(self.document_with_attachment, 'checkout') # noqa

        # Test we can actually fetch an action payload based on the URL JWT
        response = self.api.get(token['url'])
        payload = response.json()

        # Test fetching the indicated file
        self.api.headers.update({'Accept': payload['content-type']})
        response = self.api.get('/'.join((payload['document-url'], payload['download']))) # noqa

        self.assertEquals(200, response.status_code)
        self.assertEquals(response.headers['content-type'], payload['content-type']) # noqa
        self.assertEquals(response.headers['content-disposition'], 'attachment; filename="{}"'.format(payload['filename'])) # noqa
        self.assertEquals(response.content, self.original_file_content)

        # Test we can perform a checkout based on the action payload
        self.api.headers.update({'Accept': 'text/html'})
        self.api.get('/'.join((payload['document-url'], payload['checkout'])) + '?_authenticator={}'.format(payload['csrf-token'])) # noqa

        self.assertTrue(browser.login().open(self.document_with_attachment).css('.checked_out_viewlet')) # noqa

    @browsing
    def test_document_checkin_without_comment(self, browser):
        self.enable_checkout()
        token = self.get_oc_url_jwt(self.document_with_attachment, 'checkout') # noqa

        # Test we can actually fetch an action payload based on the URL JWT
        response = self.api.get(token['url'])
        payload = response.json()

        # Test fetching the indicated file
        self.api.headers.update({'Accept': payload['content-type']})
        response = self.api.get('/'.join((payload['document-url'], payload['download']))) # noqa

        # Test we can perform a checkout based on the action payload
        self.api.headers.update({'Accept': 'text/html'})
        self.api.get('/'.join((payload['document-url'], payload['checkout'])) + '?_authenticator={}'.format(payload['csrf-token'])) # noqa

        # Test we can upload a new version of the file
        browser.login()
        browser.open(self.document_with_attachment, view=payload['edit-form'])
        # The DATA in the file tuple needs to be seekable
        browser.fill({
            'form.widgets.file.action': 'replace',
            'form.widgets.file': (
                str(self.modified_file_content),
                payload['filename'],
                payload['content-type'],
                ),
            })
        browser.css('#form-buttons-save').first.click()

        # Test we can check in the file
        response = self.api.get('/'.join((payload['document-url'], payload['checkin-without-comment'])) + '?_authenticator={}'.format(payload['csrf-token'])) # noqa

        # Test the uploaded new file is now properly the latest version
        self.api.headers.update({'Accept': payload['content-type']})
        response = self.api.get('/'.join((payload['document-url'], payload['download']))) # noqa

        self.assertEquals(response.content, self.modified_file_content)

    @browsing
    def test_document_checkin_with_comment(self, browser):
        self.enable_checkout()
        token = self.get_oc_url_jwt(self.document_with_attachment, 'checkout') # noqa

        # Test we can actually fetch an action payload based on the URL JWT
        response = self.api.get(token['url'])
        payload = response.json()

        # Test fetching the indicated file
        self.api.headers.update({'Accept': payload['content-type']})
        response = self.api.get('/'.join((payload['document-url'], payload['download']))) # noqa

        # Test we can perform a checkout based on the action payload
        self.api.headers.update({'Accept': 'text/html'})

        self.api.get('/'.join((payload['document-url'], payload['checkout'])) + '?_authenticator={}' .format(payload['csrf-token'])) # noqa

        # Test we can upload a new version of the file
        browser.login()
        browser.open(self.document_with_attachment, view=payload['edit-form'])
        # The DATA in the file tuple needs to be seekable
        browser.fill({
            'form.widgets.file.action': 'replace',
            'form.widgets.file': (
                str(self.modified_file_content),
                payload['filename'],
                payload['content-type'],
                ),
            })
        browser.css('#form-buttons-save').first.click()

        # Test we can check in with a comment
        browser.open(self.document_with_attachment, view='checkin_document')
        browser.fill({
            'form.widgets.comment': self.test_comment,
        })
        browser.css('#form-buttons-button_checkin').first.click()

        browser.open(self.document_with_attachment, view='tabbedview_view-journal') # noqa

        journal_entry = browser.css('.listing').first.lists()[1]

        self.assertEquals(journal_entry[1], 'Dokument eingecheckt')
        self.assertEquals(journal_entry[3], self.test_comment)

        # Test the uploaded new file is now properly the latest version
        self.api.headers.update({'Accept': payload['content-type']})
        response = self.api.get('/'.join((payload['document-url'], payload['download']))) # noqa

        self.assertEquals(response.content, self.modified_file_content)
