from opengever.core.upgrade import SchemaMigration
from opengever.sqlcatalog.interfaces import ISQLCatalog
from sqlalchemy import Column
from sqlalchemy import String
from zope.component import getUtility


class AddDocumentCatalogRecord(SchemaMigration):
    """Add document catalog record.
    """

    def migrate(self):
        self.op.create_table(
            'catalog_document',
            Column('oguid', String(32), primary_key=True, index=True, nullable=False),
            Column('admin_unit_id', String(30), index=True, nullable=False),
            Column('uuid', String(32), unique=True, nullable=False, index=True),
            Column('title', String(256), index=True),
            Column('absolute_path', String(512), index=True, nullable=False),
            Column('relative_path', String(512), index=True, nullable=False))

        map(getUtility(ISQLCatalog).index,
            self.objects({'portal_type': 'opengever.document.document'},
                         'Index documents into SQL catalog.'))
