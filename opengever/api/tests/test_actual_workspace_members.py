from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestActualWorkspaceMembersGet(IntegrationTestCase):

    @browsing
    def test_get_actual_workspace_members(self, browser):
        self.login(self.workspace_member, browser=browser)
        url = self.workspace.absolute_url() + '/@actual-workspace-members'
        browser.open(url, method='GET', headers=self.api_headers)

        expected_json = {
            u'@id': u'http://nohost/plone/workspaces/workspace-1/@actual-workspace-members',
            u'items': [{u'title': u'Fr\xf6hlich G\xfcnther',
                        u'token': u'gunther.frohlich'},
                       {u'title': u'Hugentobler Fridolin',
                        u'token': u'fridolin.hugentobler'},
                       {u'title': u'Peter Hans',
                        u'token': u'hans.peter'},
                       {u'title': u'Schr\xf6dinger B\xe9atrice',
                        u'token': u'beatrice.schrodinger'}],
            u'items_total': 4}
        self.assertEqual(expected_json, browser.json)

    @browsing
    def test_get_actual_workspace_members_with_query(self, browser):
        self.login(self.workspace_member, browser=browser)
        url = self.workspace.absolute_url() + '/@actual-workspace-members?query=bea'
        browser.open(url, method='GET', headers=self.api_headers)

        expected_json = {
            u'@id': u'http://nohost/plone/workspaces/workspace-1/@actual-workspace-members?query=bea',
            u'items': [{u'title': u'Schr\xf6dinger B\xe9atrice',
                        u'token': u'beatrice.schrodinger'}],
            u'items_total': 1}
        self.assertEqual(expected_json, browser.json)

    @browsing
    def test_get_actual_workspace_members_outside_a_workspace(self, browser):
        self.login(self.regular_user, browser=browser)
        url = self.document.absolute_url() + '/@actual-workspace-members'
        with browser.expect_http_error(400):
            browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(
            {"message": "'{}' is not within a workspace".format(self.document.getId()),
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_response_is_batched(self, browser):
        self.login(self.workspace_member, browser=browser)
        url = self.workspace.absolute_url() + '/@actual-workspace-members?b_size=2'

        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(2, len(browser.json.get('items')))
        self.assertEqual(4, browser.json.get('items_total'))
        self.assertIn('batching', browser.json)
