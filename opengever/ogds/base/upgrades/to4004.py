from opengever.core.upgrade import DeactivatedFKConstraint
from opengever.core.upgrade import SchemaMigration
from sqlalchemy import String


class MigrateAdminUnitOrgUnitSchema(SchemaMigration):

    profileid = 'opengever.ogds.base'
    upgradeid = 4004

    def migrate(self):
        self.drop_org_unit_columns()
        self.make_org_unit_column_required()
        self.make_admin_unit_columns_required()
        self.rename_clients_table_to_org_units()

    def drop_org_unit_columns(self):
        self.op.drop_column('clients', 'ip_address')
        self.op.drop_column('clients', 'site_url')
        self.op.drop_column('clients', 'public_url')

    def make_fk_column_required(self, tablename, column_name, fk_name,
                                fk_table_name, fk_column_name, length=30):
        """Make a column that is the source of a foreign key constraint
        required.

        MySQL might block an alter column when a foreign key constraint has
        been specified, so we must drop and re-create the constraint.

        """
        with DeactivatedFKConstraint(self.op, fk_name, tablename,
                                     fk_table_name,
                                     [column_name], [fk_column_name]):
            self.op.alter_column(tablename, column_name, nullable=False,
                                 existing_type=String(length))

    def make_org_unit_column_required(self):
        self.make_fk_column_required("clients", "users_group_id",
                                     "clients_ibfk_1", "groups", "groupid")
        self.make_fk_column_required("clients", "inbox_group_id",
                                     "clients_ibfk_2", "groups", "groupid")
        self.make_fk_column_required("clients", "admin_unit_id",
                                     "clients_ibfk_3",
                                     "admin_units", "unit_id")

    def make_admin_unit_columns_required(self):
        self.op.alter_column("admin_units", "ip_address", nullable=False,
                             existing_type=String(50))
        self.op.alter_column("admin_units", "site_url", nullable=False,
                             existing_type=String(50))
        self.op.alter_column("admin_units", "public_url", nullable=False,
                             existing_type=String(50))

    def rename_clients_table_to_org_units(self):
        self.op.rename_table('clients', 'org_units')
        self.op.alter_column('org_units', 'client_id',
                             new_column_name='unit_id',
                             existing_nullable=False,
                             existing_type=String(30))
