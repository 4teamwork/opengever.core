from opengever.meeting import is_word_meeting_implementation_enabled
from opengever.meeting.interfaces import IMeetingWrapper
from opengever.meeting.browser.meetings.zipexport import MeetingZipExport


class MeetingAppExport(MeetingZipExport):
    """Generate a Zip file and export it to the meeting app"""

    def __init__(self, context, request):
        super(MeetingAppExport, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        return ''

    def visible_in_actions_menu(self):
        """Returns ``True`` when the zip export action should be displayed
        in the actions menu.

        The action should only appear when we are on a meeting view and the
        word-meeting feature is enabled.
        """
        return IMeetingWrapper.providedBy(self.context) and \
            is_word_meeting_implementation_enabled()
