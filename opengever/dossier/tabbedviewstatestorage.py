from five import grok
from ftw.tabbedview.interfaces import IGridStateStorageKeyGenerator
from opengever.dossier.behaviors.dossier import IDossierMarker
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserView


class DossierGridStateStorageKeyGenerator(grok.MultiAdapter):
    """This storage key generator creates a shared key for all dossier types,
    since we need to share the configuration between different dossier types.
    """

    grok.implements(IGridStateStorageKeyGenerator)
    grok.adapts(IDossierMarker, IBrowserView, IBrowserRequest)

    def __init__(self, context, tabview, request):
        self.context = context
        self.tabview = tabview
        self.request = request

    def get_key(self):
        key = []
        key.append('ftw.tabbedview')

        # replace the portal type with static 'opengever.dossier'
        key.append('openever.dossier')

        view_name = self.tabview.__name__
        if view_name in ['tabbedview_view-documents',
                         'tabbedview_view-mydocuments']:
            view_name = '{}-proxy'.format(view_name)

        # add the name of the tab
        key.append(view_name)

        # add the userid
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        key.append(member.getId())

        # concatenate with "-"
        return '-'.join(key)


class PloneSiteRootGridStateStorageKeyGenerator(DossierGridStateStorageKeyGenerator):
    """This storage key generator creates a shared key for the frontpage.
    The implemmentation have to be the same like the dossier
    """

    grok.implements(IGridStateStorageKeyGenerator)
    grok.adapts(IPloneSiteRoot, IBrowserView, IBrowserRequest)
