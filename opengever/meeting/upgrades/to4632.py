from opengever.base.utils import get_preferred_language_code
from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


class AddRepositoryFolderColumns(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4632

    def migrate(self):
        self.add_columns()
        self.migrate_data()
        self.make_columns_non_nullable()

    def add_columns(self):
        self.op.add_column(
            'proposals',
            Column('repository_folder_title', Text, nullable=True))
        self.op.add_column(
            'proposals',
            Column('language', String(8), nullable=True))

    def migrate_data(self):
        """Temporarily insert placeholders as repository_folder_title,
        the real value will be inserted by the 4633 upgradestep.
        """
        default_language = get_preferred_language_code()

        proposal_table = table("proposals",
                               column("id"),
                               column("repository_folder_title"),
                               column("language"))

        self.execute(
            proposal_table.update().values(repository_folder_title=u'-'))
        self.execute(
            proposal_table.update().values(language=default_language))

    def make_columns_non_nullable(self):
        self.op.alter_column('proposals', 'repository_folder_title',
                             existing_type=Text, nullable=False)
        self.op.alter_column('proposals', 'language',
                             existing_type=String(8), nullable=False)
