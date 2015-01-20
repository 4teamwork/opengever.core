from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.testing import FunctionalTestCase


class TestDisabledMeetingFeature(FunctionalTestCase):

    def test_meeting_feature_is_disabled(self):
        view = self.portal.restrictedTraverse('is_meeting_feature_enabled')
        self.assertFalse(view())


class TestEnabledMeetingFeature(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def test_meeting_feature_is_enabled(self):
        view = self.portal.restrictedTraverse('is_meeting_feature_enabled')
        self.assertTrue(view())
