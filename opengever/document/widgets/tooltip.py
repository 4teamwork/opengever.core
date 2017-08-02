from opengever.document.browser.actionbuttons import ActionButtonRendererMixin
from plone.app.contentlisting.interfaces import IContentListingObject


class TooltipView(ActionButtonRendererMixin):
    """File tooltip"""

    def __init__(self, context, request):
        super(TooltipView, self).__init__(context, request)
        self.document = IContentListingObject(self.context)
        self.request.response.setHeader('X-Tooltip-Response', True)
