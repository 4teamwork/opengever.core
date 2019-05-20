from opengever.core.upgrade import SchemaMigration
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
import json


class MakeSubjectsColumnNonSortable(SchemaMigration):
    """Make subjects column non sortable.
    """

    def migrate(self):
        _table = table('dictstorage', column("key"), column('value'))

        items = self.connection.execute(_table.select()).fetchall()
        for item in items:
            if item.value is None:
                continue

            try:
                value = json.loads(item.value)
            except ValueError:
                # The dictstorage contains non json values, the ldap
                # syncronisation timestampe for example
                continue

            for col in value.get('columns', []):
                if col.get('id') == 'Subject':
                    col['sortable'] = False

            new_value = json.dumps(value)
            self.execute(_table.update()
                         .values(value=new_value)
                         .where(_table.columns.key == item.key))
