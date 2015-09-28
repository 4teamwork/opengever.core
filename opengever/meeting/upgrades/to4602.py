from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Text
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


class AddDossierReferenceNumberColumn(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4602

    def migrate(self):
        self.add_dossier_reference_number_column()
        self.migrate_data()
        self.make_dossier_reference_number_nullable()

    def add_dossier_reference_number_column(self):
        self.op.add_column(
            'proposals',
            Column('dossier_reference_number', Text, nullable=True))

    def migrate_data(self):
        """Temporarily insert placeholders as dossier_reference_numbers,
        the real value will be inserted by the 4603 upgradestep.
        """
        proposal_table = table("proposals",
                               column("id"),
                               column("dossier_reference_number"))

        self.execute(
            proposal_table.update().values(dossier_reference_number=u'-'))

    def make_dossier_reference_number_nullable(self):
        self.op.alter_column('proposals', 'dossier_reference_number',
                             existing_type=Text, nullable=False)
