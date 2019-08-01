from ftw.bumblebee.interfaces import IBumblebeeDocument
from opengever.document.browser.actionbuttons import VisibleActionButtonRendererMixin
from plone.app.contentlisting.interfaces import IContentListingObject


class TooltipView(VisibleActionButtonRendererMixin):
    """File tooltip"""

    def __init__(self, context, request):
        super(TooltipView, self).__init__(context, request)
        self.document = IContentListingObject(self.context)
        self.request.response.setHeader('X-Tooltip-Response', True)

    def get_bumblebee_checksum(self):
        return IBumblebeeDocument(self.context).get_checksum()
