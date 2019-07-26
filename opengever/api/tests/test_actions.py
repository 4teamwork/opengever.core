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
            {u'icon': u'',
             u'id': u'officeconnector_checkout_url',
             u'title': u'Checkout and edit'},
            ]
        listed_file_actions = browser.json['file_actions']
        self.assertEqual(expected_file_actions, listed_file_actions)

    @browsing
    def test_zem_checkout_available_if_oc_checkout_deactivated(self, browser):
        self.deactivate_feature('officeconnector-checkout')
        self.login(self.regular_user, browser)
        browser.open(self.document.absolute_url() + '/@actions',
                     method='GET', headers=self.api_headers)
        expected_file_actions = [
            {u'title': u'Download copy', u'id': u'download', u'icon': u''},
            {u'icon': u'', u'id': u'zem_checkout', u'title': u'Checkout and edit'}
            ]
        listed_file_actions = browser.json['file_actions']
        self.assertEqual(expected_file_actions, listed_file_actions)

    @browsing
    def test_simple_checkout_available_if_file_not_oc_editable(self, browser):
        self.login(self.regular_user, browser)
        self.document.file.contentType = u'foo/bar'
        browser.open(self.document.absolute_url() + '/@actions',
                     method='GET', headers=self.api_headers)
        expected_file_actions = [
            {u'title': u'Download copy', u'id': u'download', u'icon': u''},
            {u'icon': u'', u'id': u'simple_checkout', u'title': u'Checkout'}
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
