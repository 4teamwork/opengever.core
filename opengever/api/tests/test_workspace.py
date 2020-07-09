from ftw.testbrowser import browsing
from opengever.base.role_assignments import ASSIGNMENT_VIA_SHARING
from opengever.base.role_assignments import RoleAssignmentManager
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


class TestPossibleWorkspaceResponsibles(IntegrationTestCase):

    def _make_user_workspaces_admin(self, userid):
        RoleAssignmentManager(self.workspace).add_or_update(
            userid, ['WorkspaceAdmin'], ASSIGNMENT_VIA_SHARING)
        self.workspace.reindexObjectSecurity()

    @browsing
    def test_endpoint_requires_permission(self, browser):
        self.login(self.workspace_guest.id, browser=browser)
        url = self.workspace.absolute_url() + '/@possible-responsibles'
        with browser.expect_http_error(401):
            browser.open(url, method='GET', headers=self.api_headers)

        self._make_user_workspaces_admin(self.workspace_guest.id)
        self.login(self.workspace_guest.id, browser=browser)
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEquals(200, browser.status_code)

    @browsing
    def test_get_all_possible_responsibles(self, browser):
        self.login(self.workspace_admin, browser=browser)
        url = self.workspace.absolute_url() + '/@possible-responsibles'

        browser.open(url, method='GET', headers=self.api_headers)
        expected_json = {
            u'@id': url,
            u'items': [
                {
                    u'title': u'Fr\xf6hlich G\xfcnther',
                    u'token': u'gunther.frohlich'
                },
                {
                    u'title': u'Hugentobler Fridolin',
                    u'token': u'fridolin.hugentobler'
                },
                {
                    u'title': u'Peter Hans',
                    u'token': u'hans.peter'
                },
                {
                    u'title': u'Schr\xf6dinger B\xe9atrice',
                    u'token': u'beatrice.schrodinger'
                }
            ],
            u'items_total': 4,
        }
        self.assertEqual(expected_json, browser.json)

    @browsing
    def test_search_for_possible_responsibles(self, browser):
        self.login(self.workspace_admin, browser=browser)
        url = self.workspace.absolute_url() + '/@possible-responsibles?query=Hans'

        browser.open(url, method='GET', headers=self.api_headers)
        expected_json = {
            u'@id': url,
            u'items': [
                {
                    u'title': u'Peter Hans',
                    u'token': u'hans.peter'
                },
            ],
            u'items_total': 1,
        }
        self.assertEqual(expected_json, browser.json)

    @browsing
    def test_response_is_batched(self, browser):
        self.login(self.workspace_admin, browser=browser)
        url = self.workspace.absolute_url() + '/@possible-responsibles?b_size=2'

        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(2, len(browser.json.get('items')))
        self.assertEqual(4, browser.json.get('items_total'))
        self.assertIn('batching', browser.json)
