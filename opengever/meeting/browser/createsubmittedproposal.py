from AccessControl.SecurityManagement import SpecialUsers
from five import grok
from opengever.base.oguid import Oguid
from opengever.meeting.service import meeting_service
from opengever.ogds.base.transport import REQUEST_KEY
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot
import json
import AccessControl


class CreateSubmittedProposal(grok.View):
    grok.context(IPloneSiteRoot)
    grok.name('create_submitted_proposal')
    grok.require('zope2.Public')

    def render(self):
        jsondata = self.request.get(REQUEST_KEY)
        data = json.loads(jsondata)
        committee = Oguid.parse(data['committee_oguid']).resolve_object()
        proposal_oguid = Oguid.parse(data['proposal_oguid'])
        proposal = meeting_service().fetch_proposal_by_oguid(proposal_oguid)

        # XXX create context manager!
        try:
            # change security context
            _sm = AccessControl.getSecurityManager()
            AccessControl.SecurityManagement.newSecurityManager(
                    self.context.REQUEST,
                    SpecialUsers.system)


            submitted_proposal = api.content.create(
                type='opengever.meeting.submittedproposal',
                id=self.generate_submitted_proposal_id(proposal),
                container=committee)

            submitted_proposal.sync_model(proposal_oguid)

            self.request.response.setHeader("Content-type", "application/json")
            return json.dumps(
                {'path': '/'.join(submitted_proposal.getPhysicalPath())})




        finally:
            AccessControl.SecurityManagement.setSecurityManager(
                _sm)


    def generate_submitted_proposal_id(self, proposal):
        return 'submitted-proposal-{}'.format(proposal.proposal_id)
