from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Boolean
from sqlalchemy import Column


class AddActiveColumnToGroup(SchemaMigration):
    """Add `active` column to OGDS `Group` model.

    (Upgrade-step for corresponding change in opengever.ogds.models)
    """

    profileid = 'opengever.ogds.base'
    upgradeid = 4302

    def migrate(self):
        self.add_active_column()

    def add_active_column(self):
        self.op.add_column('groups', Column('active', Boolean, default=True))
