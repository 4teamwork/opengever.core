from opengever.document.base import BaseDocumentMixin
from plone.app.contentlisting.interfaces import IContentListingObject


class TooltipView(BaseDocumentMixin):
    """File tooltip"""

    def __init__(self, context, request):
        super(TooltipView, self).__init__(context, request)
        self.document = IContentListingObject(self.context)
