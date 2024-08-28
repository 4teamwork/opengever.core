from ftw.testbrowser import browsing
from opengever.sign.utils import is_sign_feature_enabled
from opengever.testing import IntegrationTestCase


class TestSigning(IntegrationTestCase):

    @browsing
    def test_can_enable_sign_feature(self, browser):
        self.login(self.regular_user, browser=browser)

        self.assertFalse(is_sign_feature_enabled())
        self.activate_feature('sign')
        self.assertTrue(is_sign_feature_enabled())
