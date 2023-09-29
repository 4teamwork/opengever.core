from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.api.upload_structure import IUploadStructureAnalyser
from opengever.contact.tests import create_contacts
from opengever.dossier.interfaces import IDossierContainerTypes
from opengever.testing import SolrIntegrationTestCase
from plone import api
import json


class TestUploadStructure(SolrIntegrationTestCase):

    maxDiff = None

    def assert_upload_structure_returns_ok(self, browser, context, files):
        payload = {u'files': files}
        browser.open(context,
                     view="@upload-structure",
                     data=json.dumps(payload),
                     method='POST',
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)

    def assert_upload_structure_raises_bad_request(self, browser, context, files, message):
        payload = {u'files': files}
        with browser.expect_http_error(code=400):
            browser.open(context,
                         view="@upload-structure",
                         data=json.dumps(payload),
                         method='POST',
                         headers=self.api_headers)

        self.assertEqual(message, browser.json['translated_message'])
        self.assertEqual(u'BadRequest', browser.json['type'])

    @browsing
    def test_upload_structure(self, browser):
        self.login(self.regular_user, browser)

        self.assert_upload_structure_returns_ok(
            browser,
            self.leaf_repofolder,
            ['folder/file.txt', 'folder/subfolder/file2.txt'])

        self.assertEqual(
            {u'items': {
                u'folder': {
                    u'@type': u'opengever.dossier.businesscasedossier',
                    u'relative_path': u'folder',
                    u'is_container': True,
                    u'items': {
                        u'file.txt': {
                            u'@type': u'opengever.document.document',
                            u'relative_path': u'folder/file.txt',
                            u'is_container': False},
                        u'subfolder': {
                            u'@type': u'opengever.dossier.businesscasedossier',
                            u'relative_path': u'folder/subfolder',
                            u'is_container': True,
                            u'items': {
                                u'file2.txt': {
                                    u'@type': u'opengever.document.document',
                                    u'relative_path': u'folder/subfolder/file2.txt',
                                    u'is_container': False}
                                }
                            }
                        }
                    }
                },
             u'max_container_depth': 2,
             u'items_total': 4,
             u'possible_duplicates': {}},
            browser.json)

    @browsing
    def test_upload_structure_respects_leading_slash(self, browser):
        self.login(self.regular_user, browser)

        self.assert_upload_structure_returns_ok(
            browser,
            self.leaf_repofolder,
            ['/folder/file.txt'])

        self.assertEqual(
            {u'items': {
                u'folder': {
                    u'@type': u'opengever.dossier.businesscasedossier',
                    u'relative_path': u'/folder',
                    u'is_container': True,
                    u'items': {
                        u'file.txt': {
                            u'@type': u'opengever.document.document',
                            u'relative_path': u'/folder/file.txt',
                            u'is_container': False},
                        }
                    }
                },
             u'max_container_depth': 1,
             u'items_total': 2,
             u'possible_duplicates': {}},
            browser.json)

    @browsing
    def test_upload_structure_requires_files_list(self, browser):
        self.login(self.regular_user, browser)

        payload = {}
        with browser.expect_http_error(code=400):
            browser.open(self.leaf_repofolder,
                         view="@upload-structure",
                         data=json.dumps(payload),
                         method='POST',
                         headers=self.api_headers)

        self.assertEqual(
            {u'additional_metadata': {},
             u'message': u'msg_prop_file_required',
             u'translated_message': u"Property 'files' is required",
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_upload_structure_requires_non_empty_filenames(self, browser):
        self.login(self.regular_user, browser)

        self.assert_upload_structure_raises_bad_request(
            browser, self.dossier, [''],
            u'Empty filename not supported')

        self.assert_upload_structure_raises_bad_request(
            browser, self.dossier, [None],
            u'Empty filename not supported')

    @browsing
    def test_upload_structure_raises_if_user_cannot_add_content_in_context(self, browser):
        self.login(self.regular_user, browser)

        payload = {u'files': ['/folder/file.txt']}
        with browser.expect_http_error(code=403):
            browser.open(self.inactive_dossier,
                         view="@upload-structure",
                         data=json.dumps(payload),
                         method='POST',
                         headers=self.api_headers)

        self.assertEqual(u'User is not allowed to add objects here',
                         browser.json['message'])
        self.assertEqual(u'Forbidden', browser.json['type'])

    @browsing
    def test_upload_structure_raises_if_max_dossier_depth_would_be_exceeded(self, browser):
        self.login(self.regular_user, browser)

        self.assert_upload_structure_returns_ok(
            browser,
            self.dossier,
            ['/folder/file.txt'])

        self.assert_upload_structure_raises_bad_request(
            browser,
            self.subdossier,
            ['/folder/file.txt'],
            u'Maximum dossier depth exceeded')

    @browsing
    def test_upload_structure_allows_document_upload_even_max_dossier_depth_is_already_exceeded(self, browser):
        self.login(self.regular_user, browser)

        subsubdossier = create(Builder('dossier').within(self.subdossier))

        self.assert_upload_structure_raises_bad_request(
            browser,
            subsubdossier,
            ['/folder/file.txt'],
            u'Maximum dossier depth exceeded')

        self.assert_upload_structure_returns_ok(
            browser,
            subsubdossier,
            ['file.txt'])

    @browsing
    def test_upload_structure_respects_local_dossier_depth(self, browser):
        self.login(self.regular_user, browser)

        # validate the max_dossier_depth
        self.assertEqual(1, api.portal.get_registry_record(
            name='maximum_dossier_depth', interface=IDossierContainerTypes))

        # Uploading a structure to this brand new dossier will not be possible
        # because the global max_depth will will be exceeded.
        dossier = create(Builder('dossier').within(self.leaf_repofolder))
        self.assert_upload_structure_raises_bad_request(
            browser,
            dossier,
            ['/folder1/folder2/file.txt'],
            u'Maximum dossier depth exceeded')

        # We now create some subdossier up to a depth of three which is more
        # than the allowed global depth. So the local allowed depth will be 3
        # for this dossier-tree.
        #
        # Uploading a structure up to a depth of three to the dossier should be
        # possible now.
        subdossier = create(Builder('dossier').within(dossier))
        create(Builder('dossier').within(subdossier))
        self.assert_upload_structure_returns_ok(
            browser,
            dossier,
            ['/folder1/folder2/file.txt'])

        # but will still raise if the upload structure exceeds the local limit
        self.assert_upload_structure_raises_bad_request(
            browser,
            dossier,
            ['/folder1/folder2/folder3/file.txt'],
            u'Maximum dossier depth exceeded')

    @browsing
    def test_upload_structure_ignores_maximal_depth_in_workspace_area(self, browser):
        self.login(self.workspace_member, browser)

        self.assert_upload_structure_returns_ok(
            browser,
            self.workspace,
            ['/folder/folder/folder/file.txt'])

    @browsing
    def test_upload_structure_in_inbox_container(self, browser):
        self.login(self.manager, browser)

        # dossier cannot be added in inbox container
        self.assert_upload_structure_raises_bad_request(
            browser, self.inbox_container, ['folder/file.txt'],
            u'Some of the objects cannot be added here')

        # document cannot be added in inbox container
        self.assert_upload_structure_raises_bad_request(
            browser, self.inbox_container, ['file.txt'],
            u'Some of the objects cannot be added here')

    @browsing
    def test_upload_structure_in_inbox(self, browser):
        self.login(self.manager, browser)

        # dossier cannot be added in inbox
        self.assert_upload_structure_raises_bad_request(
            browser, self.inbox, ['folder/file.txt'],
            u'Some of the objects cannot be added here')

        # document can be added in inbox
        self.assert_upload_structure_returns_ok(
            browser, self.inbox, ['file.txt'])

        self.assertEqual(browser.json['items']['file.txt']['@type'],
                         u'opengever.document.document')

    @browsing
    def test_upload_structure_in_repository_root(self, browser):
        self.login(self.manager, browser)

        # dossier cannot be added in repository root
        self.assert_upload_structure_raises_bad_request(
            browser, self.repository_root, ['folder/file.txt'],
            u'Some of the objects cannot be added here')

        # document cannot be added in repository root
        self.assert_upload_structure_raises_bad_request(
            browser, self.repository_root, ['file.txt'],
            u'Some of the objects cannot be added here')

    @browsing
    def test_upload_structure_in_branch_repofolder(self, browser):
        self.login(self.manager, browser)

        # dossier cannot be added in branch repofolder
        self.assert_upload_structure_raises_bad_request(
            browser, self.branch_repofolder, ['folder/file.txt'],
            u'Some of the objects cannot be added here')

        # document cannot be added in branch repofolder
        self.assert_upload_structure_raises_bad_request(
            browser, self.branch_repofolder, ['file.txt'],
            u'Some of the objects cannot be added here')

    @browsing
    def test_upload_structure_in_leaf_repofolder(self, browser):
        self.login(self.manager, browser)

        # document cannot be added in repository folder
        self.assert_upload_structure_raises_bad_request(
            browser, self.leaf_repofolder, ['file.txt'],
            u'Some of the objects cannot be added here')

        # dossier can be added in repository folder
        self.assert_upload_structure_returns_ok(
            browser,
            self.leaf_repofolder,
            ['folder/file.txt', 'folder/file.msg'])

        folder = browser.json['items']['folder']
        self.assertEqual(folder['@type'],
                         u'opengever.dossier.businesscasedossier')
        self.assertEqual(folder['items']['file.txt']['@type'],
                         u'opengever.document.document')
        self.assertEqual(folder['items']['file.msg']['@type'],
                         u'ftw.mail.mail')
    @browsing
    def test_upload_structure_in_dossier(self, browser):
        self.login(self.regular_user, browser)
        self.assert_upload_structure_returns_ok(
            browser,
            self.dossier,
            ['folder/file.txt', 'file.msg'])

        folder = browser.json['items']['folder']
        self.assertEqual(folder['@type'],
                         u'opengever.dossier.businesscasedossier')
        self.assertEqual(folder['items']['file.txt']['@type'],
                         u'opengever.document.document')
        self.assertEqual(browser.json['items']['file.msg']['@type'],
                         u'ftw.mail.mail')

    @browsing
    def test_upload_structure_in_workspace_root(self, browser):
        self.login(self.manager, browser)

        # dossier cannot be added in workspace root
        self.assert_upload_structure_raises_bad_request(
            browser, self.workspace_root, ['folder/file.txt'],
            u'Some of the objects cannot be added here')

        # document cannot be added in workspace root
        self.assert_upload_structure_raises_bad_request(
            browser, self.workspace_root, ['file.txt'],
            u'Some of the objects cannot be added here')

    @browsing
    def test_upload_structure_in_workspace(self, browser):
        self.login(self.workspace_member, browser)
        self.assert_upload_structure_returns_ok(
            browser,
            self.workspace,
            ['folder/file.txt', 'file.msg'])

        folder = browser.json['items']['folder']
        self.assertEqual(folder['@type'],
                         u'opengever.workspace.folder')
        self.assertEqual(folder['items']['file.txt']['@type'],
                         u'opengever.document.document')
        self.assertEqual(browser.json['items']['file.msg']['@type'],
                         u'ftw.mail.mail')

    @browsing
    def test_upload_structure_in_workspace_folder(self, browser):
        self.login(self.workspace_member, browser)
        self.assert_upload_structure_returns_ok(
            browser,
            self.workspace_folder,
            ['folder/file.txt', 'file.msg'])

        folder = browser.json['items']['folder']
        self.assertEqual(folder['@type'],
                         u'opengever.workspace.folder')
        self.assertEqual(folder['items']['file.txt']['@type'],
                         u'opengever.document.document')
        self.assertEqual(browser.json['items']['file.msg']['@type'],
                         u'ftw.mail.mail')

    @browsing
    def test_upload_structure_in_task(self, browser):
        self.login(self.manager, browser)

        # dossier cannot be added in task
        self.assert_upload_structure_raises_bad_request(
            browser, self.task, ['folder/file.txt'],
            u'Some of the objects cannot be added here')

        self.assert_upload_structure_returns_ok(
            browser, self.task, ['file.txt', 'file.msg'])
        self.assertEqual(browser.json['items']['file.txt']['@type'],
                         u'opengever.document.document')
        self.assertEqual(browser.json['items']['file.msg']['@type'],
                         u'ftw.mail.mail')

    @browsing
    def test_upload_structure_in_proposal(self, browser):
        self.login(self.manager, browser)

        # dossier cannot be added in proposal
        self.assert_upload_structure_raises_bad_request(
            browser, self.proposal, ['folder/file.txt'],
            u'Some of the objects cannot be added here')

        # document cannot be added in proposal
        self.assert_upload_structure_raises_bad_request(
            browser, self.proposal, ['file.txt'],
            u'Some of the objects cannot be added here')

    @browsing
    def test_upload_structure_in_contact_folder(self, browser):
        create_contacts(self)
        self.commit_solr()
        self.login(self.manager, browser)

        # dossier cannot be added in contact folder
        self.assert_upload_structure_raises_bad_request(
            browser, self.contactfolder, ['folder/file.txt'],
            u'Some of the objects cannot be added here')

        # document cannot be added in contact folder
        self.assert_upload_structure_raises_bad_request(
            browser, self.contactfolder, ['file.txt'],
            u'Some of the objects cannot be added here')

    @browsing
    def test_upload_structure_in_committee_container(self, browser):
        self.login(self.manager, browser)

        # dossier cannot be added in committee container
        self.assert_upload_structure_raises_bad_request(
            browser, self.committee_container, ['folder/file.txt'],
            u'Some of the objects cannot be added here')

        # document cannot be added in committee container
        self.assert_upload_structure_raises_bad_request(
            browser, self.committee_container, ['file.txt'],
            u'Some of the objects cannot be added here')

    @browsing
    def test_upload_structure_in_committee(self, browser):
        self.login(self.manager, browser)

        # dossier cannot be added in committee
        self.assert_upload_structure_raises_bad_request(
            browser, self.committee, ['folder/file.txt'],
            u'Some of the objects cannot be added here')

        # document cannot be added in committee
        self.assert_upload_structure_raises_bad_request(
            browser, self.committee_container, ['file.txt'],
            u'Some of the objects cannot be added here')

    @browsing
    def test_upload_structure_in_templatefolder(self, browser):
        self.login(self.manager, browser)

        # dossier cannot be added in templatefolder
        self.assert_upload_structure_raises_bad_request(
            browser, self.templates, ['folder/file.txt'],
            u'Some of the objects cannot be added here')

        # document can be added in templatefolder
        self.assert_upload_structure_returns_ok(
            browser, self.templates, ['file.txt'])
        self.assertEqual(browser.json['items']['file.txt']['@type'],
                         u'opengever.document.document')

    @browsing
    def test_upload_structure_in_dossiertemplate(self, browser):
        self.login(self.manager, browser)

        # dossier cannot be added in dossiertemplate
        self.assert_upload_structure_raises_bad_request(
            browser, self.dossiertemplate, ['folder/file.txt'],
            u'Some of the objects cannot be added here')

        # document can be added in dossiertemplate
        self.assert_upload_structure_returns_ok(
            browser, self.dossiertemplate, ['file.txt'])
        self.assertEqual(browser.json['items']['file.txt']['@type'],
                         u'opengever.document.document')

    @browsing
    def test_upload_structure_in_proposal_template(self, browser):
        self.login(self.manager, browser)

        # dossier cannot be added in proposal_template
        self.assert_upload_structure_raises_bad_request(
            browser, self.proposal_template, ['folder/file.txt'],
            u'Some of the objects cannot be added here')

        # document can be added in proposal_template
        self.assert_upload_structure_returns_ok(
            browser, self.proposal_template, ['file.txt'])
        self.assertEqual(browser.json['items']['file.txt']['@type'],
                         u'opengever.document.document')

    @browsing
    def test_upload_structure_in_tasktemplate(self, browser):
        self.login(self.manager, browser)

        # dossier cannot be added in tasktemplate
        self.assert_upload_structure_raises_bad_request(
            browser, self.tasktemplate, ['folder/file.txt'],
            u'Some of the objects cannot be added here')

        # document cannot be added in tasktemplate
        self.assert_upload_structure_raises_bad_request(
            browser, self.tasktemplate, ['file.txt'],
            u'Some of the objects cannot be added here')

    @browsing
    def test_upload_structure_in_private_root(self, browser):
        self.login(self.manager, browser)

        # dossier cannot be added in private root
        self.assert_upload_structure_raises_bad_request(
            browser, self.private_root, ['folder/file.txt'],
            u'Some of the objects cannot be added here')

        # document cannot be added in private root
        self.assert_upload_structure_raises_bad_request(
            browser, self.private_root, ['file.txt'],
            u'Some of the objects cannot be added here')

    @browsing
    def test_upload_structure_in_private_folder(self, browser):
        self.login(self.regular_user, browser)

        # document cannot be added in private folder
        self.assert_upload_structure_raises_bad_request(
            browser, self.private_folder, ['file.txt'],
            u'Some of the objects cannot be added here')

        # dossier can be added in private folder
        self.assert_upload_structure_returns_ok(
            browser, self.private_folder, ['folder/file.txt'])

        folder = browser.json['items']['folder']
        self.assertEqual(folder['@type'],
                         u'opengever.private.dossier')
        self.assertEqual(folder['items']['file.txt']['@type'],
                         u'opengever.document.document')


class TestDuplicateControl(SolrIntegrationTestCase):

    def assert_upload_structure_returns_ok(self, browser, context, files):
        payload = {u'files': files}
        browser.open(context,
                     view="@upload-structure",
                     data=json.dumps(payload),
                     method='POST',
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)

    @browsing
    def test_duplicate_control_handles_unicode(self, browser):
        self.login(self.manager, browser)

        self.assert_upload_structure_returns_ok(
            browser, self.subdossier, [u"Vertr\xe4gsentwurf.docx"])

        self.assertIn(u"Vertr\xe4gsentwurf.docx", browser.json['possible_duplicates'])
        self.assertEqual(
            [{u'@id': self.document.absolute_url_path(),
              u'@type': u'opengever.document.document',
              u'filename': u'Vertraegsentwurf.docx',
              u'title': u'Vertr\xe4gsentwurf'}],
            browser.json['possible_duplicates'][u"Vertr\xe4gsentwurf.docx"])

    @browsing
    def test_duplicate_control_handles_path(self, browser):
        self.login(self.manager, browser)

        self.assert_upload_structure_returns_ok(
            browser, self.dossier, [u"foo/Vertr\xe4gsentwurf.docx"])

        self.assertIn(u"foo/Vertr\xe4gsentwurf.docx",
                      browser.json['possible_duplicates'])
        self.assertEqual(
            [{u'@id': self.document.absolute_url_path(),
              u'@type': u'opengever.document.document',
              u'filename': u'Vertraegsentwurf.docx',
              u'title': u'Vertr\xe4gsentwurf'}],
            browser.json['possible_duplicates'][u"foo/Vertr\xe4gsentwurf.docx"])

    @browsing
    def test_subdossier_duplicate_control_searches_main_dossier(self, browser):
        self.login(self.manager, browser)

        self.assert_upload_structure_returns_ok(
            browser, self.subdossier2,
            [self.meeting_document.get_filename(),
             self.document.get_filename(),
             self.subsubdocument.get_filename()])

        self.assertNotIn(self.meeting_document.get_filename(),
                         browser.json['possible_duplicates'])
        self.assertIn(self.document.get_filename(),
                      browser.json['possible_duplicates'])
        self.assertIn(self.subsubdocument.get_filename(),
                      browser.json['possible_duplicates'])
        self.assertEqual(
            [{u'@id': self.document.absolute_url_path(),
              u'@type': u'opengever.document.document',
              u'filename': u'Vertraegsentwurf.docx',
              u'title': u'Vertr\xe4gsentwurf'}],
            browser.json['possible_duplicates'][self.document.get_filename()])
        self.assertEqual(
            [{u'@id': self.subsubdocument.absolute_url_path(),
              u'@type': u'opengever.document.document',
              u'filename': u'Uebersicht der Vertraege von 2014.xlsx',
              u'title': u'\xdcbersicht der Vertr\xe4ge von 2014'}],
            browser.json['possible_duplicates'][self.subsubdocument.get_filename()])

    @browsing
    def test_duplicate_control_search_root(self, browser):
        self.login(self.manager, browser)

        # No search performed on these levels
        analyser = IUploadStructureAnalyser(self.leaf_repofolder)
        self.assertEqual(None, analyser.duplicate_search_root)

        analyser = IUploadStructureAnalyser(self.private_folder)
        self.assertEqual(None, analyser.duplicate_search_root)

        # search in main dossier
        analyser = IUploadStructureAnalyser(self.private_dossier)
        self.assertEqual(self.private_dossier, analyser.duplicate_search_root)

        analyser = IUploadStructureAnalyser(self.dossier)
        self.assertEqual(self.dossier, analyser.duplicate_search_root)

        analyser = IUploadStructureAnalyser(self.subsubdossier)
        self.assertEqual(self.dossier, analyser.duplicate_search_root)

        analyser = IUploadStructureAnalyser(self.subtask)
        self.assertEqual(self.dossier, analyser.duplicate_search_root)

        # search in main TemplateFolder
        analyser = IUploadStructureAnalyser(self.templates)
        self.assertEqual(self.templates, analyser.duplicate_search_root)

        analyser = IUploadStructureAnalyser(self.subtemplates)
        self.assertEqual(self.templates, analyser.duplicate_search_root)

        # search in main DossierTemplate
        analyser = IUploadStructureAnalyser(self.dossiertemplate)
        self.assertEqual(self.dossiertemplate, analyser.duplicate_search_root)

        analyser = IUploadStructureAnalyser(self.subdossiertemplate)
        self.assertEqual(self.dossiertemplate, analyser.duplicate_search_root)

        # search in current context
        analyser = IUploadStructureAnalyser(self.inbox)
        self.assertEqual(self.inbox, analyser.duplicate_search_root)

        # search in workspace
        analyser = IUploadStructureAnalyser(self.workspace)
        self.assertEqual(self.workspace, analyser.duplicate_search_root)

        analyser = IUploadStructureAnalyser(self.workspace_folder)
        self.assertEqual(self.workspace, analyser.duplicate_search_root)
