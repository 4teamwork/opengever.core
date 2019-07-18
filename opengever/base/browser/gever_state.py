from opengever.base.casauth import get_cas_server_url
from opengever.base.casauth import get_cluster_base_url
from opengever.base.casauth import get_gever_portal_url
from opengever.base.interfaces import IGeverState
from opengever.contact.interfaces import IContactFolder
from opengever.inbox.yearfolder import IYearFolder
from opengever.ogds.base.interfaces import ITeam
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from Products.Five import BrowserView
from zope.interface import implements


class GeverStateView(BrowserView):
    """A view that provides traversable helper methods to be used in templates
    or TAL expressions, similar to Plone's portal_state view.
    """
    implements(IGeverState)

    types_without_properties_action = (
        IContactFolder,
        ITeam,
        IYearFolder,
    )

    @memoize_contextless
    def cluster_base_url(self):
        return get_cluster_base_url()

    @memoize_contextless
    def gever_portal_url(self):
        return get_gever_portal_url()

    @memoize_contextless
    def cas_server_url(self):
        return get_cas_server_url()

    @memoize
    def properties_action_available(self):
        plone_view = self.context.restrictedTraverse("@@plone")
        if plone_view.getViewTemplateId() == 'view' or \
           plone_view.isPortalOrPortalDefaultPage():
            return False

        if any(iface.providedBy(self.context)
               for iface in self.types_without_properties_action):
            return False

        return True
