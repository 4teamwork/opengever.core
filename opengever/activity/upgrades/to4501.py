from opengever.base.model import Base
from opengever.base.model import create_session
from opengever.base.model import get_tables
from opengever.core.upgrade import SchemaMigration
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
        Base.metadata.create_all(
            create_session().bind,
            tables=get_tables(['activities_translation']),
            checkfirst=True)

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
