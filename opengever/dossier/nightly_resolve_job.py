from opengever.nightlyjobs.interfaces import INightlyJobProvider
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


@implementer(INightlyJobProvider)
@adapter(IPloneSiteRoot, IBrowserRequest)
class ResolveDossiersJobProvider(object):

    def __init__(self, context, request):
        self.catalog = api.portal.get_tool('portal_catalog')
        self.query = {
            'portal_type': 'opengever.dossier.businesscasedossier',
            'review_state': 'dossier-state-pending-resolution',
        }
        self.portal = api.portal.get()
        self.wftool = api.portal.get_tool('portal_workflow')
        self.transition = 'dossier-transition-pending-resolution-to-resolved'

    def __iter__(self):
        pending = self.catalog.unrestrictedSearchResults(self.query)
        return iter([{'path': brain.getPath()} for brain in pending])

    def __len__(self):
        resultset = self.catalog.unrestrictedSearchResults(self.query)
        return resultset.actual_result_count

    def run_job(self, job, interrupt_if_necessary):
        path = job.data['path']
        dossier = self.portal.unrestrictedTraverse(path)
        self.wftool.doActionFor(dossier, self.transition)
        print "Resolved dossier %r" % dossier
