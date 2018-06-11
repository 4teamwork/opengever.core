from ftw.upgrade import UpgradeStep
from opengever.meeting.model import Meeting


class RemoveLockOnExistingProtocols(UpgradeStep):
    """Remove lock on existing protocols.
    """

    def __call__(self):
        for committee in self.objects(
                {'portal_type': 'opengever.meeting.committee'},
                'Unlock meeting protocols'):
            committee_model = committee.load_model()
            meetings = Meeting.query.pending_meetings(committee_model)
            for meeting in meetings:
                if meeting.has_protocol_document() and meeting.protocol_document.is_locked():
                    meeting.protocol_document.unlock_document()
