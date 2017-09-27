from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Boolean
from sqlalchemy import String
from sqlalchemy.schema import Sequence


GROUP_ID_LENGTH = 255
UNIT_ID_LENGTH = 30
UNIT_TITLE_LENGTH = 255


class AddTeamModel(SchemaMigration):
    """Add team model.
    """

    def migrate(self):
        self.add_team_table()

    def add_team_table(self):
        self.op.create_table(
            'teams',
            Column('id', Integer, Sequence('teams_id_seq'), primary_key=True),
            Column('title', String(UNIT_TITLE_LENGTH), nullable=False),
            Column('active', Boolean, default=True),
            Column('groupid', String(GROUP_ID_LENGTH),
                   ForeignKey('groups.groupid'), nullable=False),
            Column('org_unit_id', String(UNIT_ID_LENGTH),
                   ForeignKey('org_units.unit_id'), nullable=False))
