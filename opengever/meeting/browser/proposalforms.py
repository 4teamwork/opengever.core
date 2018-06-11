from ftw.table import helper
from opengever.base.schema import TableChoice
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.meeting import _
from opengever.meeting.form import ModelProxyAddForm
from opengever.meeting.form import ModelProxyEditForm
from opengever.meeting.proposal import IProposal
from opengever.meeting.proposal import Proposal
from opengever.meeting.proposal import SubmittedProposal
from opengever.officeconnector.helpers import is_officeconnector_checkout_feature_enabled  # noqa
from opengever.tabbedview.helper import document_with_icon
from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.autoform import directives as form
from plone.dexterity.browser import edit
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.interfaces import IDexterityFTI
from plone.z3cform.fieldsets.utils import move
from Products.CMFCore.interfaces import IFolderish
from Products.CMFPlone.utils import safe_unicode
from z3c.form import field
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget
from z3c.form.interfaces import HIDDEN_MODE
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import Bool


class ProposalEditForm(ModelProxyEditForm,
                       edit.DefaultEditForm):

    fields = field.Fields(Proposal.model_schema, ignoreContext=True)
    content_type = Proposal

    def updateFields(self):
        super(ProposalEditForm, self).updateFields()
        move(self, 'title', before='*')

    def updateWidgets(self):
        super(ProposalEditForm, self).updateWidgets()
        ltool = api.portal.get_tool('portal_languages')
        if len(ltool.getSupportedLanguages()) <= 1:
            self.widgets['language'].mode = HIDDEN_MODE

        if self.context.get_state() is not self.context.load_model().STATE_PENDING:
            self.widgets['issuer'].mode = HIDDEN_MODE


class SubmittedProposalEditForm(ModelProxyEditForm,
                                edit.DefaultEditForm):

    fields = field.Fields(SubmittedProposal.model_schema, ignoreContext=True)
    content_type = SubmittedProposal

    def updateFields(self):
        super(SubmittedProposalEditForm, self).updateFields()
        move(self, 'title', before='*')

    def updateWidgets(self):
        super(SubmittedProposalEditForm, self).updateWidgets()
        self.widgets['relatedItems'].mode = HIDDEN_MODE

        if self.context.get_state() is not self.context.load_model().STATE_PENDING:
            self.widgets['issuer'].mode = HIDDEN_MODE


class IAddProposal(IProposal):

    proposal_template = TableChoice(
        title=_('label_proposal_template', default=u'Proposal template'),
        vocabulary='opengever.meeting.ProposalTemplatesForCommitteeVocabulary',
        required=True,
        show_filter=True,
        vocabulary_depends_on=['form.widgets.committee'],
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

    form.widget(edit_after_creation=SingleCheckBoxFieldWidget)
    edit_after_creation = Bool(
        title=_(u'label_edit_after_creation', default=u'Edit after creation'),
        default=True,
        required=False)


class ProposalAddForm(ModelProxyAddForm, DefaultAddForm):
    content_type = Proposal
    fields = field.Fields(Proposal.model_schema)
    allow_prefill_from_GET_request = True

    def __init__(self, *args, **kwargs):
        super(ProposalAddForm, self).__init__(*args, **kwargs)
        self.instance_schema = IAddProposal

    @property
    def schema(self):
        # We cannot set the attribute "schema" because it is a class attribute
        # and setting it has side effects.
        # Therefore we use a property and introduce the instance_schema
        # attribute.
        return self.instance_schema

    def update(self):
        self.prefillPredecessorDefaults()
        self.prefill_issuer()
        return super(ProposalAddForm, self).update()

    def updateFields(self):
        try:
            return super(ProposalAddForm, self).updateFields()
        finally:
            if self.schema is IAddProposal:
                move(self, 'proposal_template', after='committee')
            move(self, 'title', before='*')

    def updateWidgets(self):
        super(ProposalAddForm, self).updateWidgets()
        ltool = api.portal.get_tool('portal_languages')
        if len(ltool.getSupportedLanguages()) <= 1:
            self.widgets['language'].mode = HIDDEN_MODE

    def prefillPredecessorDefaults(self):
        """When we create a successor proposal, the defaults change to
        be based on the predecessor.
        Since the relation widgets do not support changing values we must
        prefill the values in the request.
        """

        # When the "Create successor proposal" button is clicked on a
        # decided proposal, the "predecessor" is submitted in a POST
        # request to this form, with the UID of the predecessor as value.
        if 'predecessor' not in self.request.form:
            # Either we are not creating a successor, but a regular proposal,
            # or the successor form is already submitted.
            # In both cases we don't want prefill defaults.
            return

        predecessor = uuidToObject(self.request.form['predecessor'])
        related_items_paths = []
        excerpt = predecessor.get_excerpt()
        if excerpt:
            related_items_paths.append('/'.join(excerpt.getPhysicalPath()))

        related_items_paths.extend(
            [safe_unicode(relation.to_path)
             for relation in predecessor.relatedItems])

        defaults = {
            'predecessor_proposal': '/'.join(predecessor.getPhysicalPath()),
            'title': safe_unicode(predecessor.Title()),
            'committee': [unicode(
                predecessor.get_committee().load_model().committee_id)],
            'language': predecessor.load_model().language,
            'relatedItems': related_items_paths}

        for name, value in defaults.items():
            self.request.form['form.widgets.' + name] = value

    def prefill_issuer(self):
        """Adds a default value for `issuer` to the request so the
        field is prefilled with the current user.
        """
        issuer = api.user.get_current().getId()
        if not self.request.form.get('form.widgets.issuer', None):
            self.request['form.widgets.issuer'] = issuer

    def createAndAdd(self, data):
        proposal_template = data.pop('proposal_template')
        edit_after_creation = data.pop('edit_after_creation')
        self.instance_schema = IProposal
        noaq_proposal = super(ProposalAddForm, self).createAndAdd(data)
        proposal = self.context.get(noaq_proposal.getId())
        proposal_doc = proposal.create_proposal_document(proposal_template.file)
        if edit_after_creation:
            self.checkout_and_external_edit(proposal_doc)
        return proposal

    def checkout_and_external_edit(self, document):
        """Checkout the document and invoke an external editing session.
        """

        # When the officeconnector checkout feature is enabled,
        # office connector will checkout the document before opening the
        # document in word, so there is no need to checkout the document
        # at this point.
        if not is_officeconnector_checkout_feature_enabled():
            getMultiAdapter((document, self.request),
                            ICheckinCheckoutManager).checkout()

        document.setup_external_edit_redirect(self.request)


@adapter(IFolderish, IDefaultBrowserLayer, IDexterityFTI)
class ProposalAddView(DefaultAddView):
    form = ProposalAddForm
