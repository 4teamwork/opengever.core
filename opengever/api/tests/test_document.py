from ftw.testbrowser import browsing
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.versioner import Versioner
from opengever.testing import IntegrationTestCase
from opengever.workspaceclient.interfaces import ILinkedDocuments
from plone.namedfile.file import NamedBlobFile
from plone.uuid.interfaces import IUUID
from zope.component import getMultiAdapter
import json


class TestDocumentSerializer(IntegrationTestCase):

    @browsing
    def test_document_serialization_contains_preview_url(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'preview_url')[:124],
            u'http://bumblebee/YnVtYmxlYmVl/api/v3/resource/local/51d6317494e'
            u'ccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2/preview')

    @browsing
    def test_document_serialization_contains_pdf_url(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'pdf_url')[:120],
            u'http://bumblebee/YnVtYmxlYmVl/api/v3/resource/local/51d6317494e'
            u'ccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2/pdf')

    @browsing
    def test_document_serialization_contains_thumbnail_url(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            browser.json.get(u'thumbnail_url')[:126],
            u'http://bumblebee/YnVtYmxlYmVl/api/v3/resource/local/51d6317494e'
            u'ccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2/thumbnail')

    @browsing
    def test_document_serialization_contains_file_extension(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual('.docx', browser.json.get(u'file_extension'))

        browser.open(self.mail_msg, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        self.assertEqual('.msg', browser.json.get(u'file_extension'))

    @browsing
    def test_contains_additional_metadata(self, browser):
        self.login(self.regular_user, browser)

        # The helpers used for the api are already tested, so no
        # need to repeat these here.
        self.checkout_document(self.subdocument)

        browser.open(self.subdocument, headers={'Accept': 'application/json'})

        self.assertEqual(self.regular_user.id, browser.json['checked_out'])
        self.assertEqual(u'B\xe4rfuss K\xe4thi', browser.json['checked_out_fullname'])
        self.assertFalse(browser.json['is_collaborative_checkout'])
        self.assertFalse(browser.json['is_locked'])
        self.assertEqual(u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
                         browser.json['containing_dossier'])
        self.assertEqual(u'2016', browser.json['containing_subdossier'])
        self.assertEqual(self.subdossier.absolute_url(), browser.json['containing_subdossier_url'])
        self.assertFalse(browser.json['trashed'])
        self.assertFalse(browser.json['is_shadow_document'])
        self.assertFalse(0, browser.json['current_version_id'])
        self.assertDictEqual({
            u'identifier': u'robert.ziegler',
            u'@id': u'http://nohost/plone/@actors/robert.ziegler',
        }, browser.json['creator'])

    @browsing
    def test_contains_collaborative_checkout_info(self, browser):
        self.login(self.regular_user, browser)

        self.checkout_document(self.subdocument, collaborative=True)

        browser.open(self.subdocument, headers={'Accept': 'application/json'})
        self.assertTrue(browser.json['is_collaborative_checkout'])

    @browsing
    def test_respects_version_id_when_traversing_on_older_version(self, browser):
        self.login(self.regular_user, browser)

        versioner = Versioner(self.document)
        versioner.create_initial_version()

        self.checkout_document(self.document)
        self.document.file = NamedBlobFile(
            data='TEST DATA', filename=self.document.file.filename)
        self.checkin_document(self.document)

        url = '{}/@history/0'.format(self.document.absolute_url())
        browser.open(url, headers=self.api_headers)
        self.assertEqual(
            browser.json.get(u'preview_url')[:124],
            u'http://bumblebee/YnVtYmxlYmVl/api/v3/resource/local/51d6317494e'
            u'ccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2/preview')

        url = '{}/@history/1'.format(self.document.absolute_url())
        browser.open(url, headers=self.api_headers)
        self.assertNotEqual(
            browser.json.get(u'preview_url')[:124],
            u'http://bumblebee/YnVtYmxlYmVl/api/v3/resource/local/51d6317494e'
            u'ccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2/preview')

    @browsing
    def test_document_serialization_contains_tr_connect_links_on_gever_doc(self, browser):
        self.login(self.workspace_member, browser)

        adapter = ILinkedDocuments(self.document)
        adapter.link_workspace_document(IUUID(self.workspace_document))
        adapter.link_workspace_document(IUUID(self.workspace_folder_document))

        browser.open(self.document, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        expected_links = {
            'workspace_documents': [
                {'UID': IUUID(self.workspace_document)},
                {'UID': IUUID(self.workspace_folder_document)},
            ],
            'gever_document': None,
        }
        self.assertEqual(expected_links, browser.json['teamraum_connect_links'])

    @browsing
    def test_document_serialization_contains_tr_connect_links_on_workspace_doc(self, browser):
        self.login(self.workspace_member, browser)

        adapter = ILinkedDocuments(self.workspace_document)
        adapter.link_gever_document(IUUID(self.document))

        browser.open(self.workspace_document, headers={'Accept': 'application/json'})
        self.assertEqual(browser.status_code, 200)
        expected_links = {
            'workspace_documents': [],
            'gever_document': {
                'UID': IUUID(self.document),
            },
        }
        self.assertEqual(expected_links, browser.json['teamraum_connect_links'])


class TestWorkspaceDocument(IntegrationTestCase):

    @browsing
    def test_members_can_permanently_delete_document(self, browser):
        self.login(self.workspace_member, browser)
        workspace_document_id = self.workspace_document.id
        self.assertIn(workspace_document_id, self.workspace.objectIds())
        browser.open(self.workspace_document, method='DELETE', headers=self.api_headers)
        self.assertEqual(204, browser.status_code)
        self.assertNotIn(workspace_document_id, self.workspace.objectIds())

    @browsing
    def test_admins_can_permanently_delete_document(self, browser):
        self.login(self.workspace_admin, browser)
        workspace_document_id = self.workspace_document.id
        self.assertIn(workspace_document_id, self.workspace.objectIds())
        browser.open(self.workspace_document, method='DELETE', headers=self.api_headers)
        self.assertEqual(204, browser.status_code)
        self.assertNotIn(workspace_document_id, self.workspace.objectIds())

    @browsing
    def test_managers_can_permanently_delete_document(self, browser):
        self.login(self.manager, browser)
        workspace_document_id = self.workspace_document.id
        self.assertIn(workspace_document_id, self.workspace.objectIds())
        browser.open(self.workspace_document, method='DELETE', headers=self.api_headers)
        self.assertEqual(204, browser.status_code)
        self.assertNotIn(workspace_document_id, self.workspace.objectIds())

    @browsing
    def test_guests_cannot_permanently_delete_document(self, browser):
        self.login(self.workspace_guest, browser)
        with browser.expect_http_error(401):
            browser.open(self.workspace_document, method='DELETE', headers=self.api_headers)


class TestDocumentPost(IntegrationTestCase):

    @browsing
    def test_does_not_allow_mails_as_file(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(code=400, reason='Bad Request'):
            data = {'@type': 'opengever.document.document',
                    'file': {'data': 'foo bar', 'filename': 'test.eml'}}
            browser.open(self.dossier, data=json.dumps(data), method='POST',
                         headers=self.api_headers)

        self.assertEqual(
            u"[{'message': 'It is not possible to add E-mails as document, use portal_type ftw.mail.mail"
            " instead.', 'error': 'ValidationError'}]",
            browser.json['message'])


class TestDocumentDelete(IntegrationTestCase):

    @browsing
    def test_can_permanently_delete_template_document(self, browser):
        self.login(self.dossier_responsible, browser)
        template_id = self.normal_template.id
        self.assertIn(template_id, self.templates.objectIds())
        browser.open(self.normal_template, method='DELETE', headers=self.api_headers)
        self.assertEqual(204, browser.status_code)
        self.assertNotIn(template_id, self.templates.objectIds())

    @browsing
    def test_regular_user_cant_permanently_delete_document(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_http_error(403):
            browser.open(self.document, method='DELETE', headers=self.api_headers)

    @browsing
    def test_dossier_manager_cant_permanently_delete_document(self, browser):
        self.login(self.dossier_manager, browser)
        with browser.expect_http_error(403):
            browser.open(self.document, method='DELETE', headers=self.api_headers)

    @browsing
    def test_administrator_cant_permanently_delete_document(self, browser):
        self.login(self.administrator, browser)
        with browser.expect_http_error(403):
            browser.open(self.document, method='DELETE', headers=self.api_headers)

    @browsing
    def test_manager_can_permanently_delete_document(self, browser):
        self.login(self.manager, browser)
        document_id = self.document.id
        self.assertIn(document_id, self.dossier.objectIds())
        browser.open(self.document, method='DELETE', headers=self.api_headers)
        self.assertEqual(204, browser.status_code)
        self.assertNotIn(document_id, self.dossier.objectIds())


class TestDocumentPatch(IntegrationTestCase):

    def setUp(self):
        super(TestDocumentPatch, self).setUp()

    @browsing
    def test_document_patch_forbidden_if_not_checked_out(self, browser):
        self.login(self.regular_user, browser)
        self.assertFalse(self.document.is_checked_out())
        with browser.expect_http_error(code=403, reason='Forbidden'):
            browser.open(
                self.document.absolute_url(),
                data='{"file": {"data": "foo bar", "filename": "foo.txt",'
                     ' "content-type": "text/plain"}}',
                method='PATCH',
                headers={'Accept': 'application/json',
                         'Content-Type': 'application/json'})
        self.assertEqual(
            browser.json['error']['message'],
            'Document not checked-out by current user.')

    @browsing
    def test_document_patch_forbidden_if_not_checked_out_by_current_user(self, browser):
        self.login(self.dossier_responsible, browser)
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)
        manager.checkout()

        self.login(self.regular_user, browser)
        with browser.expect_http_error(code=403, reason='Forbidden'):
            browser.open(
                self.document.absolute_url(),
                data='{"file": {"data": "foo bar", "filename": "foo.txt",'
                     ' "content-type": "text/plain"}}',
                method='PATCH',
                headers={'Accept': 'application/json',
                         'Content-Type': 'application/json'})
        self.assertEqual(
            browser.json['error']['message'],
            'Document not checked-out by current user.')

    @browsing
    def test_document_patch_allowed_if_checked_out_by_current_user(self, browser):
        self.login(self.regular_user, browser)
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)
        manager.checkout()
        browser.open(
            self.document.absolute_url(),
            data='{"file": {"data": "foo bar", "filename": "foo.txt",'
                 ' "content-type": "text/plain"}}',
            method='PATCH',
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'})
        self.assertEqual(browser.status_code, 204)
        self.assertEqual(self.document.file.data, 'foo bar')

    @browsing
    def test_document_patch_allowed_if_not_modifying_file(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.document.absolute_url(),
            data='{"description": "Foo bar"}',
            method='PATCH',
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'})
        self.assertEqual(browser.status_code, 204)
        self.assertEqual(self.document.Description(), u'Foo bar')

    @browsing
    def test_title_and_filename_are_synced_correctly_when_patched_in_single_request(self, browser):
        """This tests an edge case where the title is set to empty string in
        the same request as the filename is changed. The result should be that
        the title gets synced to the new filename, the risk being that when the
        filename is set to empty string, it gets synced to the old filename,
        then the filename is changed and the synced to the title, so that we
        endup with both filename and title reflecting the old filename.
        """
        self.login(self.regular_user, browser)
        manager = getMultiAdapter((self.document, self.request),
                                  ICheckinCheckoutManager)
        manager.checkout()
        browser.open(
            self.document.absolute_url(),
            data='{"file": {"data": "foo bar", "filename": "foo.txt",'
                 ' "content-type": "text/plain"},'
                 ' "title": ""}',
            method='PATCH',
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'})
        self.assertEqual(browser.status_code, 204)
        self.assertEqual(self.document.get_filename(), 'foo.txt')
        self.assertEqual(self.document.title, 'foo')
