from ftw.testbrowser import browsing
from mock import patch
from opengever.testing import IntegrationTestCase


class TestOGDSSync(IntegrationTestCase):

    @browsing
    def test_syncs_users_groups_and_local_groups(self, browser):
        self.login(self.administrator, browser=browser)

        # patch
        with patch('opengever.api.ogdssync.sync_ogds') as mock_sync:
            url = "{}/@ogds-sync".format(self.portal.absolute_url())
            browser.open(url, method="POST", headers=self.api_headers)

        mock_sync.assert_called_once_with(
            self.portal, users=True, groups=True, local_groups=True)

        self.assertEqual(204, browser.status_code)

    @browsing
    def test_sync_is_only_allowed_for_administrators(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(401):
            url = "{}/@ogds-sync".format(self.portal.absolute_url())
            browser.open(url, method="POST", headers=self.api_headers)

        self.assertEqual(
            {u'message': u'You are not authorized to access this resource.',
             u'type': u'Unauthorized'},
            browser.json)
