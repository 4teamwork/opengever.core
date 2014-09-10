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

    def make_org_unit_column_required(self):
        self.op.alter_column("clients", "users_group_id", nullable=False,
                             existing_type=String(30))
        self.op.alter_column("clients", "inbox_group_id", nullable=False,
                             existing_type=String(30))
        self.op.alter_column("clients", "admin_unit_id", nullable=False,
                             existing_type=String(30))

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
