from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from collective import dexteritytextindexer
from datetime import date
from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.base.command import CreateDocumentCommand
from opengever.base.interfaces import IReferenceNumber
from opengever.base.oguid import Oguid
from opengever.base.security import elevated_privileges
from opengever.base.source import DossierPathSourceBinder
from opengever.base.source import SolrObjPathSourceBinder
from opengever.base.utils import get_preferred_language_code
from opengever.base.utils import to_html_xweb_intelligent
from opengever.document.widgets.document_link import DocumentLinkWidget
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.utils import get_containing_dossier
from opengever.meeting import _
from opengever.meeting.activity.activities import ProposalCommentedActivitiy
from opengever.meeting.activity.activities import ProposalRejectedActivity
from opengever.meeting.activity.activities import ProposalSubmittedActivity
from opengever.meeting.activity.watchers import remove_watchers_on_submitted_proposal_deleted
from opengever.meeting.command import CopyProposalDocumentCommand
from opengever.meeting.command import CreateSubmittedProposalCommand
from opengever.meeting.command import NullUpdateSubmittedDocumentCommand
from opengever.meeting.command import RejectProposalCommand
from opengever.meeting.command import UpdateSubmittedDocumentCommand
from opengever.meeting.container import ModelContainer
from opengever.meeting.interfaces import IHistory
from opengever.meeting.model import SubmittedDocument
from opengever.meeting.model.proposal import Proposal as ProposalModel
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.sources import AssignedUsersSourceBinder
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import ogds_service
from opengever.trash.trash import ITrashed
from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.autoform.directives import mode
from plone.autoform.directives import omitted
from plone.autoform.directives import widget
from plone.dexterity.content import Container
from plone.supermodel import model
from plone.uuid.interfaces import IUUID
from z3c.relationfield.event import addRelations
from z3c.relationfield.relation import RelationValue
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zc.relation.interfaces import ICatalog
from zope import schema
from zope.component import getUtility
from zope.interface import implements
from zope.interface import Interface
from zope.interface import provider
from zope.intid.interfaces import IIntIds
from zope.schema.interfaces import IContextAwareDefaultFactory


@provider(IContextAwareDefaultFactory)
def default_title(context):
    # At this point, only proposals (not submitted proposals) should acquire
    # an actual default. This is indicated by the parent being a dossier.
    if not IDossierMarker.providedBy(context):
        return u''

    # Use Title() accessor to make this defaultFactor robust in regard to
    # objects with ITranslatedTitle behavior or titles stored in SQL
    return context.Title().decode('utf-8')


class IProposalModel(Interface):
    """Proposal model schema interface."""


class ISubmittedProposalModel(Interface):
    """Submitted proposal model schema interface."""


class IBaseProposal(model.Schema):

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        required=True,
        max_length=256,
        defaultFactory=default_title
        )

    dexteritytextindexer.searchable('description')
    description = schema.Text(
        title=_(u'label_description', default=u'Description'),
        required=False,
        missing_value=u'',
        default=u'',
        )

    widget('issuer', KeywordFieldWidget, async=True)
    issuer = schema.Choice(
        title=_(u"label_issuer", default="Issuer"),
        source=AssignedUsersSourceBinder(),
        required=True,
    )

    omitted('date_of_submission')
    date_of_submission = schema.Date(
        description=_('label_date_of_submission',
                      default='Date of submission'),
        default=None,
        missing_value=None,
        required=False,
        )

    language = schema.Choice(
        title=_('language', default=u'Language'),
        source='opengever.meeting.LanguagesVocabulary',
        required=True,
        defaultFactory=get_preferred_language_code)


class IProposal(IBaseProposal):
    """Proposal Proxy Object Schema Interface"""

    committee_oguid = schema.Choice(
        title=_('label_committee', default=u'Committee'),
        source='opengever.meeting.ActiveCommitteeVocabulary',
        required=True)

    relatedItems = RelationList(
        title=_(u'label_attachments', default=u'Attachments'),
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            title=u"Related",
            source=DossierPathSourceBinder(
                portal_type=("opengever.document.document", "ftw.mail.mail"),
                navigation_tree_query={
                    'review_state': {'not': 'document-state-shadow'},
                    'object_provides': [
                        'opengever.dossier.behaviors.dossier.IDossierMarker',
                        'opengever.document.document.IDocumentSchema',
                        'opengever.task.task.ITask',
                        'opengever.meeting.proposal.IProposal',
                        'ftw.mail.mail.IMail',
                        ],
                    }),
            ),
        required=False,
        )

    mode(predecessor_proposal='hidden')
    predecessor_proposal = RelationChoice(
        title=_(u'predecessor_proposal_label', default=u'Predecessor proposal'),
        default=None,
        missing_value=None,
        required=False,
        source=SolrObjPathSourceBinder(portal_type='opengever.meeting.proposal')
        )


class ISubmittedProposal(IBaseProposal):

    excerpts = RelationList(
        title=_(u'label_excerpts', default=u'Excerpts'),
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            title=u'Excerpt',
            source=DossierPathSourceBinder(
                portal_type=('opengever.document.document',),
                navigation_tree_query={
                    'object_provides':
                    ['opengever.dossier.behaviors.dossier.IDossierMarker',
                     'opengever.document.document.IDocumentSchema'],
                }),
        ),
        required=False)


class ProposalBase(object):

    workflow = None

    def Title(self):
        return self.title.encode('utf-8')

    def get_description(self):
        return to_html_xweb_intelligent(self.description)

    def Description(self):
        return self.description.encode('utf-8')

    def get_overview_attributes(self):
        model = self.load_model()
        assert model, 'missing db-model for {}'.format(self)

        attributes = [
            {'label': _(u"label_title", default=u'Title'),
             'value': self.title},

            {'label': _(u"label_description", default=u'Description'),
             'value': self.get_description(),
             'is_html': True},

            {'label': _('label_committee', default=u'Committee'),
             'value': model.committee.get_link(),
             'is_html': True},

            {'label': _('label_meeting', default=u'Meeting'),
             'value': model.get_meeting_link(),
             'is_html': True},

            {'label': _('label_issuer', default=u'Issuer'),
             'value': Actor.lookup(self.issuer).get_label(),
             'is_html': True},
        ]

        proposal_document = self.get_proposal_document()
        if proposal_document:
            attributes.append({
                'label': _('proposal_document',
                           default=u'Proposal document'),
                'value': DocumentLinkWidget(proposal_document).render(),
                'is_html': True})

        attributes.extend([
            {'label': _('label_workflow_state', default=u'State'),
             'value': self.get_state().title,
             'is_html': True},

            {'label': _('label_decision_number', default=u'Decision number'),
             'value': model.get_decision_number(),
             'is_html': True},
        ])

        return attributes

    def can_execute_transition(self, name):
        return self.workflow.can_execute_transition(self.load_model(), name)

    def execute_transition(self, name, text=None):
        self.workflow.execute_transition(self, self.load_model(), name, text=text)

    def get_transitions(self):
        return self.workflow.get_transitions(self.get_state())

    def get_state(self):
        model = self.load_model()
        if model:
            return model.get_state()

        return self.workflow.default_state

    def get_physical_path(self):
        url_tool = api.portal.get_tool(name="portal_url")
        return '/'.join(url_tool.getRelativeContentPath(self))

    def get_committee_admin_unit(self):
        admin_unit_id = self.load_model().committee.admin_unit_id
        return ogds_service().fetch_admin_unit(admin_unit_id)

    def get_proposal_document(self):
        """If the word meeting implementation feature is enabled,
        this method returns the proposal document, containing the actual
        proposal "body".
        """
        if getattr(self, '_proposal_document_uuid', None) is None:
            return None

        document = uuidToObject(self._proposal_document_uuid)
        if document is None:
            raise ValueError('Proposal document seems to have vanished.')

        if aq_parent(aq_inner(document)) != self:
            raise ValueError('Proposal document is in wrong location.')

        return document

    def create_proposal_document(self, title=None, source_blob=None, **kwargs):
        """Creates a proposal document within this proposal or submitted
        proposal.
        Only one proposal document can be created.
        """
        if self.get_proposal_document():
            raise ValueError('There is already a proposal document.')

        if title:
            kwargs.setdefault('title', title)

        if source_blob:
            kwargs.setdefault('filename', source_blob.filename)
            kwargs.setdefault('data', source_blob.open().read())
            kwargs.setdefault('content_type', source_blob.contentType)

        kwargs['context'] = self
        kwargs.setdefault('preserved_as_paper', False)

        with elevated_privileges():
            obj = CreateDocumentCommand(**kwargs).execute()

        self._proposal_document_uuid = IUUID(obj)
        return obj

    def contains_checked_out_documents(self):
        for brain in api.content.find(context=self,
                                      portal_type='opengever.document.document'):
            if brain.checked_out:
                return True

        return False

    def comment(self, text, uuid=None):
        ProposalCommentedActivitiy(self, self.REQUEST).record()
        return IHistory(self).append_record(u'commented', uuid=uuid, text=text)

    def is_submitted(self):
        model = self.load_model()
        return model.is_submitted()


class SubmittedProposal(ModelContainer, ProposalBase):
    """Proxy for a proposal in queue with a committee."""

    content_schema = ISubmittedProposal
    model_schema = ISubmittedProposalModel
    model_class = ProposalModel

    implements(content_schema)
    workflow = ProposalModel.workflow.with_visible_transitions(
        ['submitted-pending'])

    def get_sync_admin_unit_id(self):
        return self.load_model().admin_unit_id

    def get_sync_target_path(self):
        return self.load_model().physical_path

    def is_editable(self):
        """A proposal in a meeting/committee is editable when submitted but not
        yet decided.

        """
        return self.load_model().is_editable_in_committee()

    def can_comment(self):
        return api.user.has_permission('Modify portal content', obj=self)

    def get_overview_attributes(self):
        data = super(SubmittedProposal, self).get_overview_attributes()

        # Insert dossier link if dossier exists after committee
        data.insert(
            2, {
                'label': _('label_dossier', default=u"Dossier"),
                'value': self.get_dossier_link(),
                'is_html': True,
            }
        )

        return data

    @classmethod
    def create(cls, proposal, container):
        submitted_proposal = api.content.create(
            type='opengever.meeting.submittedproposal',
            id=cls.generate_submitted_proposal_id(proposal),
            container=container)

        return submitted_proposal

    @classmethod
    def generate_submitted_proposal_id(cls, proposal):
        return 'submitted-proposal-{}'.format(proposal.proposal_id)

    def get_physical_path(self):
        url_tool = api.portal.get_tool(name="portal_url")
        return '/'.join(url_tool.getRelativeContentPath(self))

    def load_model(self):
        oguid = Oguid.for_object(self)
        if oguid is None:
            return None
        return ProposalModel.query.filter_by(
            submitted_oguid=Oguid.for_object(self)).first()

    def get_documents(self):
        catalog = api.portal.get_tool('portal_catalog')
        documents = catalog(
            portal_type=['opengever.document.document', 'ftw.mail.mail'],
            path=dict(query='/'.join(self.getPhysicalPath())),
            sort_on='sortable_title'
            )

        ignored_documents = [self.get_excerpt()]
        ignored_documents.append(self.get_proposal_document())

        all_docs = [document.getObject() for document in documents]
        return [doc for doc in all_docs if doc not in ignored_documents]

    def get_excerpt(self):
        return self.load_model().resolve_submitted_excerpt_document()

    def is_submit_additional_documents_allowed(self):
        return False

    def reject(self, text):
        """Reject the submitted proposal."""

        RejectProposalCommand(self).execute()
        proposal = self.load_model()
        proposal.reject(text)

        ProposalRejectedActivity(self, self.REQUEST).record()

        remove_watchers_on_submitted_proposal_deleted(
            self, proposal.committee.group_id)

        with elevated_privileges():
            api.content.delete(self)

    def get_containing_dossier(self):
        model = self.load_model()
        proposal = model.resolve_proposal()
        if not proposal:
            return None
        return get_containing_dossier(proposal)

    def get_dossier_link(self):
        dossier = self.get_containing_dossier()
        if not dossier:
            return _('label_dossier_not_available',
                     default=u"Dossier not available")

        return u'<a href="{0}" title="{1}">{1}</a>'.format(
            dossier.absolute_url(),
            dossier.title)

    def get_excerpts(self, unrestricted=False, include_trashed=False):
        """Return a restricted list of document objects which are excerpts
        of the current proposal.

        Sorted per excerpt title_or_id().
        """
        excerpts = []
        checkPermission = getSecurityManager().checkPermission
        for relation_value in getattr(self, 'excerpts', ()):
            obj = relation_value.to_object
            if unrestricted or checkPermission('View', obj):
                excerpts.append(obj)
        if not include_trashed:
            excerpts = filter(lambda obj: not ITrashed.providedBy(obj), excerpts)
        return sorted(excerpts, key=lambda excerpt: excerpt.title_or_id())

    def append_excerpt(self, excerpt_document):
        """Add a relation to a new excerpt document.
        """
        excerpts = getattr(self, 'excerpts', None)
        if not excerpts:
            # The missing_value attribute of a z3c-form field is used
            # as soon as an object has no default_value i.e. after creating
            # an object trough the command-line.
            #
            # Because the excerpts field needs a list as a missing_value,
            # we will fall into the "mutable keyword argument"-python gotcha.
            # The excerpts will be shared between the object-instances.
            #
            # Unfortunately the z3c-form field does not provide a
            # missing_value-factory (like the defaultFactory) which would be
            # necessary to fix this issue properly.
            #
            # As a workaround we reassign the field with a new list if the
            # excerpts-attribute has never been assigned before.
            excerpts = []

        intid = getUtility(IIntIds).getId(excerpt_document)
        excerpts.append(RelationValue(intid))
        self.excerpts = excerpts
        addRelations(self, None)

    def remove_excerpt(self, excerpt_document):
        if excerpt_document not in self.get_excerpts(include_trashed=True):
            raise ValueError("Excerpt not found in excerpts.")
        self.excerpts = filter(lambda excerpt: excerpt.to_object != excerpt_document, self.excerpts)

    def get_edit_values(self, fieldnames):
        """
        This is used by the 'inject_initial_data' method to prefill the edit
        form. The values are taken from the attributes of the model with
        the corresponding names. For a SubmittedProposal we want to prefill
        the form 'title' and 'description' fields with the 'submitted_title' and
        'submitted_description' attributes of the model, hence the replacement
        of the fieldname here.
        """
        fieldnames_to_modify = ['title', 'description']
        for fieldname in fieldnames_to_modify:
            if fieldname not in fieldnames:
                continue
            fieldnames[fieldnames.index(fieldname)] = 'submitted_' + fieldname
        values = super(SubmittedProposal, self).get_edit_values(fieldnames)
        for fieldname in fieldnames_to_modify:
            if 'submitted_' + fieldname not in fieldnames:
                continue
            values[fieldname] = values.pop('submitted_' + fieldname, '')
        return values


class Proposal(Container, ProposalBase):
    """Act as proxy for the proposal stored in the database.

    """
    implements(IProposal)

    workflow = ProposalModel.workflow.with_visible_transitions(
        ['pending-submitted'])

    def load_model(self):
        oguid = Oguid.for_object(self)
        if oguid is None:
            return None
        return ProposalModel.query.get_by_oguid(oguid)

    def get_sync_admin_unit_id(self):
        return self.load_model().submitted_admin_unit_id

    def get_sync_target_path(self):
        return self.load_model().submitted_physical_path

    def is_editable(self):
        """A proposal in a dossier is only editable while not submitted.

        It will remain editable on the submitted side but with a different set
        of editable attributes.

        """
        return self.load_model().is_editable_in_dossier()

    def can_comment(self):
        return api.user.has_permission('opengever.meeting: Add Proposal Comment', obj=self)

    def get_documents(self):
        return sorted(
            [relation.to_object for relation in self.relatedItems],
            key=lambda document: document.title_or_id(),
            )

    def get_excerpt(self):
        return self.load_model().resolve_excerpt_document()

    def has_active_committee(self):
        return self.load_model().committee.is_active()

    def get_committee(self):
        return Oguid.parse(self.committee_oguid).resolve_object()

    def get_containing_dossier(self):
        return get_containing_dossier(self)

    def get_repository_folder_title(self):
        main_dossier = self.get_containing_dossier().get_main_dossier()
        repository_folder = aq_parent(aq_inner(main_dossier))
        return repository_folder.Title(language=self.language,
                                       prefix_with_reference_number=False)

    def get_main_dossier_reference_number(self):
        return IReferenceNumber(self.get_main_dossier()).get_number()

    def is_submit_additional_documents_allowed(self):
        return self.load_model().is_submit_additional_documents_allowed()

    def submit_additional_document(self, document):
        assert self.is_submit_additional_documents_allowed()

        submitted_document = SubmittedDocument.query.get_by_source(
            self, document)
        proposal_model = self.load_model()

        if submitted_document:
            if submitted_document.is_up_to_date(document):
                command = NullUpdateSubmittedDocumentCommand(document)
            else:
                command = UpdateSubmittedDocumentCommand(
                    self, document, submitted_document)

        else:
            command = CopyProposalDocumentCommand(
                self,
                document,
                target_path=proposal_model.submitted_physical_path,
                target_admin_unit_id=proposal_model.submitted_admin_unit_id)

            if not self.relatedItems:
                # The missing_value attribute of a z3c-form field is used
                # as soon as an object has no default_value i.e. after creating
                # an object trough the command-line.
                #
                # Because the relatedItems field needs a list as a missing_value,
                # we will fall into the "mutable keyword argument"-python gotcha.
                # The relatedItems will be shared between the object-instances.
                #
                # Unfortunately the z3c-form field does not provide a
                # missing_value-factory (like the defaultFactory) which would be
                # necessary to fix this issue properly.
                #
                # As a workaround we reassign the field with a new list if the
                # relatedItems-attribute has never been assigned before.
                self.relatedItems = []

            self.relatedItems.append(
                RelationValue(getUtility(IIntIds).getId(document)))

        command.execute()
        return command

    def submit(self, text=None):
        self.date_of_submission = date.today()

        documents = self.get_documents()
        create_command = CreateSubmittedProposalCommand(self)
        copy_commands = [
            CopyProposalDocumentCommand(
                self, document,
                parent_action=create_command,
                record_activity=False)
            for document in documents]

        create_command.execute(text)
        for copy_command in copy_commands:
            copy_command.execute()

        ProposalSubmittedActivity(self, self.REQUEST).record()

    def reject(self):
        """Reject the proposal.

        Called via remote-request after the proposal has been rejected on the
        committee side.
        """

        ProposalRejectedActivity(self, self.REQUEST).record()
        self.date_of_submission = None
        api.content.transition(obj=self,
                               transition='proposal-transition-reject')

    def get_overview_attributes(self):
        data = super(Proposal, self).get_overview_attributes()

        if self.predecessor_proposal and self.predecessor_proposal.to_object:
            predecessor_model = self.predecessor_proposal.to_object.load_model()
            data.append({
                'label': _('label_predecessor', default=u'Predecessor'),
                'value': predecessor_model.get_link(),
                'is_html': True})

        catalog = getUtility(ICatalog)
        doc_id = getUtility(IIntIds).getId(aq_inner(self))
        successor_html_items = []
        for relation in catalog.findRelations({
                'to_id': doc_id,
                'from_attribute': 'predecessor_proposal'}):
            successor_html_items.append(u'<li>{}</li>'.format(
                relation.from_object.load_model().get_link()))
        if successor_html_items:
            data.append({
                'label': _('label_successors', default=u'Successors'),
                'value': u'<ul>{}</ul>'.format(''.join(successor_html_items)),
                'is_html': True})

        return data
