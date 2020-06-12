from opengever.testing import IntegrationTestCase
from ftw.testbrowser import browsing


class TestAssignedUsers(IntegrationTestCase):

    @browsing
    def test_get_assigned_users(self, browser):
        self.login(self.regular_user, browser=browser)
        url = self.portal.absolute_url() + '/@assigned-users?query=Fri'

        browser.open(url, method='GET', headers=self.api_headers)

        expected_json = {
            u'@id': url,
            u'items': [{
                u'title': u'Hugentobler Fridolin (fridolin.hugentobler)',
                u'token': u'fridolin.hugentobler'
                }],
            u'items_total': 1}

        self.assertEqual(expected_json, browser.json)

    @browsing
    def test_response_is_batched(self, browser):
        self.login(self.regular_user, browser=browser)
        url = self.portal.absolute_url() + '/@assigned-users?b_size=5'

        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(5, len(browser.json.get('items')))
        self.assertEqual(18, browser.json.get('items_total'))
        self.assertIn('batching', browser.json)
