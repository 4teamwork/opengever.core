from datetime import datetime
from ftw.testbrowser import browsing
from opengever.document.approvals import IApprovalList
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.interfaces import IDocumentSettings
from opengever.document.interfaces import ITemplateDocumentMarker
from opengever.document.versioner import Versioner
from opengever.private.interfaces import IPrivateFolderQuotaSettings
from opengever.testing import IntegrationTestCase
from opengever.workspaceclient.interfaces import ILinkedDocuments
from plone import api
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
    def test_contains_meeting_metadata(self, browser):
        self.activate_feature('meeting')
        self.login(self.committee_responsible, browser)

        document = self.decided_proposal.get_excerpt()
        browser.open(document, headers=self.api_headers)
        self.assertEqual({u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/'
                                  u'vertrage-und-vereinbarungen/dossier-1/proposal-3',
                          u'title': u'Initialvertrag f\xfcr Bearbeitung'}, browser.json['proposal'])

        self.assertEqual({'@id': self.decided_proposal.absolute_url(),
                          'title': self.decided_proposal.title}, browser.json['submitted_proposal'])
        self.assertEqual({'@id': self.decided_meeting.model.get_url(),
                          'title': self.decided_meeting.model.title}, browser.json['meeting'])

        browser.open(self.document, headers=self.api_headers)
        self.assertEqual([{'@id': self.proposal.absolute_url(), 'title': self.proposal.title}],
                         browser.json['submitted_with'])

    @browsing
    def test_does_not_contain_meeting_metadata_when_meeting_feature_disabled(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, headers=self.api_headers)

        self.assertIsNone(browser.json.get('proposal'))
        self.assertIsNone(browser.json.get('meeting'))
        self.assertIsNone(browser.json.get('submitted_proposal'))
        self.assertIsNone(browser.json.get('submitted_with'))

    @browsing
    def test_contains_collaborative_checkout_info(self, browser):
        self.login(self.regular_user, browser)

        self.checkout_document(self.subdocument, collaborative=True)

        browser.open(self.subdocument, headers={'Accept': 'application/json'})
        self.assertTrue(browser.json['is_collaborative_checkout'])
        self.assertEqual(browser.json['checkout_collaborators'], ['kathi.barfuss'])

    @browsing
    def test_contains_file_modification_time(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.subdocument, headers={'Accept': 'application/json'})
        self.assertTrue(isinstance(browser.json['file_mtime'], float))

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
    def test_respects_version_specific_file_extension(self, browser):
        self.login(self.regular_user, browser)

        versioner = Versioner(self.document)
        versioner.create_initial_version()

        self.checkout_document(self.document)
        self.document.file = NamedBlobFile(
            data='PDF TEST DATA', filename=u'final.pdf')
        self.checkin_document(self.document)

        url = '{}/@history/0'.format(self.document.absolute_url())
        browser.open(url, headers=self.api_headers)
        self.assertEqual(browser.json.get(u'file_extension'), u'.docx')

        url = '{}/@history/1'.format(self.document.absolute_url())
        browser.open(url, headers=self.api_headers)
        self.assertEqual(browser.json.get(u'file_extension'), u'.pdf')

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

    @browsing
    def test_contains_document_backreferences(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.subdocument, method="GET", headers=self.api_headers)
        self.assertEqual(
            [{u'@id': self.subsubdocument.absolute_url(),
              u'@type': u'opengever.document.document',
              u'UID': u'createtreatydossiers000000000019',
              u'checked_out': None,
              u'description': u'',
              u'file_extension': u'.xlsx',
              u'is_leafnode': None,
              u'review_state': u'document-state-draft',
              u'title': self.subsubdocument.title}],
            browser.json['back_references_relatedItems'])

        browser.open(self.mail_eml, method="GET", headers=self.api_headers)
        self.assertEqual([], browser.json['back_references_relatedItems'])

    @browsing
    def test_filters_anything_but_documents_from_backreferences(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.document, method="GET", headers=self.api_headers)
        self.assertEqual([
            (u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/document-22',
             u'opengever.document.document'),
            (u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/dossier-4/document-23',
             u'opengever.document.document')],
            [(ref['@id'], ref['@type']) for ref in browser.json['back_references_relatedItems']])

    @browsing
    def test_approvals_expansion(self, browser):
        self.login(self.regular_user, browser=browser)

        approvals = IApprovalList(self.document)
        approvals.add(
            0, self.subtask, self.regular_user.id, datetime(2021, 7, 2))
        approvals.add(
            1, self.task_in_protected_dossier, self.administrator.id,
            datetime(2021, 8, 2))

        self.login(self.meeting_user, browser=browser)

        browser.open(
            '{}?expand=approvals'.format(self.document.absolute_url()),
            method="GET", headers=self.api_headers,)

        self.assertEqual(
            [{u'approved': u'2021-07-02T00:00:00',
              u'approver': u'kathi.barfuss',
              u'task': {
                  u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/task-1/task-2',
                  u'@type': u'opengever.task.task',
                  u'UID': u'createtasks000000000000000000002',
                  u'description': u'',
                  u'is_leafnode': None,
                  u'review_state': u'task-state-resolved',
                  u'title': u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen'},
              u'version_id': 0},
             {u'approved': u'2021-08-02T00:00:00',
              u'approver': u'nicole.kohler',
              u'task': None,
              u'version_id': 1}],
            browser.json['@components']['approvals'])

    @browsing
    def test_document_serialization_contains_workspace_document_links(self, browser):
        self.login(self.workspace_member, browser)

        adapter = ILinkedDocuments(self.document)
        adapter.link_workspace_document(IUUID(self.workspace_document))
        adapter.link_workspace_document(IUUID(self.workspace_folder_document))

        with self.env(TEAMRAUM_URL='https://example.com/teamraum'):
            browser.open(self.document, headers={'Accept': 'application/json'})

            self.assertEqual(
                [u'https://example.com/teamraum/redirect-to-uuid/createworkspace00000000000000003',
                 u'https://example.com/teamraum/redirect-to-uuid/createworkspace00000000000000005'],
                browser.json["workspace_document_urls"])


class TestDocumentPost(IntegrationTestCase):

    @browsing
    def test_does_not_allow_mails_as_file(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(code=400, reason='Bad Request'):
            data = {'@type': 'opengever.document.document',
                    'file': {'data': 'foo bar', 'filename': 'test.eml'}}
            browser.open(self.dossier, data=json.dumps(data), method='POST',
                         headers=self.api_headers)

        self.assertEqual(u'BadRequest', browser.json[u'type'])
        self.assertEqual(u'It is not possible to add E-mails as document, '
                         'use portal_type ftw.mail.mail instead.',
                         browser.json[u'translated_message'])

    @browsing
    def test_raises_if_quota_is_exceeded(self, browser):
        self.login(self.regular_user, browser)

        api.portal.set_registry_record(interface=IPrivateFolderQuotaSettings,
                                       name='size_hard_limit', value=1)

        with self.observe_children(self.private_dossier) as children:
            with browser.expect_http_error(code=403, reason='Forbidden'):
                data = {'@type': 'opengever.document.document',
                        'file': {'data': 'foo bar', 'filename': 'test.docx'}}
                browser.open(self.private_dossier, data=json.dumps(data), method='POST',
                             headers=self.api_headers)
        self.assertEqual(0, len(children["added"]))

    @browsing
    def test_document_is_marked_as_template_when_added_in_template_folder(self, browser):
        self.login(self.dossier_responsible, browser)

        with self.observe_children(self.templates) as children:
            data = {'@type': 'opengever.document.document',
                    'file': {'data': 'foo bar', 'filename': 'test.docx'}}
            browser.open(self.templates, data=json.dumps(data), method='POST',
                         headers=self.api_headers)

        self.assertEqual(1, len(children["added"]))
        doc = children["added"].pop()
        self.assertTrue(ITemplateDocumentMarker.providedBy(doc))

    @browsing
    def test_document_is_not_marked_as_template_when_added_in_template_dossier(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossiertemplate)

        with self.observe_children(self.dossiertemplate) as children:
            data = {'@type': 'opengever.document.document',
                    'file': {'data': 'foo bar', 'filename': 'test.docx'}}
            browser.open(self.dossiertemplate, data=json.dumps(data),
                         method='POST', headers=self.api_headers)

        self.assertEqual(1, len(children["added"]))
        doc = children["added"].pop()
        self.assertFalse(ITemplateDocumentMarker.providedBy(doc))

    @browsing
    def test_does_not_allow_blacklisted_filetypes(self, browser):
        self.login(self.regular_user, browser)

        api.portal.set_registry_record(
            'upload_filetypes_blacklist', ['.zip'], IDocumentSettings)

        # Do not allow to upload zip-files
        with browser.expect_http_error(code=400, reason='Bad Request'):
            data = {'@type': 'opengever.document.document',
                    'file': {'data': 'foo bar', 'filename': 'test.zip'}}
            browser.open(self.dossier, data=json.dumps(data), method='POST',
                         headers=self.api_headers)

        api.portal.set_registry_record(
            'upload_filetypes_blacklist', ['zip'], IDocumentSettings)

        # File extensions don't require leading dot
        with browser.expect_http_error(code=400, reason='Bad Request'):
            data = {'@type': 'opengever.document.document',
                    'file': {'data': 'foo bar', 'filename': 'test.zip'}}
            browser.open(self.dossier, data=json.dumps(data), method='POST',
                         headers=self.api_headers)

        api.portal.set_registry_record(
            'upload_filetypes_blacklist', ['ZIP'], IDocumentSettings)

        # File extensions are compared case insensitively
        with browser.expect_http_error(code=400, reason='Bad Request'):
            data = {'@type': 'opengever.document.document',
                    'file': {'data': 'foo bar', 'filename': 'test.zIp'}}
            browser.open(self.dossier, data=json.dumps(data), method='POST',
                         headers=self.api_headers)

        self.assertEqual(u'BadRequest', browser.json[u'type'])
        self.assertEqual(u'It is not allowed to upload this file format',
                         browser.json[u'translated_message'])

        # But allow all other file types
        with self.observe_children(self.dossier) as children:
            data = {'@type': 'opengever.document.document',
                    'file': {'data': 'foo bar', 'filename': 'test.docx'}}
            browser.open(self.dossier, data=json.dumps(data), method='POST',
                         headers=self.api_headers)

        self.assertEqual(1, len(children["added"]))


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
            browser.json["translated_message"],
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
            browser.json["translated_message"],
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

    @browsing
    def test_disallows_non_docx_mimetype_for_proposal_documents(self, browser):
        self.login(self.regular_user, browser)
        document = self.draft_proposal.get_proposal_document()
        manager = getMultiAdapter((document, self.request),
                                  ICheckinCheckoutManager)
        manager.checkout()

        data = {
            "file": {
                "data": "foo bar",
                "filename": "foo.txt",
                "content-type": "text/plain"
            }
        }

        with browser.expect_http_error(code=403, reason="Forbidden"):
            browser.open(
                document,
                data=json.dumps(data),
                method="PATCH",
                headers=self.api_headers)
        self.assertEqual(
            browser.json["translated_message"],
            "Mime type must be "
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document "
            "for proposal documents."
        )

    @browsing
    def test_disallows_non_docx_filename_for_proposal_documents(self, browser):
        self.login(self.regular_user, browser)
        document = self.draft_proposal.get_proposal_document()
        manager = getMultiAdapter((document, self.request),
                                  ICheckinCheckoutManager)
        manager.checkout()

        data = {
            "file": {
                "data": "foo bar",
                "filename": "foo.txt",
            }
        }

        with browser.expect_http_error(code=403, reason="Forbidden"):
            browser.open(
                document,
                data=json.dumps(data),
                method="PATCH",
                headers=self.api_headers)
        self.assertEqual(
            browser.json["translated_message"],
            'File extension must be .docx for proposal documents.'
        )

    @browsing
    def test_prevents_removing_file_from_proposal_document(self, browser):
        self.login(self.regular_user, browser)
        document = self.draft_proposal.get_proposal_document()
        manager = getMultiAdapter((document, self.request),
                                  ICheckinCheckoutManager)
        manager.checkout()

        data = {
            "file": None
        }

        with browser.expect_http_error(code=403, reason="Forbidden"):
            browser.open(
                document,
                data=json.dumps(data),
                method="PATCH",
                headers=self.api_headers)

        self.assertEqual(
            browser.json["translated_message"],
            "Proposal documents require a file."
        )
