from five import grok
from opengever.base.oguid import Oguid
from opengever.base.security import elevated_privileges
from opengever.base.transport import REQUEST_KEY
from opengever.meeting.proposal import ISubmittedProposal
from opengever.meeting.proposal import SubmittedProposal
from opengever.meeting.service import meeting_service
from Products.CMFPlone.interfaces import IPloneSiteRoot
import base64
import json


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

        with elevated_privileges():
            submitted_proposal = SubmittedProposal.create(proposal, committee)
            ISubmittedProposal(submitted_proposal).file = (
                ISubmittedProposal['file']._type(
                    filename=data['file']['filename'],
                    contentType=data['file']['contentType'],
                    data=base64.decodestring(data['file']['data'])))

            self.request.response.setHeader("Content-type", "application/json")
            return json.dumps(
                {'path': '/'.join(submitted_proposal.getPhysicalPath())})
