from five import grok
from opengever.meeting import is_meeting_feature_enabled
from opengever.meeting.proposal import IProposalModel
from opengever.meeting.proposal import Proposal
from plone.directives import dexterity
from z3c.form import field
from zExceptions import Unauthorized


class AddForm(dexterity.AddForm):
    grok.name('opengever.meeting.proposal')

    fields = field.Fields(IProposalModel)

    def render(self):
        if not is_meeting_feature_enabled():
            raise Unauthorized
        return super(AddForm, self).render()

    def create_model(self, obj, data):
        obj.create_model(data, self.context)

    def createAndAdd(self, data):
        """Create proposal, this is a two-step process:

            1) Create the plone proxy object (with no data)
            2) Create database model where the data is stored

        """
        obj_data, model_data = Proposal.partition_data(data)
        obj = super(AddForm, self).createAndAdd(data=obj_data)
        self.create_model(obj, model_data)
        return obj
