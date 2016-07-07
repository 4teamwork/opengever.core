from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String


class AddParticipationModel(SchemaMigration):
    """Add participation models.
    """

    def migrate(self):
        self.create_participations_table()
        self.create_participation_roles_table()

    def create_participations_table(self):
        self.op.create_table(
            'participations',
            Column("id", Integer, primary_key=True),
            Column("contact_id", Integer, ForeignKey('contacts.id'), nullable=False),
            Column("dossier_admin_unit_id", String(30), nullable=False),
            Column("dossier_int_id", Integer, nullable=False)
        )

    def create_participation_roles_table(self):
        self.op.create_table(
            'participation_roles',
            Column("id", Integer, primary_key=True),
            Column("participation_id", Integer, ForeignKey('participations.id'), nullable=False),
            Column("role", String(255), nullable=False)
        )
