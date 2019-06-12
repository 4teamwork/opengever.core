from opengever.testing import IntegrationTestCase
from Products.PlonePAS.events import UserLoggedInEvent
from zope.event import notify
from ftw.testbrowser import browsing


class TestAvatarGeneration(IntegrationTestCase):

    @browsing
    def test_avatar_generation_is_disabled_when_ui_is_disabled(self, browser):
        self.login(self.regular_user, browser=browser)

        notify(UserLoggedInEvent(self.regular_user))

        browser.open()
        self.assertEquals(
            'http://nohost/plone/defaultUser.png?size=26',
            browser.css('#personaltools-portrait').first.get('src'))

    @browsing
    def test_avatar_generation_is_enabled_when_ui_enabled(self, browser):
        self.activate_feature('gever_ui')
        self.login(self.regular_user, browser=browser)

        notify(UserLoggedInEvent(self.regular_user))

        browser.open()
        self.assertEquals(
            'http://nohost/plone/portal_memberdata/portraits/kathi.barfuss?size=26',
            browser.css('#personaltools-portrait').first.get('src'))
