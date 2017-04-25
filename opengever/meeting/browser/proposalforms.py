from five import grok
from opengever.base.widgets import TrixFieldWidget
from opengever.meeting import is_word_meeting_implementation_enabled
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



class FieldOmitterMixin(object):
    """The field omitter mixin makes sure that the right fields are present
    in each form.
    """

    def updateFields(self):
        super(FieldOmitterMixin, self).updateFields()
        if not is_word_meeting_implementation_enabled():
            self.omit_field('file')
            self.omit_field('proposal_template_path')
            return

        self.omit_field('legal_basis')
        self.omit_field('initial_position')
        self.omit_field('proposed_action')
        self.omit_field('decision_draft')
        self.omit_field('publish_in')
        self.omit_field('disclose_to')
        self.omit_field('copy_for_attention')

        if isinstance(self, dexterity.AddForm):
            self.omit_field('file')
        else:
            self.omit_field('proposal_template_path')

    def omit_field(self, fieldname):
        if fieldname in self.fields:
            self.fields = self.fields.omit(fieldname)


class ProposalEditForm(FieldOmitterMixin, ModelProxyEditForm, dexterity.EditForm):

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


class SubmittedProposalEditForm(
        FieldOmitterMixin, ModelProxyEditForm, dexterity.EditForm):

    grok.context(ISubmittedProposal)
    fields = field.Fields(SubmittedProposal.model_schema, ignoreContext=True)
    content_type = Proposal

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


class AddForm(FieldOmitterMixin, ModelProxyAddForm, dexterity.AddForm):

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
