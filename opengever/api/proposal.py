from opengever.api.response import SerializeResponseToJson
from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.base.oguid import Oguid
from opengever.meeting.model import Meeting
from opengever.meeting.proposal import IProposal
from opengever.meeting.proposal import ISubmittedProposal
from opengever.meeting.proposalhistory import IProposalResponse
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(IProposalResponse, Interface)
class SerializeProposalResponseToJson(SerializeResponseToJson):

    model = IProposalResponse

    def __call__(self, *args, **kwargs):
        resp = super(SerializeProposalResponseToJson, self).__call__(*args, **kwargs)

        additional_data = resp['additional_data']
        if 'successor_oguid' in additional_data:
            successor = Oguid.parse(self.context.successor_oguid).resolve_object()
            model = successor.load_model()
            additional_data['successor_title'] = model.title
            if model.display_proposal_link():
                additional_data['successor_url'] = model.get_url()

        if 'meeting_id' in additional_data:
            meeting = Meeting.query.get(self.context.meeting_id)
            additional_data['meeting_title'] = json_compatible(
                meeting.get_title() if meeting else u'')
            if meeting.can_view():
                additional_data['meeting_url'] = meeting.get_url()
        return resp


@implementer(ISerializeToJson)
@adapter(ISubmittedProposal, Interface)
class SerializeSubmittedProposalToJson(GeverSerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeSubmittedProposalToJson, self).__call__(*args, **kwargs)

        excerpt = self.context.get_excerpt()
        if excerpt:
            serializer = getMultiAdapter(
                 (excerpt, self.request), interface=ISerializeToJsonSummary
            )
            result[u'excerpt'] = serializer()
        else:
            result[u'excerpt'] = None

        meeting = self.context.load_model().get_meeting()
        if meeting:
            result[u'meeting'] = {
                'title': meeting.title,
                '@id': meeting.get_url(view=None)
                }
        else:
            result[u'meeting'] = None

        result[u'decision_number'] = self.context.load_model().get_decision_number()

        return result


@implementer(ISerializeToJson)
@adapter(IProposal, Interface)
class SerializeProposalToJson(SerializeSubmittedProposalToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeProposalToJson, self).__call__(*args, **kwargs)

        successor_proposals = []
        for successor in self.context.get_successor_proposals():
            serializer = getMultiAdapter(
                 (successor, self.request), interface=ISerializeToJsonSummary
            )
            successor_proposals.append(serializer())

        result['successor_proposals'] = successor_proposals

        return result
