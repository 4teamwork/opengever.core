from opengever.meeting import is_meeting_feature_enabled
from Products.Five.browser import BrowserView


class MeetingFeatureEnabledView(BrowserView):

    def __call__(self):
        return is_meeting_feature_enabled()
