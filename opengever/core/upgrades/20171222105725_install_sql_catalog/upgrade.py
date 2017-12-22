from opengever.base.date_time import utcnow_tz_aware
from opengever.core.upgrade import SchemaMigration
from opengever.sqlcatalog.interfaces import ISQLCatalog
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from zope.component import getUtility


class InstallSQLCatalog(SchemaMigration):
    """Install SQL catalog and index catalog records.
    """

    def migrate(self):
        self.install_documents()
        self.install_mails()
        self.install_repository_root()
        self.install_repository_folder()

    def install_documents(self):
        self.op.create_table(
            'catalog_document',
            Column('oguid', String(32), primary_key=True, index=True, nullable=False),
            Column('admin_unit_id', String(30), index=True, nullable=False),
            Column('uuid', String(32), unique=True, nullable=False, index=True),
            Column('record_created', DateTime, default=utcnow_tz_aware),
            Column('record_modified', DateTime, default=utcnow_tz_aware, onupdate=utcnow_tz_aware),
            Column('created', DateTime, index=True),
            Column('modified', DateTime, index=True),
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
        self.index_objects('opengever.document.document')

    def install_mails(self):
        self.op.create_table(
            'catalog_mail',
            Column('oguid', String(32), primary_key=True, index=True, nullable=False),
            Column('admin_unit_id', String(30), index=True, nullable=False),
            Column('uuid', String(32), unique=True, nullable=False, index=True),
            Column('record_created', DateTime, default=utcnow_tz_aware),
            Column('record_modified', DateTime, default=utcnow_tz_aware, onupdate=utcnow_tz_aware),
            Column('created', DateTime, index=True),
            Column('modified', DateTime, index=True),
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
        self.index_objects('ftw.mail.mail')

    def install_repository_root(self):
        self.op.create_table(
            'catalog_repository_root',
            Column('oguid', String(32), primary_key=True, index=True, nullable=False),
            Column('admin_unit_id', String(30), index=True, nullable=False),
            Column('uuid', String(32), unique=True, nullable=False, index=True),
            Column('record_created', DateTime, default=utcnow_tz_aware),
            Column('record_modified', DateTime, default=utcnow_tz_aware, onupdate=utcnow_tz_aware),
            Column('created', DateTime, index=True),
            Column('modified', DateTime, index=True),
            Column('title', String(256), index=True),
            Column('id', String(256)),
            Column('absolute_path', String(512), index=True, nullable=False),
            Column('relative_path', String(512), index=True, nullable=False),
            Column('review_state', String(255)),
            Column('icon', String(50)),
        )
        self.index_objects('opengever.repository.repositoryroot')

    def install_repository_folder(self):
        self.op.create_table(
            'catalog_repository_folder',
            Column('oguid', String(32), primary_key=True, index=True, nullable=False),
            Column('admin_unit_id', String(30), index=True, nullable=False),
            Column('uuid', String(32), unique=True, nullable=False, index=True),
            Column('record_created', DateTime, default=utcnow_tz_aware),
            Column('record_modified', DateTime, default=utcnow_tz_aware, onupdate=utcnow_tz_aware),
            Column('created', DateTime, index=True),
            Column('modified', DateTime, index=True),
            Column('title', String(256), index=True),
            Column('id', String(256)),
            Column('absolute_path', String(512), index=True, nullable=False),
            Column('relative_path', String(512), index=True, nullable=False),
            Column('review_state', String(255)),
            Column('icon', String(50)),
        )
        self.index_objects('opengever.repository.repositoryfolder')

    def index_objects(self, portal_type):
        map(getUtility(ISQLCatalog).index,
            self.objects({'portal_type': portal_type},
                         'SQL catalog: index {}'.format(portal_type)))
