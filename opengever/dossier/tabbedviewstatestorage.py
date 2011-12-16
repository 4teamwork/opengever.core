from Products.CMFCore.utils import getToolByName
from five import grok
from ftw.tabbedview.interfaces import IGridStateStorageKeyGenerator
from opengever.dossier.behaviors.dossier import IDossierMarker
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IBrowserRequest


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

        # add the name of the tab
        key.append(self.tabview.__name__)

        # add the userid
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        key.append(member.getId())

        # concatenate with "-"
        return '-'.join(key)
