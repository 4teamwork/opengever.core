from five import grok
from opengever.base.interfaces import IDataCollector
from opengever.base.oguid import Oguid
from opengever.base.security import elevated_privileges
from opengever.base.transport import REQUEST_KEY
from opengever.meeting import is_word_meeting_implementation_enabled
from opengever.meeting.proposal import SubmittedProposal
from opengever.meeting.service import meeting_service
from opengever.ogds.base.utils import encode_after_json
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import getMultiAdapter
import base64
import json


class CreateSubmittedProposal(grok.View):
    grok.context(IPloneSiteRoot)
    grok.name('create_submitted_proposal')
    grok.require('zope2.Public')

    def render(self):
        jsondata = self.request.get(REQUEST_KEY)
        data = encode_after_json(json.loads(jsondata))
        committee = Oguid.parse(data['committee_oguid']).resolve_object()
        proposal_oguid = Oguid.parse(data['proposal_oguid'])
        proposal = meeting_service().fetch_proposal_by_oguid(proposal_oguid)

        with elevated_privileges():
            submitted_proposal = SubmittedProposal.create(proposal, committee)

            # XXX use Transporter API?
            collector = getMultiAdapter((submitted_proposal,), IDataCollector,
                                        name='field-data')
            data['field-data']['ISubmittedProposal'] = data['field-data'].pop(
                'IProposal')
            collector.insert(data['field-data'])

            if is_word_meeting_implementation_enabled():
                submitted_proposal.create_proposal_document(
                    filename=data['file']['filename'],
                    content_type=data['file']['contentType'].encode('utf-8'),
                    data=base64.decodestring(data['file']['data']))

            self.request.response.setHeader("Content-type", "application/json")
            return json.dumps(
                {'path': '/'.join(submitted_proposal.getPhysicalPath())})
