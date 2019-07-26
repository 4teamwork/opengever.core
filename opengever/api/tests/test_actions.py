from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestCheckoutAPI(IntegrationTestCase):

    @browsing
    def test_available_file_actions_for_document(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document.absolute_url() + '/@actions',
                     method='GET', headers=self.api_headers)
        expected_file_actions = [
            {u'title': u'Download copy', u'id': u'download', u'icon': u''},
            ]
        listed_file_actions = browser.json['file_actions']
        self.assertEqual(expected_file_actions, listed_file_actions)

    @browsing
    def test_available_file_actions_for_mail(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.mail_eml.absolute_url() + '/@actions',
                     method='GET', headers=self.api_headers)
        expected_file_actions = [
            {u'title': u'Download copy', u'id': u'download', u'icon': u''},
            ]
        listed_file_actions = browser.json['file_actions']
        self.assertEqual(expected_file_actions, listed_file_actions)
