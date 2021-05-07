from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
import json


class TestUploadStructure(IntegrationTestCase):

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

        self.assertEqual(message, browser.json['message'])
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
                    u'items': {
                        u'file.txt': {
                            u'@type': u'opengever.document.document',
                            u'relative_path': u'folder/file.txt'},
                        u'subfolder': {
                            u'@type': u'opengever.dossier.businesscasedossier',
                            u'relative_path': u'folder/subfolder',
                            u'items': {
                                u'file2.txt': {
                                    u'@type': u'opengever.document.document',
                                    u'relative_path': u'folder/subfolder/file2.txt'}
                                }
                            }
                        }
                    }
                },
             u'max_container_depth': 2,
             u'items_total': 4},
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
                    u'items': {
                        u'file.txt': {
                            u'@type': u'opengever.document.document',
                            u'relative_path': u'/folder/file.txt'},
                        }
                    }
                },
             u'max_container_depth': 1,
             u'items_total': 2},
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
            {u'message': u"Property 'files' is required", u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_upload_structure_raises_if_user_cannot_add_content_in_context(self, browser):
        self.login(self.regular_user, browser)

        self.assert_upload_structure_raises_bad_request(
            browser, self.inactive_dossier, ['/folder/file.txt'],
            u'User is not allowed to add objects here')

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
