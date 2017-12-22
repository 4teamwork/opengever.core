from opengever.base.date_time import utcnow_tz_aware
from opengever.base.interfaces import ISequenceNumber
from opengever.base.model import Base
from opengever.base.model import Session
from opengever.base.oguid import Oguid
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models import UNIT_ID_LENGTH
from opengever.ogds.models import USER_ID_LENGTH
from opengever.sqlcatalog.interfaces import ISQLRecord
from operator import attrgetter
from plone import api
from plone.uuid.interfaces import IUUID
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm.attributes import set_attribute
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implementer
import logging


LOG = logging.getLogger('opengever.sqlcatalog')


tables = [
    'catalog_document',
    'catalog_mail',
]


@implementer(ISQLRecord)
class CatalogRecordBase(Base):
    """Catalog records are entries in the SQL catalog, compareable
    with a "brain" or a "record" of the ZCatalog.

    All catalog record classes shall subclass the BaseCatalogRecord class.
    """

    __abstract__ = True

    oguid = Column(String(32), primary_key=True, index=True, nullable=False)
    admin_unit_id = Column(String(UNIT_ID_LENGTH), index=True, nullable=False)
    uuid = Column(String(32), unique=True, nullable=False, index=True)
    record_created = Column(DateTime, default=utcnow_tz_aware)
    record_modified = Column(DateTime, default=utcnow_tz_aware, onupdate=utcnow_tz_aware)

    created = Column(DateTime, index=True)
    modified = Column(DateTime, index=True)
    title = Column(String(256), index=True)
    id = Column(String(256))
    absolute_path = Column(String(512), index=True, nullable=False)
    relative_path = Column(String(512), index=True, nullable=False)
    review_state = Column(String(256))
    icon = Column(String(50))

    def __repr__(self):
        return '<Catalog record {} {!r}>'.format(type(self).__name__, self.oguid, self.title)

    @classmethod
    def created_indexer(kls, obj):
        return obj.created().asdatetime()

    @classmethod
    def modified_indexer(kls, obj):
        return obj.modified().asdatetime()

    @classmethod
    def absolute_path_indexer(kls, obj):
        return '/'.join(obj.getPhysicalPath())

    @classmethod
    def relative_path_indexer(kls, obj):
        return '/'.join(obj.getPhysicalPath()[2:])

    @classmethod
    def review_state_indexer(kls, obj):
        return api.content.get_state(obj)

    @classmethod
    def icon_indexer(kls, obj):
        return obj.getIcon()

    @classmethod
    def create_from(cls, obj):
        """Create a new record from an object.

        This classmethod must be called on the correct model and the caller must
        make sure that no record exists yet for this object.

        You probably want to use getUtility(ISQLCatalog).index(obj)
        """
        LOG.debug('Index {!r} for {!r}'.format(cls, obj))
        oguid = Oguid.for_object(obj)
        data = cls.get_data_for(obj)
        record = cls(oguid=oguid.id,
                     admin_unit_id=oguid.admin_unit_id,
                     uuid=IUUID(obj),
                     **data)
        Session.add(record)
        return record

    @classmethod
    def get_columns_to_index(cls):
        """Return a list of column objects for all columns to be indexed and reindex.

        Columns which must not change, such as oguid, admin id, uuid, must be excluded here.
        """
        return [column for column in cls.__table__.columns
                if column.name not in ('oguid', 'admin_unit_id', 'uuid',
                                       'record_created', 'record_modified')]

    @classmethod
    def get_data_for(cls, obj):
        """Return a dict of data to index in the record of a specific object.
        """
        return {column.name: cls.get_indexer_for_column(column)(obj)
                for column in cls.get_columns_to_index()}

    @classmethod
    def get_indexer_for_column(cls, column):
        """Return an indexer for a specific column.

        Register custom indexer by implementing a classmethod with the name
        "{coulumn name}_indexer", accepting the object and returning the value to be indexed.
        """
        return getattr(cls, '{}_indexer'.format(column.name), attrgetter(column.name))

    def reindex(self):
        """Reindex the current record.
        """
        LOG.warning('Index {!r} for {!r}'.format(self, self.get_object()))
        for key, value in self.get_data_for(self.get_object()).items():
            set_attribute(self, key, value)
        return self

    def get_object(self):
        """Return the object for the record.

        This method only works when the object is stored on this client.
        """
        return Oguid.parse(self.oguid).resolve_object()

    @property
    def Title(self):
        return self.title.encode('utf-8')

    def getPath(self):
        return self.absolute_path.encode('utf-8')

    def getURL(self):
        if self.admin_unit_id == get_current_admin_unit().id():
            return '/'.join((getSite().absolute_url(), self.relative_path.encode('utf-8')))
        else:
            raise NotImplementedError()


class DocumentishMixin(object):
    sequence_number = Column(Integer, index=True, nullable=False)
    document_author = Column(String(USER_ID_LENGTH), index=True)
    document_date = Column(DateTime, index=True)
    receipt_date = Column(DateTime, index=True)
    delivery_date = Column(DateTime, index=True)
    checked_out = Column(String(USER_ID_LENGTH), index=True)

    @classmethod
    def sequence_number_indexer(kls, obj):
        return getUtility(ISequenceNumber).get_number(obj)

    @classmethod
    def checked_out_indexer(kls, obj):
        manager = queryMultiAdapter((obj, obj.REQUEST), ICheckinCheckoutManager)
        if not manager:
            return ''

        return manager.get_checked_out_by() or ''


class DocumentCatalogRecord(DocumentishMixin, CatalogRecordBase):
    __tablename__ = 'catalog_document'
    portal_type = 'opengever.document.document'


class MailCatalogRecord(DocumentishMixin, CatalogRecordBase):
    __tablename__ = 'catalog_mail'
    portal_type = 'ftw.mail.mail'
