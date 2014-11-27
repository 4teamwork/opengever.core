from five import grok
from opengever.meeting import is_meeting_feature_enabled
from zope.interface import Interface


class MeetingFeatureEnabledView(grok.View):
    grok.context(Interface)
    grok.name('is_meeting_feature_enabled')
    grok.require('zope2.View')

    def render(self):
        return is_meeting_feature_enabled()
