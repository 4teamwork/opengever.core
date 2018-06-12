from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from collective import dexteritytextindexer
from datetime import date
from opengever.base.command import CreateDocumentCommand
from opengever.base.interfaces import IReferenceNumber
from opengever.base.oguid import Oguid
from opengever.base.security import elevated_privileges
from opengever.base.source import DossierPathSourceBinder
from opengever.base.source import SolrObjPathSourceBinder
from opengever.base.utils import get_preferred_language_code
from opengever.document.widgets.document_link import DocumentLinkWidget
from opengever.dossier.utils import get_containing_dossier
from opengever.meeting import _
from opengever.meeting.command import CopyProposalDocumentCommand
from opengever.meeting.command import CreateSubmittedProposalCommand
from opengever.meeting.command import NullUpdateSubmittedDocumentCommand
from opengever.meeting.command import RejectProposalCommand
from opengever.meeting.command import UpdateSubmittedDocumentCommand
from opengever.meeting.container import ModelContainer
from opengever.meeting.interfaces import IHistory
from opengever.meeting.model import SubmittedDocument
from opengever.meeting.model.proposal import Proposal as ProposalModel
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import ogds_service
from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.autoform.directives import mode
from plone.autoform.directives import omitted
from plone.supermodel import model
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import safe_unicode
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
    return context.title


class IProposalModel(Interface):
    """Proposal model schema interface."""

    committee = schema.Choice(
        title=_('label_committee', default=u'Committee'),
        source='opengever.meeting.ActiveCommitteeVocabulary',
        required=True)

    language = schema.Choice(
        title=_('language', default=u'Language'),
        source='opengever.meeting.LanguagesVocabulary',
        required=True,
        defaultFactory=get_preferred_language_code)


class ISubmittedProposalModel(Interface):
    """Submitted proposal model schema interface."""


class IProposal(model.Schema):
    """Proposal Proxy Object Schema Interface"""

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        required=True,
        max_length=256,
        defaultFactory=default_title
        )

    relatedItems = RelationList(
        title=_(u'label_attachments', default=u'Attachments'),
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            title=u"Related",
            source=DossierPathSourceBinder(
                portal_type=("opengever.document.document", "ftw.mail.mail"),
                navigation_tree_query={
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
        title=u'Predecessor proposal',
        default=None,
        missing_value=None,
        required=False,
        source=SolrObjPathSourceBinder(portal_type='opengever.meeting.proposal')
        )

    omitted('date_of_submission')
    date_of_submission = schema.Date(
        description=_('label_date_of_submission',
                      default='Date of submission'),
        default=None,
        missing_value=None,
        required=False,
        )


class ISubmittedProposal(IProposal):

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


class ProposalBase(ModelContainer):

    workflow = None

    def Title(self):
        return self.title.encode('utf-8')

    def get_overview_attributes(self):
        model = self.load_model()
        assert model, 'missing db-model for {}'.format(self)

        attributes = [
            {'label': _(u"label_title", default=u'Title'),
             'value': self.title},

            {'label': _('label_committee', default=u'Committee'),
             'value': model.committee.get_link(),
             'is_html': True},

            {'label': _('label_meeting', default=u'Meeting'),
             'value': model.get_meeting_link(),
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

        if self.predecessor_proposal and self.predecessor_proposal.to_object:
            predecessor_model = self.predecessor_proposal.to_object.load_model()
            attributes.append({
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
            attributes.append({
                'label': _('label_successors', default=u'Successors'),
                'value': u'<ul>{}</ul>'.format(''.join(successor_html_items)),
                'is_html': True})

        return attributes

    def can_execute_transition(self, name):
        if not api.user.has_permission('Modify portal content', obj=self):
            return False

        return self.workflow.can_execute_transition(self.load_model(), name)

    def execute_transition(self, name, text=None):
        self.workflow.execute_transition(self, self.load_model(), name, text=text)

    def get_transitions(self):
        if not api.user.has_permission('Modify portal content', obj=self):
            return []

        return self.workflow.get_transitions(self.get_state())

    def get_state(self):
        return self.load_model().get_state()

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

    def create_proposal_document(self, source_blob=None, **kwargs):
        """Creates a proposal document within this proposal or submitted
        proposal.
        Only one proposal document can be created.
        """
        if self.get_proposal_document():
            raise ValueError('There is already a proposal document.')

        if source_blob:
            kwargs.setdefault('filename', source_blob.filename)
            kwargs.setdefault('data', source_blob.open().read())
            kwargs.setdefault('content_type', source_blob.contentType)

        kwargs['context'] = self
        kwargs.setdefault('preserved_as_paper', False)

        kwargs.setdefault('title', safe_unicode(self.Title()))

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
        return IHistory(self).append_record(u'commented', uuid=uuid, text=text)


class SubmittedProposal(ProposalBase):
    """Proxy for a proposal in queue with a committee."""

    content_schema = ISubmittedProposal
    model_schema = ISubmittedProposalModel
    model_class = ProposalModel

    implements(content_schema)
    workflow = ProposalModel.workflow.with_visible_transitions(
        ['submitted-pending'])

    def get_source_admin_unit_id(self):
        return self.load_model().admin_unit_id

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

    def load_proposal(self, oguid):
        return ProposalModel.query.get_by_oguid(oguid)

    def sync_model(self, proposal_model=None):
        proposal_model = proposal_model or self.load_model()

        proposal_model.submitted_oguid = Oguid.for_object(self)
        proposal_model.submitted_physical_path = self.get_physical_path()
        proposal_model.submitted_admin_unit_id = get_current_admin_unit().id()
        proposal_model.submitted_title = self.title
        proposal_model.date_of_submission = self.date_of_submission

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

    def get_excerpts(self, unrestricted=False):
        """Return a restricted list of document objects which are excerpts
        of the current proposal.
        """
        excerpts = []
        checkPermission = getSecurityManager().checkPermission
        for relation_value in getattr(self, 'excerpts', ()):
            obj = relation_value.to_object
            if unrestricted or checkPermission('View', obj):
                excerpts.append(obj)

        return excerpts

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


class Proposal(ProposalBase):
    """Act as proxy for the proposal stored in the database.

    """
    content_schema = IProposal
    model_schema = IProposalModel
    model_class = ProposalModel

    implements(content_schema)

    workflow = ProposalModel.workflow.with_visible_transitions(
        ['pending-submitted', 'pending-cancelled', 'cancelled-pending'])

    def _after_model_created(self, model_instance):
        IHistory(self).append_record(u'created')

        if self.predecessor_proposal is not None:
            predecessor = self.predecessor_proposal.to_object
            IHistory(predecessor).append_record(
                u'successor_created',
                successor_oguid=Oguid.for_object(self).id)

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

    def get_committee(self):
        committee_model = self.load_model().committee
        return committee_model.oguid.resolve_object()

    def get_containing_dossier(self):
        return get_containing_dossier(self)

    def get_repository_folder_title(self, language):
        main_dossier = self.get_containing_dossier().get_main_dossier()
        repository_folder = aq_parent(aq_inner(main_dossier))
        return repository_folder.Title(language=language,
                                       prefix_with_reference_number=False)

    def update_model_create_arguments(self, data, context):
        aq_wrapped_self = self.__of__(context)

        workflow_state = self.workflow.default_state.name
        reference_number = IReferenceNumber(
            context.get_main_dossier()).get_number()

        language = data.get('language')
        repository_folder_title = safe_unicode(
            aq_wrapped_self.get_repository_folder_title(language))

        data.update(dict(workflow_state=workflow_state,
                         physical_path=aq_wrapped_self.get_physical_path(),
                         dossier_reference_number=reference_number,
                         repository_folder_title=repository_folder_title,
                         creator=aq_wrapped_self.Creator()))
        return data

    def update_model(self, data):
        language = data.get('language')
        data['repository_folder_title'] = safe_unicode(
            self.get_repository_folder_title(language))
        return super(Proposal, self).update_model(data)

    def sync_model(self, proposal_model=None):
        proposal_model = proposal_model or self.load_model()

        reference_number = IReferenceNumber(
            self.get_containing_dossier().get_main_dossier()).get_number()
        repository_folder_title = safe_unicode(self.get_repository_folder_title(
            proposal_model.language))

        proposal_model.physical_path = self.get_physical_path()
        proposal_model.dossier_reference_number = reference_number
        proposal_model.repository_folder_title = repository_folder_title
        proposal_model.title = self.title
        proposal_model.date_of_submission = self.date_of_submission

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
                self, document, parent_action=create_command)
            for document in documents]

        create_command.execute(text)
        for copy_command in copy_commands:
            copy_command.execute()

    def reject(self):
        """Reject the proposal.

        Called via remote-request after the proposal has been rejected on the
        committee side.
        """

        self.date_of_submission = None
        api.content.transition(obj=self,
                               transition='proposal-transition-reject')

    def is_submitted(self):
        model = self.load_model()
        return bool(model.submitted_physical_path)
