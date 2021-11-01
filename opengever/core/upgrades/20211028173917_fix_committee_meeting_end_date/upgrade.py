from opengever.core.upgrade import SchemaMigration
from opengever.meeting.model.meeting import Meeting


class FixCommitteeMeetingEndDate(SchemaMigration):
    """Fix committee meeting end date.
    """

    def migrate(self):
        meetings = self.session.query(Meeting).filter(
            Meeting.end != None).filter(Meeting.start >= Meeting.end).all()  # noqa
        for meeting in meetings:
            meeting.end = None
