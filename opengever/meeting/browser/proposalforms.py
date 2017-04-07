from five import grok
from ftw.table import helper
from opengever.base.schema import TableChoice
from opengever.base.widgets import TrixFieldWidget
from opengever.dossier.templatefolder import get_template_folder
from opengever.meeting import _
from opengever.meeting import is_word_meeting_implementation_enabled
from opengever.meeting.form import ModelProxyAddForm
from opengever.meeting.form import ModelProxyEditForm
from opengever.meeting.proposal import IProposal
from opengever.meeting.proposal import ISubmittedProposal
from opengever.meeting.proposal import Proposal
from opengever.meeting.proposal import SubmittedProposal
from opengever.tabbedview.helper import document_with_icon
from plone import api
from plone.directives import dexterity
from plone.uuid.interfaces import IUUID
from plone.z3cform.fieldsets.utils import move
from z3c.form import field
from z3c.form.interfaces import HIDDEN_MODE
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary


class FieldConfigurationMixin(object):
    """The field omitter mixin makes sure that the right fields are present
    in each form.
    """

    def updateFields(self):
        super(FieldConfigurationMixin, self).updateFields()
        textfields = ('legal_basis',
                      'initial_position',
                      'proposed_action',
                      'decision_draft',
                      'publish_in',
                      'disclose_to',
                      'copy_for_attention')

        map(self.use_trix, textfields)
        if is_word_meeting_implementation_enabled():
            map(self.omit_field, textfields)

    def omit_field(self, fieldname):
        self.fields = self.fields.omit(fieldname)

    def use_trix(self, fieldname):
        self.fields[fieldname].widgetFactory = TrixFieldWidget


class ProposalEditForm(FieldConfigurationMixin,
                       ModelProxyEditForm,
                       dexterity.EditForm):
    grok.context(IProposal)
    fields = field.Fields(Proposal.model_schema, ignoreContext=True)
    content_type = Proposal

    def updateWidgets(self):
        super(ProposalEditForm, self).updateWidgets()
        ltool = api.portal.get_tool('portal_languages')
        if len(ltool.getSupportedLanguages()) <= 1:
            self.widgets['language'].mode = HIDDEN_MODE


class SubmittedProposalEditForm(FieldConfigurationMixin,
                                ModelProxyEditForm,
                                dexterity.EditForm):
    grok.context(ISubmittedProposal)
    fields = field.Fields(SubmittedProposal.model_schema, ignoreContext=True)
    content_type = SubmittedProposal

    def updateWidgets(self):
        super(SubmittedProposalEditForm, self).updateWidgets()
        self.widgets['relatedItems'].mode = HIDDEN_MODE


@provider(IContextSourceBinder)
def get_proposal_template_vocabulary(context):
    template_folder = get_template_folder()
    if template_folder is None:
        # this may happen when the user does not have permissions to
        # view templates and/or during ++widget++ traversal
        return SimpleVocabulary([])

    templates = api.content.find(
        context=template_folder,
        depth=-1,
        portal_type="opengever.meeting.proposaltemplate",
        sort_on='sortable_title', sort_order='ascending')

    terms = []
    for brain in templates:
        template = brain.getObject()
        terms.append(SimpleVocabulary.createTerm(
            template,
            IUUID(template),
            brain.Title))
    return SimpleVocabulary(terms)


class IAddProposal(IProposal):

    proposal_template = TableChoice(
        title=_('label_proposal_template', default=u'Proposal template'),
        source=get_proposal_template_vocabulary,
        required=True,
        columns=(
            {'column': 'title',
             'column_title': _(u'label_title', default=u'Title'),
             'sort_index': 'sortable_title',
             'transform': document_with_icon},
            {'column': 'Creator',
             'column_title': _(u'label_creator', default=u'Creator'),
             'sort_index': 'document_author'},
            {'column': 'modified',
             'column_title': _(u'label_modified', default=u'Modified'),
             'transform': helper.readable_date}))


class AddForm(FieldConfigurationMixin, ModelProxyAddForm, dexterity.AddForm):
    grok.name('opengever.meeting.proposal')
    content_type = Proposal
    fields = field.Fields(Proposal.model_schema)

    def __init__(self, *args, **kwargs):
        super(AddForm, self).__init__(*args, **kwargs)
        if is_word_meeting_implementation_enabled():
            self.instance_schema = IAddProposal
        else:
            self.instance_schema = IProposal

    @property
    def schema(self):
        # We cannot set the attribute "schema" because it is a class attribute
        # and setting it has side effects.
        # Therefore we use a property and introduce the instance_schema
        # attribute.
        return self.instance_schema

    def updateFields(self):
        try:
            return super(AddForm, self).updateFields()
        finally:
            if self.schema is IAddProposal:
                move(self, 'proposal_template', after='committee')

    def updateWidgets(self):
        super(AddForm, self).updateWidgets()
        ltool = api.portal.get_tool('portal_languages')
        if len(ltool.getSupportedLanguages()) <= 1:
            self.widgets['language'].mode = HIDDEN_MODE

    def createAndAdd(self, data):
        if not is_word_meeting_implementation_enabled():
            return super(AddForm, self).createAndAdd(data)

        proposal_template = data.pop('proposal_template')
        self.instance_schema = IProposal
        noaq_proposal = super(AddForm, self).createAndAdd(data)
        proposal = self.context.get(noaq_proposal.getId())
        proposal.create_proposal_document(proposal_template.file)
        return proposal
