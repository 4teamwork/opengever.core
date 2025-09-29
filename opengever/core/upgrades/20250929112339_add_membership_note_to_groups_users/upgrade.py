from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import UnicodeText


class AddMembershipNoteToGroupsUsers(SchemaMigration):
    """Add membership note to Groups Users.
    """

    def migrate(self):
        # Reflect current schema
        self.refresh_metadata()

        table = self.metadata.tables.get('groups_users')
        if table is None:
            return

        if 'note' in table.columns:
            return

        if self.is_oracle:
            self.execute(u"ALTER TABLE groups_users ADD (note CLOB NULL)")
        else:
            self.op.add_column(
                'groups_users',
                Column('note', UnicodeText, nullable=True),
            )

        self.refresh_metadata()
