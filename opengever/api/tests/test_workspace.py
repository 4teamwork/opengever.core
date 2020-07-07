from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from plone import api
import json


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


class TestChangeWorkspaceResponsiblePost(IntegrationTestCase):

    @browsing
    def test_workspace_admin_can_change_workspace_responsible(self, browser):
        self.login(self.workspace_owner, browser=browser)

        browser.open(
            self.workspace.absolute_url(),
            method="GET",
            headers=self.api_headers
        )
        # Make sure Kathi is not responsible of the workspace yet (in case that
        # ever changes in the fixtures). Otherwise this test does not make any sense.
        self.assertNotEqual(
            u"kathi.barfuss",
            browser.json["responsible"]["token"]
        )
        # Kathi Barfuss does not have the admin role yet. She will also not get
        # it after being set as the responsible of the workspace.
        self.assertNotIn(
            "WorkspaceAdmin",
            api.user.get_roles(username="kathi.barfuss", obj=self.workspace)
        )

        # Set the new responsible and make sure everything worked as expected. Please note
        # that Kathi did not get the admin role.
        browser.open(
            self.workspace.absolute_url() + "/@change-responsible",
            method="POST",
            headers=self.api_headers,
            data=json.dumps({"userid": u"kathi.barfuss"})
        )
        self.assertEqual(browser.status_code, 204)
        self.assertEqual(u"kathi.barfuss", self.workspace.Creator())
        self.assertNotIn(
            "WorkspaceAdmin",
            api.user.get_roles(username="kathi.barfuss", obj=self.workspace)
        )
        browser.open(
            self.workspace.absolute_url(),
            method="GET",
            headers=self.api_headers
        )
        self.assertEqual(
            u"kathi.barfuss",
            browser.json["responsible"]["token"]
        )

    @browsing
    def test_setting_workspace_responsible_raises_unauthorized_when_permission_missing(self, browser):
        self.login(self.workspace_member, browser=browser)

        with browser.expect_http_error(401):
            browser.open(
                self.workspace.absolute_url() + "/@change-responsible",
                method="POST",
                headers=self.api_headers,
                data=json.dumps({"userid": u"kathi.barfuss"})
            )

    @browsing
    def test_changing_responsible_requires_a_userid(self, browser):
        self.login(self.workspace_owner, browser=browser)
        with browser.expect_http_error(400):
            browser.open(
                self.workspace.absolute_url() + "/@change-responsible",
                method="POST",
                headers=self.api_headers
            )

        self.assertEqual(
            {
                "message": "Property 'userid' is required",
                "type": "BadRequest",
            },
            browser.json
        )

    @browsing
    def test_changing_responsible_requires_valid_userid(self, browser):
        self.login(self.workspace_owner, browser=browser)
        with browser.expect_http_error(400):
            browser.open(
                self.workspace.absolute_url() + "/@change-responsible",
                method="POST",
                headers=self.api_headers,
                data=json.dumps({"userid": "chaosqueen"})
            )
        self.assertEqual(
            {
                "message": "userid 'chaosqueen' does not exist",
                "type": "BadRequest"
            },
            browser.json
        )
