from ftw.table import helper
from opengever.base.schema import TableChoice
from opengever.base.source import DossierPathSourceBinder
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.meeting import _
from opengever.meeting.activity.watchers import add_watcher_on_proposal_created
from opengever.meeting.activity.watchers import change_watcher_on_proposal_edited
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
from z3c.form.browser import radio
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import INPUT_MODE
from z3c.relationfield.schema import RelationChoice
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import Invalid
from zope.interface import invariant
from zope.i18n import translate
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import Bool
from zope.schema import Choice
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class ProposalEditForm(ModelProxyEditForm,
                       edit.DefaultEditForm):

    fields = field.Fields(Proposal.model_schema, ignoreContext=True)
    content_type = Proposal

    def updateFields(self):
        super(ProposalEditForm, self).updateFields()
        move(self, 'description', before='*')
        move(self, 'title', before='*')

    def updateWidgets(self):
        super(ProposalEditForm, self).updateWidgets()
        ltool = api.portal.get_tool('portal_languages')
        if len(ltool.getSupportedLanguages()) <= 1:
            self.widgets['language'].mode = HIDDEN_MODE

        if self.context.get_state() is not self.context.load_model().STATE_PENDING:
            self.widgets['issuer'].mode = HIDDEN_MODE

    def update_watcher(self, obj, new_issuer):
        if obj.issuer != new_issuer:
            change_watcher_on_proposal_edited(obj, new_issuer)

    def applyChanges(self, data):
        self.update_watcher(self.context, data.get('issuer'))
        return super(ProposalEditForm, self).applyChanges(data)


class SubmittedProposalEditForm(ModelProxyEditForm,
                                edit.DefaultEditForm):

    fields = field.Fields(SubmittedProposal.model_schema, ignoreContext=True)
    content_type = SubmittedProposal

    def updateFields(self):
        super(SubmittedProposalEditForm, self).updateFields()
        move(self, 'title', before='*')

    def updateWidgets(self):
        super(SubmittedProposalEditForm, self).updateWidgets()
        self.widgets['excerpts'].mode = HIDDEN_MODE
        self.widgets['relatedItems'].mode = HIDDEN_MODE

        if self.context.get_state() is not self.context.load_model().STATE_PENDING:
            self.widgets['issuer'].mode = HIDDEN_MODE

    def applyChanges(self, data):
        super(SubmittedProposalEditForm, self).applyChanges(data)
        self.context.sync_model()
        return True


class IAddProposal(IProposal):

    proposal_document_type = Choice(
        title=_(u'label_template_or_existing_document',
                default=u'Proposal document type'),
        vocabulary=SimpleVocabulary([
            SimpleTerm(value=u'template', title=_(u'From template')),
            SimpleTerm(value=u'existing', title=_(u'Existing document'))]),
        required=False,
        default='template',
    )

    proposal_document = RelationChoice(
        title=_(u'label_proposal_document', default=u'Proposal Document'),
        required=False,
        source=DossierPathSourceBinder(
            portal_type=("opengever.document.document", ),
            navigation_tree_query={
                'review_state': {'not': 'document-state-shadow'},
                'file_extension': '.docx',
                'object_provides': [
                    'opengever.document.document.IDocumentSchema',
                    'opengever.dossier.behaviors.dossier.IDossierMarker',
                    'opengever.meeting.proposal.IProposal',
                    'opengever.task.task.ITask',
                    ],
            }),
        )

    proposal_template = TableChoice(
        title=_('label_proposal_template', default=u'Proposal template'),
        vocabulary='opengever.meeting.ProposalTemplatesForCommitteeVocabulary',
        required=False,
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

    @invariant
    def template_or_document_required_for_creation(data):
        proposal_template = data.proposal_template
        proposal_document = data.proposal_document
        proposal_document_type = data.proposal_document_type

        selected_document_type_choosen = proposal_template \
            if proposal_document_type == 'template' else proposal_document

        if not selected_document_type_choosen:
            raise Invalid(_(
                u'error_template_or_document_required_for_creation',
                default=u'Either a proposal template or a proposal document is required.',
                ))

    @invariant
    def proposal_document_must_be_docx(data):
        # XXX - this should get removed once we have a mimetype index based on which we can filter at source
        proposal_document = data.proposal_document
        if proposal_document:
            proposal_document_mimetype = proposal_document.file.contentType
            docx_mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            if not proposal_document_mimetype == docx_mimetype:
                raise Invalid(_(
                    u'error_only_docx_files_allowed_as_proposal_documents',
                    default=u'Only .docx files allowed as proposal documents.',
                    ))


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
        # XXX - tabbedview -> form injections should get reengineered
        paths = self.request.get('paths', [])
        if paths:
            self.request.set('form.widgets.relatedItems', paths)
        self.prefill_meeting_protocol_defaults()
        self.prefillPredecessorDefaults()
        self.prefill_issuer()
        return super(ProposalAddForm, self).update()

    def updateFields(self):
        try:
            return super(ProposalAddForm, self).updateFields()
        finally:
            if self.schema is IAddProposal:
                move(self, 'proposal_template', after='committee')
                move(self, 'proposal_document_type', before='proposal_template')
                move(self, 'proposal_document', before='proposal_template')
                move(self, 'edit_after_creation', after='proposal_template')
            move(self, 'description', before='*')
            move(self, 'title', before='*')
            move(self, 'issuer', after='description')

            self.fields['proposal_document_type'].widgetFactory[INPUT_MODE] \
                = radio.RadioFieldWidget

    def updateWidgets(self):
        super(ProposalAddForm, self).updateWidgets()
        ltool = api.portal.get_tool('portal_languages')
        if len(ltool.getSupportedLanguages()) <= 1:
            self.widgets['language'].mode = HIDDEN_MODE

    def prefill_meeting_protocol_defaults(self):
        if 'protocol' not in self.request.form:
            # Either we are not creating a proposal from a meeting protocol,
            # but a regular proposal, or form is already submitted.
            # In both cases we don't want prefill defaults.
            return
        protocol_document = uuidToObject(self.request.form['protocol'])
        meeting = protocol_document.get_parent_dossier().get_meeting()
        related_items_paths = ['/'.join(protocol_document.getPhysicalPath())]

        title = translate(_(u'label_protocol_approval', default=u'Approve protocol'),
                          context=self.request)
        defaults = {
            'title': u"{} {}".format(title, safe_unicode(meeting.title)),
            'committee': [unicode(meeting.committee_id)],
            'relatedItems': related_items_paths}

        for name, value in defaults.items():
            self.request.form['form.widgets.' + name] = value

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
        # We need to pop the form related extras before hitting the super call
        proposal_template = data.pop('proposal_template')
        proposal_document = data.pop('proposal_document')
        proposal_document_type = data.pop('proposal_document_type')

        proposal_template = proposal_template \
            if proposal_document_type == 'template' else proposal_document

        edit_after_creation = data.pop('edit_after_creation')
        self.instance_schema = IProposal
        noaq_proposal = super(ProposalAddForm, self).createAndAdd(data)
        proposal = self.context.get(noaq_proposal.getId())
        proposal_doc = proposal.create_proposal_document(
            title=proposal.title_or_id(),
            source_blob=proposal_template.file,
        )
        if edit_after_creation:
            self.checkout_and_external_edit(proposal_doc)

        add_watcher_on_proposal_created(proposal)
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
