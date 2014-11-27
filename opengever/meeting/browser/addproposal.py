from five import grok
from opengever.meeting.model.proposal import IProposalModel
from plone.directives import dexterity
from z3c.form import field


class AddForm(dexterity.AddForm):
    grok.name('opengever.meeting.proposal')

    fields = field.Fields(IProposalModel)

    def create_model(self, obj, data):
        obj.create_model(data, self.context)

    def createAndAdd(self, data):
        """Create proposal, this is a two-step process:

            1) Create the plone proxoy object (with no data)
            2) Create database model where the data is stored

        """
        obj = super(AddForm, self).createAndAdd(data={})
        self.create_model(obj, data)
        return obj
