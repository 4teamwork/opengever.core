from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestGeverLayoutPolicy(IntegrationTestCase):

    @browsing
    def test_bumblebee_feature(self, browser):
        self.login(self.regular_user, browser)
        feature_class = 'feature-bumblebee'

        self.deactivate_feature('bumblebee')
        browser.open()
        self.assertNotIn(feature_class, browser.css('body').first.classes)

        self.activate_feature('bumblebee')
        browser.open()
        self.assertIn(feature_class, browser.css('body').first.classes)

    @browsing
    def test_word_meeting_feature_presence(self, browser):
        self.login(self.regular_user, browser)
        self.activate_feature('meeting')
        feature_class = 'feature-word-meeting'

        self.deactivate_feature('word-meeting')
        browser.open()
        self.assertNotIn(feature_class, browser.css('body').first.classes)

        self.activate_feature('word-meeting')
        browser.open()
        self.assertIn(feature_class, browser.css('body').first.classes)
