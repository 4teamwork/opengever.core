from opengever.api.response import SerializeResponseToJson
from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.meeting.proposal import IBaseProposal
from opengever.meeting.proposalhistory import IProposalResponse
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(IProposalResponse, Interface)
class SerializeProposalResponseToJson(SerializeResponseToJson):

    model = IProposalResponse


@implementer(ISerializeToJson)
@adapter(IBaseProposal, Interface)
class SerializeProposalToJson(GeverSerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeProposalToJson, self).__call__(*args, **kwargs)

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
