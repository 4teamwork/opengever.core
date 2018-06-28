from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


class ChangePhysicalPathColumnType(SchemaMigration):
    """Change physical path column type.
    """

    def migrate(self):
        self.alter_column(
            'tasks',
            'physical_path',
            type_=Text,
            existing_nullable=True,
            existing_type=String(256))

        self.alter_column(
            'proposals',
            'physical_path',
            type_=Text,
            existing_nullable=False,
            existing_type=String(256))

        self.alter_column(
            'proposals',
            'submitted_physical_path',
            type_=Text,
            existing_nullable=True,
            existing_type=String(256))

        self.alter_column(
            'committees',
            'physical_path',
            type_=Text,
            existing_nullable=False,
            existing_type=String(256))

    def alter_column(self, table_name, column_name, type_, existing_nullable, existing_type):  # noqa

        if self.is_oracle:
            self.alter_oracle_column(table_name, column_name,
                                     type_, existing_nullable, existing_type)
        else:
            self.op.alter_column(
                table_name, column_name, type_=type_,
                existing_nullable=existing_nullable,
                existing_type=existing_type)

    def alter_oracle_column(self, table_name, column_name, type_, existing_nullable, existing_type):  # noqa
        tmp_column_name = 'tmp{}'.format(column_name)

        # rename existing column
        self.op.alter_column(table_name,
                             column_name,
                             new_column_name=tmp_column_name,
                             existing_nullable=existing_nullable,
                             existing_type=existing_type)

        # add new column with the new type
        self.op.add_column(
            table_name, Column(column_name, type_, nullable=True))

        # migrate_data
        _table = table(table_name,
            column("id"),
            column(tmp_column_name),
            column(column_name),
        )

        items = self.connection.execute(_table.select()).fetchall()
        for item in items:
            self.execute(
                _table.update()
                .values(**{column_name: getattr(item, tmp_column_name)})
                .where(_table.columns.id == item.id)
            )

        # make column non nullable
        if not existing_nullable:
            self.op.alter_column(
                table_name, column_name, existing_type=type_, nullable=False)

        # drop_tmp_column
        self.op.drop_column(table_name, tmp_column_name)
