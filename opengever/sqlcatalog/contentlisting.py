from ftw import bumblebee
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.document.behaviors import IBaseDocument
from opengever.document.document import Document
from opengever.document.widgets.document_link import DocumentLinkWidget
from opengever.mail.mail import OGMail
from opengever.sqlcatalog.interfaces import ISQLRecord
from opengever.trash.trash import ITrashed
from plone.app.contentlisting.contentlisting import BaseContentListingObject
from plone.app.contentlisting.interfaces import IContentListingObject
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer


@implementer(IContentListingObject)
@adapter(ISQLRecord)
class SQLRecordContentListing(BaseContentListingObject):

    def __init__(self, record):
        self.record = record

    def getId(self):
        return self.record.id

    def Title(self):
        return self.record.Title

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

    @property
    def is_document(self):
        # XXX expensive
        return IBaseDocument.providedBy(self.getObject())

    @property
    def is_trashed(self):
        return ITrashed.providedBy(self.getObject())

    @property
    def is_removed(self):
        removed_states = [Document.removed_state, OGMail.removed_state]
        return self.review_state() in removed_states

    def is_bumblebeeable(self):
        return is_bumblebee_feature_enabled()

    def render_link(self, **kwargs):
        return DocumentLinkWidget(self).render(**kwargs)

    def get_breadcrumbs(self):
        obj = self.getObject()
        breadcrumbs_view = getMultiAdapter((obj, obj.REQUEST), name='breadcrumbs_view')
        return breadcrumbs_view.breadcrumbs()

    def get_overlay_url(self):
        """Return the url to fetch the bumblebee overlay."""

        if not self.is_bumblebeeable():
            return None

        return '{}/@@bumblebee-overlay-listing'.format(self.getURL())

    def get_preview_image_url(self):
        """Return the url to fetch the bumblebee preview thumbnail."""

        if not self.is_bumblebeeable():
            return None

        return bumblebee.get_service_v3().get_representation_url(
            self.getObject(), 'thumbnail')

    def get_overlay_title(self):
        return self.Title().decode('utf-8')
