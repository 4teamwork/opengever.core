from AccessControl import getSecurityManager
from five import grok
from opengever.base.browser.helper import get_css_class
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.ogds.base.interfaces import IContactInformation
from opengever.tabbedview.browser.tabs import OpengeverTab
from plone.directives.dexterity import DisplayForm
from zope.component import getUtility, queryMultiAdapter


try:
    from opengever.pdfconverter.behaviors.preview import IPreviewMarker
    from opengever.pdfconverter.behaviors.preview import IPreview
    from opengever.pdfconverter import CONVERSION_STATE_READY

    PDFCONVERTER_AVAILABLE = True
except ImportError:
    PDFCONVERTER_AVAILABLE = False


class Overview(DisplayForm, OpengeverTab):
    grok.context(IDocumentSchema)
    grok.name('tabbedview_view-overview')
    grok.template('overview')

    show_searchform = False

    def creator_link(self):
        info = getUtility(IContactInformation)
        return info.render_link(self.context.Creator())

    def checked_out_link(self):
        manager = queryMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)

        if manager.checked_out():
            info = getUtility(IContactInformation)
            return info.render_link(manager.checked_out())

        return None

    def get_css_class(self):
        return get_css_class(self.context)

    def is_preview_supported(self):
        # XXX TODO: should be persistent called two times
        if PDFCONVERTER_AVAILABLE:
            return IPreviewMarker.providedBy(self.context)
        return False

    def is_pdf_download_available(self):
        if self.is_preview_supported():
            if IPreview(
                self.context).conversion_state == CONVERSION_STATE_READY:
                return True
        return False

    def is_checkout_and_edit_available(self):
        manager = queryMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)

        if manager.checked_out():
            if manager.checked_out() == \
                    getSecurityManager().getUser().getId():
                return True
            else:
                return False

        return manager.is_checkout_allowed()

    def is_download_copy_available(self):
        """Disable copy link when the document is checked
        out by an other user."""

        manager = queryMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)
        if manager.checked_out():
            if manager.checked_out() != getSecurityManager().getUser().getId():
                return False
        return True
