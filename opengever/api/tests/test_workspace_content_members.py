from ftw.testbrowser import browsing
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.testing import IntegrationTestCase
from plone import api
from unittest import skip
from zExceptions import Forbidden
import json


class TestWorkspaceContentMembersGetGet(IntegrationTestCase):

    @browsing
    def test_get_workspace_content_members(self, browser):
        self.login(self.workspace_member, browser=browser)
        url = self.workspace.absolute_url() + '/@workspace-content-members'
        browser.open(url, method='GET', headers=self.api_headers)

        expected_json = {
            u'@id': u'http://nohost/plone/workspaces/workspace-1/@workspace-content-members',
            u'items': [{u'title': u'Fr\xf6hlich G\xfcnther (gunther.frohlich)',
                        u'token': u'gunther.frohlich'},
                       {u'title': u'Hugentobler Fridolin (fridolin.hugentobler)',
                        u'token': u'fridolin.hugentobler'},
                       {u'title': u'Peter Hans (hans.peter)',
                        u'token': u'hans.peter'},
                       {u'title': u'Schr\xf6dinger B\xe9atrice (beatrice.schrodinger)',
                        u'token': u'beatrice.schrodinger'}],
            u'items_total': 4}
        self.assertEqual(expected_json, browser.json)

    @browsing
    def test_raises_forbidden_for_guests_if_members_are_hidden(self, browser):
        browser.exception_bubbling = True

        self.login(self.workspace_admin)
        self.workspace.hide_members_for_guests = True

        self.login(self.workspace_guest, browser=browser)
        url = self.workspace.absolute_url() + '/@workspace-content-members'
        with self.assertRaises(Forbidden):
            browser.open(url, method='GET', headers=self.api_headers)

    @browsing
    def test_get_workspace_content_members_with_query(self, browser):
        self.login(self.workspace_member, browser=browser)
        url = self.workspace.absolute_url() + '/@workspace-content-members?query=bea'
        browser.open(url, method='GET', headers=self.api_headers)

        expected_json = {
            u'@id': u'http://nohost/plone/workspaces/workspace-1/@workspace-content-members?query=bea',
            u'items': [{u'title': u'Schr\xf6dinger B\xe9atrice (beatrice.schrodinger)',
                        u'token': u'beatrice.schrodinger'}],
            u'items_total': 1}
        self.assertEqual(expected_json, browser.json)

    @browsing
    @skip('Title should contain username, not userid')
    def test_get_workspace_content_members_includes_group_users(self, browser):
        self.login(self.workspace_admin, browser=browser)
        browser.open(self.workspace, view='@workspace-content-members', method='GET',
                     headers=self.api_headers)
        self.assertEqual(4, browser.json['items_total'])
        self.assertNotIn({u'title': u'Kohler Nicole (nicole.kohler)',
                          u'token': self.administrator.id},
                         browser.json['items'])
        self.assertNotIn({u'title': u'M\xfcller Fr\xe4nzi (franzi.muller)',
                          u'token': self.committee_responsible.id},
                         browser.json['items'])

        data = json.dumps({'participant': 'committee_rpk_group', 'role': 'WorkspaceMember'})
        browser.open(self.workspace, view='/@participations/committee_rpk_group', method='POST',
                     headers=self.api_headers, data=data)

        browser.open(self.workspace, view='@workspace-content-members', method='GET',
                     headers=self.api_headers)
        self.assertEqual(6, browser.json['items_total'])
        self.assertIn({u'title': u'Kohler Nicole (nicole.kohler)',
                       u'token': self.administrator.id},
                      browser.json['items'])
        self.assertIn({u'title': u'M\xfcller Fr\xe4nzi (franzi.muller)',
                       u'token': self.committee_responsible.id},
                      browser.json['items'])

    @browsing
    def test_get_workspace_content_members_includes_groups(self, browser):
        self.login(self.workspace_admin, browser=browser)

        data = json.dumps({'participant': 'committee_rpk_group', 'role': 'WorkspaceMember'})
        browser.open(self.workspace, view='/@participations/committee_rpk_group', method='POST',
                     headers=self.api_headers, data=data)

        browser.open(self.workspace, view='@workspace-content-members?include_groups=true',
                     method='GET', headers=self.api_headers)

        self.assertEqual({u'token': u'committee_rpk_group', u'title': u'Gruppe Rechnungspr\xfcfungskommission'},
                         browser.json['items'][-1])

    @browsing
    def test_get_workspace_content_members_respects_local_roles_block(self, browser):
        self.login(self.workspace_member, browser=browser)
        url = self.workspace_folder.absolute_url() + '/@workspace-content-members'
        browser.open(url, method='GET', headers=self.api_headers)
        expected_json = {
            u'@id': u'http://nohost/plone/workspaces/workspace-1/folder-1/@workspace-content-members',
            u'items': [{u'title': u'Fr\xf6hlich G\xfcnther (gunther.frohlich)',
                        u'token': u'gunther.frohlich'},
                       {u'title': u'Hugentobler Fridolin (fridolin.hugentobler)',
                        u'token': u'fridolin.hugentobler'},
                       {u'title': u'Peter Hans (hans.peter)',
                        u'token': u'hans.peter'},
                       {u'title': u'Schr\xf6dinger B\xe9atrice (beatrice.schrodinger)',
                        u'token': u'beatrice.schrodinger'}],
            u'items_total': 4}
        self.assertEqual(expected_json, browser.json)

        self.workspace_folder.__ac_local_roles_block__ = True
        RoleAssignmentManager(self.workspace_folder).add_or_update_assignment(
            SharingRoleAssignment(api.user.get_current().getId(), ['WorkspaceMember']))

        browser.open(url, method='GET', headers=self.api_headers)

        expected_json = {
            u'@id': u'http://nohost/plone/workspaces/workspace-1/folder-1/@workspace-content-members',
            u'items': [{u'title': u'Schr\xf6dinger B\xe9atrice (beatrice.schrodinger)',
                        u'token': u'beatrice.schrodinger'}],
            u'items_total': 1}
        self.assertEqual(expected_json, browser.json)

    @browsing
    def test_get_workspace_content_members_outside_a_workspace(self, browser):
        self.login(self.regular_user, browser=browser)
        url = self.document.absolute_url() + '/@workspace-content-members'
        with browser.expect_http_error(400):
            browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(
            {"message": "'{}' is not within a workspace".format(self.document.getId()),
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_response_is_batched(self, browser):
        self.login(self.workspace_member, browser=browser)
        url = self.workspace.absolute_url() + '/@workspace-content-members?b_size=2'

        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(2, len(browser.json.get('items')))
        self.assertEqual(4, browser.json.get('items_total'))
        self.assertIn('batching', browser.json)
