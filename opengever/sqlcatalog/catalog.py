from Acquisition import aq_base
from opengever.base.model import Session
from opengever.base.oguid import Oguid
from opengever.sqlcatalog.interfaces import ISQLCatalog
from opengever.sqlcatalog.record import CatalogRecordBase
from zope.interface import implementer


@implementer(ISQLCatalog)
class SQLCatalog(object):

    def is_supported(self, obj):
        return self.get_model_for(obj) is not None

    def index(self, obj):
        record = self.get_record_for(obj)
        if record is None:
            return self.get_model_for(obj).create_from(obj)
        else:
            return record.reindex()

    def get_record_for(self, obj):
        if not self.is_supported(obj):
            raise ValueError('Unsupported object {!r}'.format(obj))

        oguid = Oguid.for_object(obj, register=True)
        return Session.query(self.get_model_for(obj)).filter_by(oguid=oguid.id).first()

    def get_model_for(self, obj):
        portal_type = getattr(aq_base(obj), 'portal_type', None)
        for model in CatalogRecordBase.__subclasses__():
            if model.portal_type == portal_type:
                return model
        return None

    def get_model_for_portal_type(self, portal_type):
        for model in CatalogRecordBase.__subclasses__():
            if model.portal_type == portal_type:
                return model
        return None
