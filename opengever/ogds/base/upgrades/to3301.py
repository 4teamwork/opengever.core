from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import String


class CreateAdminUnitTable(SchemaMigration):

    profileid = 'opengever.ogds.base'
    upgradeid = 3301

    def migrate(self):
        self.create_admin_units_table()
        self.create_admin_unit_id_column()
        self.refresh_medatata()

        self.migrate_data()

        self.create_admin_unit_id_column_constraint()

    def create_admin_units_table(self):
        if self.metadata.tables.get('admin_units') is not None:
            return

        self.op.create_table(
            'admin_units',
            Column('unit_id', String(30), primary_key=True),
            Column('title', String(30)),
            Column('enabled', Boolean(), default=True),
            Column('ip_address', String(50)),
            Column('site_url', String(100)),
            Column('public_url', String(100)),
        )

    def create_admin_unit_id_column(self):
        client_table = self.metadata.tables.get('clients')
        if client_table.columns.get('admin_unit_id') is not None:
            return

        self.op.add_column(
            'clients',
            Column('admin_unit_id', String(30))
        )

    def create_admin_unit_id_column_constraint(self):
        self.op.alter_column("clients", "admin_unit_id", nullable=False,
                             existing_type=String(30))

        for fk in self.metadata.tables.get('clients').foreign_keys:
            if fk.name == "clients_ibfk_3":
                assert fk.column.name == u'unit_id', \
                    'unexpected foreign key constraint setup'
                return

        self.op.create_foreign_key("clients_ibfk_3",
                                   "clients", "admin_units",
                                   ["admin_unit_id"], ["unit_id"])

    def migrate_data(self):
        admin_units_table = self.metadata.tables.get('admin_units')
        client_table = self.metadata.tables.get('clients')

        clients = self.connection.execute(client_table.select()).fetchall()
        for row in clients:
            existing_clients = self.execute(
                admin_units_table.select()
                .where(admin_units_table.c.unit_id == row.client_id)
            ).fetchall()

            if len(existing_clients) > 0:
                continue

            admin_unit_data = dict(
                unit_id=row.client_id,
                title=row.title,
                enabled=row.enabled,
                ip_address=row.ip_address,
                site_url=row.site_url,
                public_url=row.public_url,
            )
            self.execute(
                admin_units_table.insert().values(**admin_unit_data)
            )
            self.execute(
                client_table.update()
                .values(admin_unit_id=row.client_id)
                .where(client_table.c.client_id == row.client_id)
            )
