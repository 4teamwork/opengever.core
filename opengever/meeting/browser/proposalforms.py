from five import grok
from opengever.base.widgets import TrixFieldWidget
from opengever.meeting.form import ModelProxyAddForm
from opengever.meeting.form import ModelProxyEditForm
from opengever.meeting.proposal import IProposal
from opengever.meeting.proposal import ISubmittedProposal
from opengever.meeting.proposal import Proposal
from opengever.meeting.proposal import SubmittedProposal
from plone import api
from plone.directives import dexterity
from z3c.form import field
from z3c.form.interfaces import HIDDEN_MODE


class ProposalEditForm(ModelProxyEditForm, dexterity.EditForm):

    grok.context(IProposal)
    fields = field.Fields(Proposal.model_schema, ignoreContext=True)
    content_type = Proposal

    fields['legal_basis'].widgetFactory = TrixFieldWidget
    fields['initial_position'].widgetFactory = TrixFieldWidget
    fields['proposed_action'].widgetFactory = TrixFieldWidget
    fields['decision_draft'].widgetFactory = TrixFieldWidget
    fields['publish_in'].widgetFactory = TrixFieldWidget
    fields['disclose_to'].widgetFactory = TrixFieldWidget
    fields['copy_for_attention'].widgetFactory = TrixFieldWidget

    def updateWidgets(self):
        super(ProposalEditForm, self).updateWidgets()

        ltool = api.portal.get_tool('portal_languages')
        if len(ltool.getSupportedLanguages()) <= 1:
            self.widgets['language'].mode = HIDDEN_MODE


class SubmittedProposalEditForm(ModelProxyEditForm, dexterity.EditForm):

    grok.context(ISubmittedProposal)
    fields = field.Fields(SubmittedProposal.model_schema, ignoreContext=True)
    content_type = SubmittedProposal

    fields['legal_basis'].widgetFactory = TrixFieldWidget
    fields['initial_position'].widgetFactory = TrixFieldWidget
    fields['proposed_action'].widgetFactory = TrixFieldWidget
    fields['considerations'].widgetFactory = TrixFieldWidget
    fields['decision_draft'].widgetFactory = TrixFieldWidget
    fields['publish_in'].widgetFactory = TrixFieldWidget
    fields['disclose_to'].widgetFactory = TrixFieldWidget
    fields['copy_for_attention'].widgetFactory = TrixFieldWidget

    def updateWidgets(self):
        super(SubmittedProposalEditForm, self).updateWidgets()
        self.widgets['relatedItems'].mode = HIDDEN_MODE


class AddForm(ModelProxyAddForm, dexterity.AddForm):

    grok.name('opengever.meeting.proposal')
    content_type = Proposal
    fields = field.Fields(Proposal.model_schema)

    fields['legal_basis'].widgetFactory = TrixFieldWidget
    fields['initial_position'].widgetFactory = TrixFieldWidget
    fields['proposed_action'].widgetFactory = TrixFieldWidget
    fields['decision_draft'].widgetFactory = TrixFieldWidget
    fields['publish_in'].widgetFactory = TrixFieldWidget
    fields['disclose_to'].widgetFactory = TrixFieldWidget
    fields['copy_for_attention'].widgetFactory = TrixFieldWidget

    def updateWidgets(self):
        super(AddForm, self).updateWidgets()

        ltool = api.portal.get_tool('portal_languages')
        if len(ltool.getSupportedLanguages()) <= 1:
            self.widgets['language'].mode = HIDDEN_MODE
