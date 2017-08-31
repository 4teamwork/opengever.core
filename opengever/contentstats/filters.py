from ftw.contentstats.interfaces import IStatsKeyFilter
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


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

        blacklist = [
            'opengever.dossier.templatefolder',
            'opengever.repository.repositoryroot',
            'opengever.inbox.inbox',
            'opengever.inbox.yearfolder',
            'opengever.inbox.container',
            'opengever.tasktemplates.tasktemplatefolder',
            'opengever.contact.contactfolder',
            'opengever.meeting.committeecontainer',
        ]
        if key in blacklist:
            return False

        # Otherwise default to including all opengever.* types, and excluding
        # all the other ones (Plone stock types)
        if key.startswith('opengever.'):
            return True
        return False
