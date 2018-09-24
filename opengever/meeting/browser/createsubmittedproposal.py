from datetime import date
from opengever.base import advancedjson
from opengever.base.interfaces import IDataCollector
from opengever.base.oguid import Oguid
from opengever.base.security import elevated_privileges
from opengever.base.transport import REQUEST_KEY
from opengever.meeting.activity.activities import ProposalSubmittedActivity
from opengever.meeting.activity.watchers import add_watchers_on_submitted_proposal_created
from opengever.meeting.interfaces import IHistory
from opengever.meeting.proposal import SubmittedProposal
from opengever.meeting.service import meeting_service
from opengever.ogds.base.utils import encode_after_json
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
import base64
import json


class CreateSubmittedProposal(BrowserView):

    def __call__(self):
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
            # XXX fix data types in transporter
            submitted_proposal.date_of_submission = date.today()

            # sync data to proposal after inserting field data
            submitted_proposal.sync_model(proposal_model=proposal)

            submitted_proposal.create_proposal_document(
                title=data['title'],
                filename=data['file']['filename'],
                content_type=data['file']['contentType'].encode('utf-8'),
                data=base64.decodestring(data['file']['data']))

            history_data = advancedjson.loads(self.request.get('history_data'))
            IHistory(submitted_proposal).append_record(
                u'submitted', uuid=history_data['uuid'], text=history_data.get("text"))

            add_watchers_on_submitted_proposal_created(submitted_proposal)

            ProposalSubmittedActivity(submitted_proposal, self.request).record()

            self.request.response.setHeader("Content-type", "application/json")
            return json.dumps(
                {'path': '/'.join(submitted_proposal.getPhysicalPath())})
