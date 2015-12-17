from opengever.base.casauth import get_cas_server_url
from opengever.base.casauth import get_cluster_base_url
from opengever.base.casauth import get_gever_portal_url
from opengever.base.interfaces import IGeverState
from plone.memoize.view import memoize_contextless
from Products.Five import BrowserView
from zope.interface import implements


class GeverStateView(BrowserView):
    """A view that provides traversable helper methods to be used in templates
    or TAL expressions, similar to Plone's portal_state view.
    """
    implements(IGeverState)

    @memoize_contextless
    def cluster_base_url(self):
        return get_cluster_base_url()

    @memoize_contextless
    def gever_portal_url(self):
        return get_gever_portal_url()

    @memoize_contextless
    def cas_server_url(self):
        return get_cas_server_url()
