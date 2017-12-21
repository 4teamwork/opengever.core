from opengever.core.upgrade import SchemaMigration
from opengever.sqlcatalog.interfaces import ISQLCatalog
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
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
            Column('id', String(256)),
            Column('absolute_path', String(512), index=True, nullable=False),
            Column('relative_path', String(512), index=True, nullable=False),
            Column('review_state', String(255)),
            Column('icon', String(50)),
            Column('sequence_number', Integer, index=True, nullable=False),
            Column('document_author', String(255), index=True),
            Column('document_date', DateTime, index=True),
            Column('receipt_date', DateTime, index=True),
            Column('delivery_date', DateTime, index=True),
            Column('checked_out', String(255), index=True),
        )

        map(getUtility(ISQLCatalog).index,
            self.objects({'portal_type': 'opengever.document.document'},
                         'Index documents into SQL catalog.'))
