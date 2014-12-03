from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String


class MigrateTaskTable(SchemaMigration):

    profileid = 'opengever.globalindex'
    upgradeid = 4000

    def migrate(self):
        self.drop_unique_constraint()
        self.alter_columns()
        self.create_issuing_orgunit_column()
        self.add_unique_constraint()
        self.migrate_issuing_orgunit_data()
        self.make_issuing_orgunit_required()

    def drop_unique_constraint(self):
        # oracle can handle column renames with unique constraints
        if self.is_oracle:
            return

        if self._has_index('client_id', 'tasks'):
            self.op.drop_constraint('client_id', 'tasks', 'unique')

    def add_unique_constraint(self):
        # oracle can handle column renames with unique constraints
        if self.is_oracle:
            return

        if not self._has_index('admin_unit_id', 'tasks'):
            self.op.create_unique_constraint('admin_unit_id', 'tasks',
                                             ['admin_unit_id', 'int_id'])

    def alter_columns(self):
        tasks_table = self.metadata.tables.get('tasks')
        self._alter_column(tasks_table, 'client_id', 'admin_unit_id')
        self._alter_column(tasks_table, 'assigned_client', 'assigned_org_unit')
        self.op.alter_column('tasks', 'int_id',
                             nullable=False, existing_nullable=True,
                             existing_autoincrement=False,
                             existing_type=Integer)

    def _alter_column(self, table, old_name, new_name):
        if table.columns.get(old_name) is None:
            return
        if table.columns.get(new_name) is not None:
            return

        self.op.alter_column(table.name, old_name, new_column_name=new_name,
                             type_=String(30),
                             existing_type=String(20),
                             nullable=False,
                             existing_nullable=True,
                             existing_autoincrement=False)

    def _has_index(self, indexname, tablename):
        table = self.metadata.tables.get(tablename)
        for index in table.indexes:
            if index.name == indexname:
                return True
        return False

    def create_issuing_orgunit_column(self):
        self.op.add_column(
            'tasks',
            Column('issuing_org_unit', String(30), index=True, nullable=True)
        )

    def make_issuing_orgunit_required(self):
        self.op.alter_column('tasks', 'issuing_org_unit', nullable=False,
                             existing_type=String(30))

    def _lookup_predecessor_admin_unit(self, task_table, row):
        while row.predecessor_id:
            row = self.connection.execute(
                task_table.select().where(
                    task_table.c.id == row.predecessor_id)
                ).fetchone()
        return row.admin_unit_id

    def migrate_issuing_orgunit_data(self):
        self.metadata.clear()
        self.metadata.reflect()

        task_table = self.metadata.tables.get('tasks')
        tasks = self.connection.execute(task_table.select()).fetchall()
        for row in tasks:
            if row.predecessor_id:
                issuing_org_unit = self._lookup_predecessor_admin_unit(
                    task_table, row)
            else:
                issuing_org_unit = row.admin_unit_id
            self.execute(
                task_table.update()
                .values(issuing_org_unit=issuing_org_unit)
                .where(task_table.c.id == row.id)
            )
