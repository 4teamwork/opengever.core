from ftw.contentstats.interfaces import IStatsKeyFilter
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


# List of GEVER types that aren't interesting to track, because they are
# not usually created by users of the application themselves.
#
# These will be filtered from portal_types as well as review_state stats.
OG_TYPES_BLACKLIST = [
    'opengever.contact.contactfolder',
    'opengever.dossier.templatefolder',
    'opengever.inbox.container',
    'opengever.inbox.inbox',
    'opengever.inbox.yearfolder',
    'opengever.meeting.committeecontainer',
    'opengever.private.root',
    'opengever.repository.repositoryroot',
    'opengever.workspace.root',
]


@implementer(IStatsKeyFilter)
@adapter(IPloneSiteRoot, Interface)
class PortalTypesFilter(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def keep(self, key):
        whitelist = ['ftw.mail.mail']
        if key in whitelist:
            return True

        if key in OG_TYPES_BLACKLIST:
            return False

        if key == '_opengever.document.behaviors.IBaseDocument':
            # Fake portal type that sums up docs and mails
            return True

        # Otherwise default to including all opengever.* types, and excluding
        # all the other ones (Plone stock types)
        if key.startswith('opengever.'):
            return True
        return False


@implementer(IStatsKeyFilter)
@adapter(IPloneSiteRoot, Interface)
class ReviewStatesFilter(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._states_to_keep = self._determine_states_to_keep()

    def _keep_type(self, portal_type):
        """Whether or not a portal_type's workflows' states should be included.
        """
        whitelist = ['ftw.mail.mail']
        if portal_type in whitelist:
            return True

        if portal_type in OG_TYPES_BLACKLIST:
            return False

        # Otherwise default to including all opengever.* types, and excluding
        # all the other ones (Plone stock types)
        if portal_type.startswith('opengever.'):
            return True
        return False

    def _determine_states_to_keep(self):
        """What workflow states should be included.

        This will include all the states of workflows of types to keep.
        """
        types_tool = api.portal.get_tool('portal_types')
        wftool = api.portal.get_tool('portal_workflow')

        states_to_keep = []
        for fti in types_tool.objectValues():
            if not self._keep_type(fti.id):
                continue
            for wf_id in wftool.getChainForPortalType(fti.id):
                wf = wftool[wf_id]
                states_to_keep.extend(wf.states.objectIds())
        # Placeful workflows are not covered by the above code.
        states_to_keep.append('opengever_workspace_document--STATUS--active')
        states_to_keep.append('opengever_workspace_document--STATUS--final')
        return states_to_keep

    def keep(self, key):
        return key in self._states_to_keep
