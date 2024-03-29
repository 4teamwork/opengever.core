from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.contact.tests import create_contacts
from opengever.kub.interfaces import IKuBSettings
from opengever.testing import IntegrationTestCase
from plone import api


class TestContactFolderTabbedView(IntegrationTestCase):

    def setUp(self):
        super(TestContactFolderTabbedView, self).setUp()
        create_contacts(self)

    @browsing
    def test_shows_local_and_user_tab(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.contactfolder, view='tabbed_view')

        self.assertEquals(
            ['Local', 'Users', 'Teams'],
            browser.css('.formTab').text)

    @browsing
    def test_shows_user_and_teams_tab_and_info_when_kub_feature_is_enabled(self, browser):
        api.portal.set_registry_record(
            'base_url', u'http://localhost:8000', IKuBSettings)
        self.login(self.regular_user, browser)
        browser.open(self.contactfolder, view='tabbed_view')
        self.assertEqual(
            ['The Contact and Authorities directory is only supported in the new UI.'],
            info_messages())
        self.assertEquals(
            ['Users', 'Teams'],
            browser.css('.formTab').text)
