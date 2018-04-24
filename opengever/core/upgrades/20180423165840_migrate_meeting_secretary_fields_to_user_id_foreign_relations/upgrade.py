from opengever.core.upgrade import SchemaMigration
from opengever.meeting.model import Member
from opengever.ogds.models.user import User
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
from uuid import uuid4


USER_ID_LENGTH = 255


class MigrateMeetingSecretaryFieldsToUserIdForeignRelations(SchemaMigration):
    """Migrate meeting secretary fields to user id foreign relations."""

    def migrate(self):
        # Add a temp secretary id column to meetings
        new_secretary_id = Column('new_secretary_id', String(USER_ID_LENGTH), ForeignKey(User.userid))
        self.op.add_column('meetings', new_secretary_id)
        # Populate temp secretary column - user if match else new inactive user
        meetings_table = table(
            'meetings',
            column('id'),
            column('secretary_id'),
            column('new_secretary_id'),
            )
        meetings = self.connection.execute(meetings_table.select()).fetchall()
        for meeting in meetings:
            if meeting.secretary_id:
                member = Member.query.get(meeting.secretary_id)
                if member:
                    user = User.query.filter(User.firstname == member.firstname, User.lastname == member.lastname).first()
                    if not user:
                        # We have to create an inactive user for the member
                        userid = uuid4().hex
                        user = User(userid)
                        user.active = False
                        user.firstname = member.firstname
                        user.lastname = member.lastname
                        user.email = member.email
                        self.session.add(user)
                        self.session.flush()
                    self.execute(
                        meetings_table.update()
                        .values(new_secretary_id=user.userid)
                        .where(meetings_table.columns.id == meeting.id)
                        )
        # Drop old secretary column
        self.op.drop_column('meetings', 'secretary_id')
        # Rename temp secretary column
        self.op.alter_column('meetings', 'new_secretary_id', new_column_name='secretary_id')
