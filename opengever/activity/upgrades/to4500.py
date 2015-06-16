from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


class ConvertActivitySummaryToText(SchemaMigration):

    profileid = 'opengever.activity'
    upgradeid = 4500

    def migrate(self):
        self.rename_tmp_column()
        self.add_new_column()

        self.migrate_data()

        self.make_summary_non_nullable()
        self.drop_tmp_column()

    def rename_tmp_column(self):
        self.op.alter_column('activities', 'summary',
                             new_column_name='tmp_summary',
                             existing_nullable=False,
                             existing_type=String(512))

    def add_new_column(self):
        self.op.add_column(
            'activities', Column('summary', Text, nullable=True))

    def migrate_data(self):
        activities_table = table(
            "activities",
            column("id"),
            column("tmp_summary"),
            column("summary"),
        )

        activities = self.connection.execute(
            activities_table.select()).fetchall()

        for activity in activities:
            self.execute(
                activities_table.update()
                .values(summary=activity.tmp_summary)
                .where(activities_table.columns.id == activity.id)
            )

    def make_summary_non_nullable(self):
        self.op.alter_column('activities', 'summary',
                             existing_type=Text, nullable=False)

    def drop_tmp_column(self):
        self.op.drop_column('activities', 'tmp_summary')
