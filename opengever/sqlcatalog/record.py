from opengever.base.model import Base
from opengever.base.model import Session
from opengever.base.oguid import Oguid
from opengever.ogds.models import UNIT_ID_LENGTH
from operator import attrgetter
from plone.uuid.interfaces import IUUID
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.orm.attributes import set_attribute
import logging


LOG = logging.getLogger('opengever.sqlcatalog')


class CatalogRecordBase(Base):
    """Catalog records are entries in the SQL catalog, compareable
    with a "brain" or a "record" of the ZCatalog.

    All catalog record classes shall subclass the BaseCatalogRecord class.
    """

    __abstract__ = True

    oguid = Column(String(32), primary_key=True, index=True, nullable=False)
    admin_unit_id = Column(String(UNIT_ID_LENGTH), index=True, nullable=False)
    uuid = Column(String(32), unique=True, nullable=False, index=True)

    title = Column(String(256), index=True)
    absolute_path = Column(String(512), index=True, nullable=False)
    relative_path = Column(String(512), index=True, nullable=False)

    def __repr__(self):
        return '<Catalog record {} {!r}>'.format(type(self).__name__, self.guid, self.title)

    @classmethod
    def absolute_path_indexer(kls, obj):
        return '/'.join(obj.getPhysicalPath())

    @classmethod
    def relative_path_indexer(kls, obj):
        return '/'.join(obj.getPhysicalPath()[2:])

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
                if column.name not in ('oguid', 'admin_unit_id', 'uuid')]

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
        for key, value in self.get_data_for(self.get_object()).items():
            set_attribute(self, key, value)
        return self

    def get_object(self):
        """Return the object for the record.

        This method only works when the object is stored on this client.
        """
        return Oguid.parse(self.oguid).resolve_object()


class DocumentCatalogRecord(CatalogRecordBase):
    __tablename__ = 'catalog_document'
    portal_type = 'opengever.document.document'
