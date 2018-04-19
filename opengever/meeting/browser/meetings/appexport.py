from opengever.meeting import is_word_meeting_implementation_enabled
from opengever.meeting.interfaces import IMeetingWrapper
from opengever.meeting.browser.meetings.zipexport import MeetingZipExport
from opengever.meeting import _
from plone import api


class MeetingAppExport(MeetingZipExport):
    """Generate a Zip file and export it to the meeting app"""

    def __init__(self, context, request):
        super(MeetingAppExport, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):

        committee = self.context.model.committee.resolve_committee()

        if committee.meeting_app_export_url is None:
            msg = _(
                u'The committee ${committee} has no meeting app export URL.',
                mapping={'committee': committee.Title().decode('utf-8')})
            api.portal.show_message(msg, self.request, type='error')

            return self.request.RESPONSE.redirect(self.context.absolute_url())

        return ''

    def visible_in_actions_menu(self):
        """Returns ``True`` when the zip export action should be displayed
        in the actions menu.

        The action should only appear when we are on a meeting view and the
        word-meeting feature is enabled.
        """
        return IMeetingWrapper.providedBy(self.context) and \
            is_word_meeting_implementation_enabled()
