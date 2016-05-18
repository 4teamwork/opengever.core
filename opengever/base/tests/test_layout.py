from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.testing import FunctionalTestCase


class TestGeverLayoutPolicy(FunctionalTestCase):
    @browsing
    def test_bumblebee_feature_body_class_is_not_present_if_feature_is_disabled(self, browser):
        browser.login().visit()
        self.assertNotIn(
            'feature-bumblebee',
            browser.css('body').first.get('class').split(' '))


class TestGeverLayoutPolicyBumblebeeFeature(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_bumblebee_feature_body_class_is_present_if_feature_is_enabled(self, browser):
        browser.login().visit()
        self.assertIn(
            'feature-bumblebee',
            browser.css('body').first.get('class').split(' '))
