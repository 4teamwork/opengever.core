from five import grok
from opengever.meeting import is_meeting_feature_enabled
from opengever.meeting.proposal import IProposal
from opengever.meeting.proposal import IProposalModel
from opengever.meeting.proposal import Proposal
from plone.directives import dexterity
from z3c.form import field
from zExceptions import Unauthorized


class EditForm(dexterity.EditForm):
    grok.context(IProposal)

    fields = field.Fields(IProposalModel, ignoreContext=True)

    def render(self):
        if not is_meeting_feature_enabled():
            raise Unauthorized
        return super(EditForm, self).render()

    def inject_initial_data(self):
        if self.request.method != 'GET':
            return

        prefix = 'form.widgets.'
        model = self.context.load_model()
        for fieldname in self.fields.keys():
            value = getattr(model, fieldname, None)

            if not value:
                continue

            if fieldname == 'commission':
                value = str(value.commission_id)
            self.request[prefix + fieldname] = value

    def updateWidgets(self):
        self.inject_initial_data()
        super(EditForm, self).updateWidgets()

    def applyChanges(self, data):
        obj_data, model_data = Proposal.partition_data(data)
        self.context.update_model(model_data)
        super(EditForm, self).applyChanges(obj_data)
        # pretend to always change the underlying data
        return True
