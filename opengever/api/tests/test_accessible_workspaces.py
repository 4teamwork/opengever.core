from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.testing.integration_test_case import SolrIntegrationTestCase


class TestAccessibleWorkspacesGet(SolrIntegrationTestCase):
    features = ('workspace', 'solr')

    def set_roles(self, obj, principal, roles):
        RoleAssignmentManager(obj).add_or_update_assignment(
            SharingRoleAssignment(principal, roles))

    @browsing
    def test_fetch_accessible_workspaces_is_allowed_for_administrators(self, browser):
        self.login(self.workspace_member, browser)

        url = '{}/@accessible-workspaces/{}'.format(self.portal.absolute_url(),
                                                    self.workspace_member.getId())
        with browser.expect_unauthorized():
            browser.open(url, headers=self.api_headers)

        self.login(self.administrator, browser)
        response = browser.open(url, headers=self.api_headers)

        self.assertEqual(200, response.status_code)

    @browsing
    def test_accessible_workspaces_response_for_user(self, browser):
        self.login(self.administrator, browser=browser)

        workspace = create(Builder('workspace').titled(
            u'A new workspace').within(self.workspace_root))
        self.set_roles(
            workspace, 'fa_users',
            ['WorkspaceMember'])
        self.commit_solr()

        url = '{}/@accessible-workspaces/{}'.format(self.portal.absolute_url(),
                                                    self.workspace_member.getId())
        browser.open(url, headers=self.api_headers)
        self.assertEqual(
            {u'@id': u'http://nohost/plone/@accessible-workspaces/beatrice.schrodinger',
             u'items': [{u'@id': workspace.absolute_url(),
                         u'@type': u'opengever.workspace.workspace',
                         u'review_state': u'opengever_workspace--STATUS--active',
                         u'title': u'A new workspace'},
                        {u'@id': self.workspace.absolute_url(),
                         u'@type': u'opengever.workspace.workspace',
                         u'review_state': u'opengever_workspace--STATUS--active',
                         u'title': u'A Workspace'}]}, browser.json)

    @browsing
    def test_raises_bad_request_when_userid_is_missing(self, browser):
        self.login(self.administrator, browser=browser)
        url = '{}/@accessible-workspaces'.format(self.portal.absolute_url())

        with browser.expect_http_error(400):
            browser.open(url, headers=self.api_headers)

        self.assertEqual(
            {"message": "Must supply a userid as URL path parameter.",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_raises_bad_request_when_too_many_params_are_given(self, browser):
        self.login(self.administrator, browser=browser)
        url = '{}/@accessible-workspaces/kathi.barfuss/bla'.format(self.portal.absolute_url())
        with browser.expect_http_error(400):
            browser.open(url, headers=self.api_headers)

        self.assertEqual(
            {"message": "Only userid is supported URL path parameter.",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_raises_bad_request_when_userid_is_invalid(self, browser):
        self.login(self.administrator, browser=browser)
        url = '{}/@accessible-workspaces/invalid'.format(self.portal.absolute_url())
        with browser.expect_http_error(400):
            browser.open(url, headers=self.api_headers)

        self.assertEqual(
            {"message": 'Invalid userid "invalid".',
             "type": "BadRequest"},
            browser.json)
