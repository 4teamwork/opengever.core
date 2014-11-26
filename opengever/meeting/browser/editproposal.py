from five import grok
from opengever.meeting.model.proposal import IProposalModel
from opengever.meeting.proposal import IProposal
from plone.directives import dexterity
from z3c.form import field
from z3c.form import interfaces
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class EditForm(dexterity.EditForm):
    grok.context(IProposal)

    ignoreContext = True
    fields = field.Fields(IProposalModel)

    def inject_initial_data(self):
        if self.request.method != 'GET':
            return

        prefix = 'form.widgets.'
        model = self.context.load_model()
        for fieldname in self.fields.keys():
            value = getattr(model, fieldname, None)
            if value:
                self.request[prefix + fieldname] = value

    def updateWidgets(self):
        self.inject_initial_data()
        super(EditForm, self).updateWidgets()

    def applyChanges(self, data):
        """Store form input in relational database.

        KISS: Currently assumes that each input is a change an thus always
        fires a changed event.

        """
        model = self.context.load_model()
        for key, value in data.items():
            if value is interfaces.NOT_CHANGED:
                continue
            setattr(model, key, value)

        notify(ObjectModifiedEvent(self.context))
        return True
