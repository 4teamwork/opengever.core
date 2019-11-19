from opengever.api.response import SerializeResponseToJson
from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from opengever.meeting.proposalhistory import IProposalResponse


@implementer(ISerializeToJson)
@adapter(IProposalResponse, Interface)
class SerializeProposalResponseToJson(SerializeResponseToJson):

    model = IProposalResponse
