from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


DEFAULT_LOCALE = 'de'


class AddI18nSupportForActivities(SchemaMigration):

    profileid = 'opengever.activity'
    upgradeid = 4501

    def migrate(self):
        self.add_activity_translations_table()
        self.migrate_data()
        self.remove_non_translated_columns()

    def add_activity_translations_table(self):
        self.op.create_table(
            'activities_translation',
            Column("id", Integer, primary_key=True, autoincrement=False),
            Column("locale", String(10), primary_key=True),
            Column('title', Text),
            Column('label', Text),
            Column('summary', Text),
            Column('description', Text),
        )
        self.op.create_foreign_key(
            'activities_trnsltn_id_fkey',
            'activities_translation', 'activities',
            ['id'], ['id'],
            ondelete='CASCADE')

    def migrate_data(self):
        activities_table = table(
            "activities",
            column("id"),
            column("kind"),
            column("summary"),
            column("title"),
            column("description"),
        )

        activities_translation_table = table(
            "activities_translation",
            column("id"),
            column("locale"),
            column("title"),
            column("label"),
            column("summary"),
            column("description"),
        )

        activities = self.connection.execute(
            activities_table.select()).fetchall()
        for activity in activities:
            self.execute(
                activities_translation_table.insert(
                    values={'id': activity.id,
                            'locale': DEFAULT_LOCALE,
                            'title': activity.title,
                            # the label column is new so we use the kind
                            # for existing entries
                            'label': activity.kind,
                            'summary': activity.summary,
                            'description': activity.description}))

    def remove_non_translated_columns(self):
        self.op.drop_column('activities', 'title')
        self.op.drop_column('activities', 'summary')
        self.op.drop_column('activities', 'description')
