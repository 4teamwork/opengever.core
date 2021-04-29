from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from zExceptions import Unauthorized
from zope.component import getMultiAdapter


class TestWorkspaceSerializer(IntegrationTestCase):

    @browsing
    def test_workspace_serialization_contains_can_manage_participants(self, browser):
        self.login(self.workspace_member, browser)
        response = browser.open(
            self.workspace, headers={'Accept': 'application/json'}).json

        self.assertFalse(response.get(u'can_manage_participants'))

        self.login(self.workspace_owner, browser)
        response = browser.open(
            self.workspace, headers={'Accept': 'application/json'}).json

        self.assertTrue(response.get(u'can_manage_participants'))

    @browsing
    def test_workspace_serialization_contains_responsible(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(
            self.workspace, headers={'Accept': 'application/json'}).json

        self.assertDictContainsSubset({
            'responsible': {
                u'token': u'gunther.frohlich',
                u'title': u'Fr\xf6hlich G\xfcnther (gunther.frohlich)'
            },
            'responsible_fullname': u'Fr\xf6hlich G\xfcnther',
            },
            browser.json
        )

    @browsing
    def test_workspace_serialization_contains_videoconferencing_url(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(
            self.workspace, headers={'Accept': 'application/json'}).json

        self.assertIn(
            u'videoconferencing_url', browser.json)
        self.assertIn(
            u'https://meet.jit.si/', browser.json['videoconferencing_url'])


class TestDeleteWorkspaceContent(IntegrationTestCase):
    def test_delete_workspace_content_is_only_allowed_for_content_within_the_workspace_root(self):
        self.login(self.manager)

        workspace_document_id = self.workspace_document.id
        view = getMultiAdapter((self.workspace_document, self.request), name="DELETE_application_json_")
        self.assertTrue(view.is_within_workspace_root())

        self.assertIn(workspace_document_id, self.workspace.objectIds())
        view.reply()
        self.assertNotIn(workspace_document_id, self.workspace.objectIds())

        gever_document_id = self.document.id
        view = getMultiAdapter((self.document, self.request), name="DELETE_application_json_")
        self.assertFalse(view.is_within_workspace_root())

        self.assertIn(gever_document_id, self.dossier.objectIds())
        with self.assertRaises(Unauthorized):
            view.reply()
        self.assertIn(gever_document_id, self.dossier.objectIds())
