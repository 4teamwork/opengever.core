from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.testing import FunctionalTestCase
from plone import api
import transaction


class TestGeverLayoutPolicy(FunctionalTestCase):
    @browsing
    def test_bumblebee_feature_body_class_is_not_present_if_feature_is_disabled(self, browser):
        browser.login().visit()
        self.assertNotIn(
            'feature-bumblebee',
            browser.css('body').first.get('class').split(' '))

    @browsing
    def test_word_meeting_feature_presence(self, browser):
        browser.login()
        prefix = 'opengever.meeting.interfaces.IMeetingSettings'
        meeting_feature = prefix + '.is_feature_enabled'
        api.portal.set_registry_record(meeting_feature, True)

        word_feature = prefix + '.is_word_implementation_enabled'

        api.portal.set_registry_record(word_feature, False)
        transaction.commit()
        self.assertNotIn('feature-word-meeting',
                         browser.open().css('body').first.classes)

        api.portal.set_registry_record(word_feature, True)
        transaction.commit()
        self.assertIn('feature-word-meeting',
                      browser.open().css('body').first.classes)


class TestGeverLayoutPolicyBumblebeeFeature(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_bumblebee_feature_body_class_is_present_if_feature_is_enabled(self, browser):
        browser.login().visit()
        self.assertIn(
            'feature-bumblebee',
            browser.css('body').first.get('class').split(' '))
