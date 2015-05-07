from opengever.activity.hooks import insert_default_settings
from opengever.core.upgrade import SchemaMigration


class InsertDefaultSettings(SchemaMigration):

    profileid = 'opengever.activity'
    upgradeid = 4301

    def migrate(self):
        insert_default_settings(self.portal)
