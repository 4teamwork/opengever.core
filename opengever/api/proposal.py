from opengever.meeting.proposal import IProposal
from opengever.meeting.proposal import PROPOSAL_TEMPLATE_KEY
from plone.restapi.deserializer import json_body
from plone.restapi.deserializer.dxcontent import DeserializeFromJson
from plone.restapi.interfaces import IDeserializeFromJson
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import RequiredMissing


@implementer(IDeserializeFromJson)
@adapter(IProposal, Interface)
class DeserializeProposalFromJson(DeserializeFromJson):

    def __call__(self, validate_all=False, data=None, create=False):
        if data is None:
            data = json_body(self.request)

        # Make sure that proposal_template is passed
        template_path = data.get("proposal_template")
        if template_path is None:
            raise RequiredMissing("proposal_template")

        # write template path to annotations as the proposal document gets
        # generated in opengever.meeting.handlers.proposal_added
        ann = IAnnotations(self.request)
        ann[PROPOSAL_TEMPLATE_KEY] = template_path

        proposal = super(DeserializeProposalFromJson, self).__call__(
            validate_all=validate_all, data=data, create=create)

        return proposal
