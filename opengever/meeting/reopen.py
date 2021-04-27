from opengever.meeting.model import Meeting
from opengever.meeting.period import Period


class ReopenMeeting(object):

    def __init__(self, meeting):
        self.meeting = meeting
        self.period = Period.get_current(
            self.meeting.committee.resolve_committee(),
            self.meeting.start.date()
        )
        self.agenda_items = [
            item for item in self.meeting.agenda_items if not item.is_paragraph
        ]
        self.decision_numbers = [
            each.decision_number for each
            in self.agenda_items
            if each.decision_number is not None
        ]
        if self.decision_numbers:
            self.reset_decision_number = min(self.decision_numbers) - 1
        else:
            self.reset_decision_number = None

        self.meeting_number = self.meeting.meeting_number
        if self.meeting_number:
            self.reset_meeting_number = self.meeting_number - 1
        else:
            self.reset_meeting_number = None

    def get_errors(self):
        errors = []
        if self.meeting.workflow_state not in ('held', 'closed'):
            errors.append(u"Can't reopen meeting in state '{}'.".format(
                self.meeting.workflow_state)
            )
        if self.agenda_items and self.reset_decision_number is None:
            errors.append(
                u"Unexpected state, have agenda items but "
                u"can't reset decision number."
            )
        if self.reset_meeting_number is None:
            errors.append(u"Unexpected state, can't reset meeting number.")
        if errors:
            # return here to prevent invalid query
            return errors

        newer_held_meetings = Meeting.query.by_committee(
            self.meeting.committee).filter(
            Meeting.meeting_number > self.meeting_number).all()
        if newer_held_meetings:
            errors.append(u"The meetings '{}' need to be reopened first.".format(
                u"', '".join(each.get_title() for each in newer_held_meetings))
            )

        return errors

    def reopen_meeting(self):
        assert not self.get_errors()

        self.meeting.workflow_state = u'pending'
        self.meeting.meeting_number = None
        for agenda_item in self.meeting.agenda_items:
            agenda_item.workflow_state = u'pending'
            agenda_item.decision_number = None
        if self.reset_decision_number is not None:
            self.period.decision_sequence_number = self.reset_decision_number
        self.period.meeting_sequence_number = self.reset_meeting_number
