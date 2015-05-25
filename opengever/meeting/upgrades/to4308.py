from opengever.core.upgrade import SchemaMigration
from sqlalchemy import String


class DecreaseMeetingColumnLengths(SchemaMigration):
    """Decrease lengths for several VARCHAR columns in 'meeting' models in
    preparation for factoring out common column lengths to constants.
    """

    profileid = 'opengever.meeting'
    upgradeid = 4308

    def migrate(self):
        self.decrease_meeting_workflow_state_length()
        self.decrease_member_firstname_length()
        self.decrease_member_lastname_length()
        self.decrease_member_email_length()
        self.decrease_proposal_workflow_state_length()
        self.decrease_proposalhistory_userid_length()

    def decrease_meeting_workflow_state_length(self):
        # Match WORKFLOW_STATE_LENGTH
        self.op.alter_column('meetings',
                             'workflow_state',
                             type_=String(255),
                             existing_nullable=False,
                             existing_type=String(256))

    def decrease_member_firstname_length(self):
        # Match FIRSTNAME_LENGTH
        self.op.alter_column('members',
                             'firstname',
                             type_=String(255),
                             existing_nullable=False,
                             existing_type=String(256))

    def decrease_member_lastname_length(self):
        # Match LASTNAME_LENGTH
        self.op.alter_column('members',
                             'lastname',
                             type_=String(255),
                             existing_nullable=False,
                             existing_type=String(256))

    def decrease_member_email_length(self):
        # Match EMAIL_LENGTH
        self.op.alter_column('members',
                             'email',
                             type_=String(255),
                             existing_nullable=True,
                             existing_type=String(256))

    def decrease_proposal_workflow_state_length(self):
        # Match WORKFLOW_STATE_LENGTH
        self.op.alter_column('proposals',
                             'workflow_state',
                             type_=String(255),
                             existing_nullable=False,
                             existing_type=String(256))

    def decrease_proposalhistory_userid_length(self):
        # Match USER_ID_LENGTH
        self.op.alter_column('proposalhistory',
                             'userid',
                             type_=String(255),
                             existing_nullable=False,
                             existing_type=String(256))
