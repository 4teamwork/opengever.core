from alembic.migration import MigrationContext
from alembic.operations import Operations
from ftw.upgrade import UpgradeStep
from opengever.ogds.base.utils import create_session
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String


class MigrateTaskTable(UpgradeStep):
    def __call__(self):
        self.setup_db()
        self.migrate()

    def setup_db(self):
        session = create_session()
        engine = session.bind
        self.connection = engine.connect()
        self.op = Operations(MigrationContext.configure(self.connection))
        self.metadata = MetaData(engine, reflect=True)

    def migrate(self):
        self.drop_unique_constraint()
        self.alter_columns()
        self.create_issuing_orgunit_column()
        self.add_unique_constraint()

    def drop_unique_constraint(self):
        if self._has_index('client_id', 'tasks'):
            self.op.drop_constraint('client_id', 'tasks', 'unique')

    def add_unique_constraint(self):
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
        tasks_table = self.metadata.tables.get('tasks')
        if tasks_table.columns.get('issuing_org_unit') is not None:
            return

        self.op.add_column(
            'tasks',
            Column('issuing_org_unit', String(30), index=True, nullable=False)
        )
