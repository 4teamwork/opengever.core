from opengever.sqlcatalog.interfaces import ISQLRecord
from plone.app.contentlisting.contentlisting import BaseContentListingObject
from plone.app.contentlisting.interfaces import IContentListingObject
from zope.component import adapter
from zope.interface import implementer


@implementer(IContentListingObject)
@adapter(ISQLRecord)
class SQLRecordContentListing(BaseContentListingObject):

    def __init__(self, record):
        self.record = record

    def getId(self):
        return self.record.id

    def getObject(self):
        return self.record.get_object()

    def getDataOrigin(self):
        return self.record

    def getPath(self):
        return self.record.absolute_path

    def getURL(self):
        return self.record.getURL()  # XXX

    def uuid(self):
        return self.record.uuid

    def getIcon(self):
        return self.record.icon

    def getSize(self):
        return None

    def review_state(self):
        return self.record.review_state

    def PortalType(self):
        return self.record.portal_type

    def CroppedDescription(self):
        return None
