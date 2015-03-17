from opengever.core.upgrade import SchemaMigration
from opengever.ogds.base.utils import get_current_admin_unit
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Time
from sqlalchemy.schema import Sequence
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class AddMeetingTable(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4200

    def migrate(self):
        self.create_meeting_table()
        self.create_agenda_item_table()
        self.add_proposal_columns()
        self.add_committee_columns()

    def create_meeting_table(self):
        self.op.create_table(
            'meetings',
            Column("id", Integer, Sequence("meeting_id_seq"), primary_key=True),
            Column("committee_id", Integer, ForeignKey('committees.id'), nullable=False),
            Column("location", String(256)),
            Column("date", Date, nullable=False),
            Column("start_time", Time),
            Column("end_time", Time),
            Column("workflow_state", String(256), nullable=False, default='pending')
        )

    def create_agenda_item_table(self):
        self.op.create_table(
            'agendaitems',
            Column("id", Integer, Sequence("agendaitems_id_seq"), primary_key=True),
            Column("meeting_id", Integer, ForeignKey('meetings.id'), nullable=False),
            Column("proposal_id", Integer, ForeignKey('proposals.id')),
            Column("title", Text),
            Column('number', String(16)),
            Column('is_paragraph', Boolean, nullable=False, default=False),
            Column("sort_order", Integer, nullable=False, default=0),
        )

    def add_proposal_columns(self):
        self.op.add_column('proposals',
                           Column('submitted_physical_path', String(256)))
        self.op.add_column('proposals',
                           Column('considerations', Text))
        self.op.add_column('proposals',
                           Column('proposed_action', Text))

    def add_committee_columns(self):
        """Careful, when committee objects/records have been created
        this works only under the assumption that this upgrade is run in a
        deployment with exactly one plone instance. When no objects/records
        have been created the upgrade can be safely run in a deployment with
        multiple instances.

        Some hints for further debugging if this upgrade fails and complains
        about null-values in the `physical_path` column:
        - verify that you are really runing only one deployment
        - verify that there are no orphaned committees in your sql-database
          (orphaned means that the corresponding plone content-type has been
           removed without deleting the sql record)

        """
        self.add_physical_path_column()
        self.migrate_commitee_data()
        self.make_physical_path_column_non_nullable()

    def add_physical_path_column(self):
        self.op.add_column('committees',
                           Column('physical_path', String(256)))

    def migrate_commitee_data(self):
        query = {'object_provides': 'opengever.meeting.committee.ICommittee'}
        msg = 'Add physical_path to committees'
        committee_table = table(
            "committees",
            column("int_id"),
            column("admin_unit_id"),
            column("physical_path"),
        )

        for obj in self.objects(query, msg):
            int_id = getUtility(IIntIds).queryId(obj)
            admin_unit_id = get_current_admin_unit().id()

            self.execute(committee_table.update()
                         .values(physical_path=obj.get_physical_path())
                         .where(committee_table.c.int_id == int_id)
                         .where(committee_table.c.admin_unit_id == admin_unit_id))

    def make_physical_path_column_non_nullable(self):
        self.op.alter_column('committees', 'physical_path', nullable=False,
                             existing_type=String(256))
