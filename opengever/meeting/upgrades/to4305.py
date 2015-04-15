from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer


class AddGeneratedExcerpts(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4305

    def migrate(self):
        self.create_meeting_excerpts_secondary_table()

    def create_meeting_excerpts_secondary_table(self):
        self.op.create_table(
            'meeting_excerpts',
            Column('meeting_id', Integer, ForeignKey('meetings.id')),
            Column('document_id', Integer, ForeignKey('generateddocuments.id'))
        )
