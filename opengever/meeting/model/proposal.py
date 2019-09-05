from opengever.base import advancedjson
from opengever.base.model import Base
from opengever.base.model import UNIT_ID_LENGTH
from opengever.base.model import USER_ID_LENGTH
from opengever.base.oguid import Oguid
from opengever.base.request import dispatch_request
from opengever.base.request import expect_ok_response
from opengever.base.types import UnicodeCoercingText
from opengever.base.utils import escape_html
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.globalindex.model import WORKFLOW_STATE_LENGTH
from opengever.meeting import _
from opengever.meeting.activity.activities import ProposalDecideActivity
from opengever.meeting.activity.activities import ProposalScheduledActivity
from opengever.meeting.interfaces import IHistory
from opengever.meeting.model import AgendaItem
from opengever.meeting.model.generateddocument import GeneratedExcerpt
from opengever.meeting.workflow import State
from opengever.meeting.workflow import Transition
from opengever.meeting.workflow import Workflow
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import ogds_service
from plone import api
from Products.CMFPlone.utils import safe_unicode
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import backref
from sqlalchemy.orm import composite
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest


MAX_TITLE_LENGTH = 256


class Reject(Transition):

    def execute(self, obj, model, text=None, **kwargs):
        obj.reject(text)
        msg = _(u"The proposal has been rejected successfully")
        api.portal.show_message(msg, request=getRequest(), type='info')


class Proposal(Base):
    """Sql representation of a proposal."""

    __tablename__ = 'proposals'
    __table_args__ = (
        UniqueConstraint('admin_unit_id', 'int_id'),
        UniqueConstraint('submitted_admin_unit_id', 'submitted_int_id'),
        {})

    proposal_id = Column("id", Integer, Sequence("proposal_id_seq"),
                         primary_key=True)
    admin_unit_id = Column(String(UNIT_ID_LENGTH), nullable=False)
    int_id = Column(Integer, nullable=False)
    oguid = composite(Oguid, admin_unit_id, int_id)
    physical_path = Column(UnicodeCoercingText, nullable=False)
    issuer = Column(String(USER_ID_LENGTH), nullable=False)

    title = Column(String(MAX_TITLE_LENGTH), index=True)
    submitted_title = Column(String(MAX_TITLE_LENGTH), index=True)

    description = Column(UnicodeCoercingText)
    submitted_description = Column(UnicodeCoercingText)

    date_of_submission = Column(Date, index=True)

    submitted_admin_unit_id = Column(String(UNIT_ID_LENGTH))
    submitted_int_id = Column(Integer)
    submitted_oguid = composite(
        Oguid, submitted_admin_unit_id, submitted_int_id)
    submitted_physical_path = Column(UnicodeCoercingText)

    excerpt_document_id = Column(Integer, ForeignKey('generateddocuments.id'))
    excerpt_document = relationship(
        'GeneratedExcerpt', uselist=False,
        backref=backref('proposal', uselist=False),
        primaryjoin="GeneratedExcerpt.document_id==Proposal.excerpt_document_id")

    submitted_excerpt_document_id = Column(Integer,
                                           ForeignKey('generateddocuments.id'))
    submitted_excerpt_document = relationship(
        'GeneratedExcerpt', uselist=False,
        backref=backref('submitted_proposal', uselist=False),
        primaryjoin="GeneratedExcerpt.document_id==Proposal.submitted_excerpt_document_id")

    workflow_state = Column(String(WORKFLOW_STATE_LENGTH), nullable=False)

    committee_id = Column(Integer, ForeignKey('committees.id'))
    committee = relationship('Committee', backref='proposals')
    dossier_reference_number = Column(UnicodeCoercingText, nullable=False)
    repository_folder_title = Column(UnicodeCoercingText, nullable=False)
    language = Column(String(8), nullable=False)

    __mapper_args__ = {
        "order_by": proposal_id
    }

    # workflow definition
    STATE_PENDING = State('pending', is_default=True,
                          title=_('pending', default='Pending'))
    STATE_SUBMITTED = State('submitted',
                            title=_('submitted', default='Submitted'))
    STATE_SCHEDULED = State('scheduled',
                            title=_('scheduled', default='Scheduled'))
    STATE_DECIDED = State('decided', title=_('decided', default='Decided'))
    STATE_CANCELLED = State('cancelled',
                            title=_('cancelled', default='Cancelled'))

    workflow = Workflow([
        STATE_PENDING,
        STATE_SUBMITTED,
        STATE_SCHEDULED,
        STATE_DECIDED,
        STATE_CANCELLED,
        ], [
        Reject('submitted', 'pending',
               title=_('reject', default='Reject')),
        Transition('submitted', 'scheduled',
                   title=_('schedule', default='Schedule')),
        Transition('scheduled', 'submitted',
                   title=_('un-schedule', default='Remove from schedule')),
        Transition('scheduled', 'decided',
                   title=_('decide', default='Decide')),
        ])

    # temporary mapping for plone workflow state to model workflow state
    WORKFLOW_STATE_TO_SQL_STATE = {
        'proposal-state-active': 'pending',
        'proposal-state-cancelled': 'cancelled',
        'proposal-state-submitted': 'submitted',
    }

    def __repr__(self):
        return "<Proposal {}@{}>".format(self.int_id, self.admin_unit_id)

    @classmethod
    def create_from(cls, proposal):
        model = cls(oguid=Oguid.for_object(proposal),
                    workflow_state='pending',
                    physical_path=proposal.get_physical_path())
        model.sync_with_proposal(proposal)
        return model

    def sync_with_proposal(self, proposal):
        """Sync self with a plone proposal instance."""

        from opengever.meeting.model.committee import Committee

        reference_number = proposal.get_main_dossier_reference_number()
        repository_folder_title = safe_unicode(
            proposal.get_repository_folder_title())
        committee = Committee.get_one(
            oguid=Oguid.parse(proposal.committee_oguid))

        # temporarily use mapping from plone workflow state to model workflow
        # state
        workflow_state = api.content.get_state(proposal)
        new_sql_state = self.WORKFLOW_STATE_TO_SQL_STATE.get(workflow_state)
        if new_sql_state:
            self.workflow_state = new_sql_state

        self.committee = committee
        self.language = proposal.language
        self.physical_path = proposal.get_physical_path()
        self.dossier_reference_number = reference_number
        self.repository_folder_title = repository_folder_title
        self.title = proposal.title
        self.issuer = proposal.issuer
        self.description = proposal.description
        self.date_of_submission = proposal.date_of_submission

    def sync_with_submitted_proposal(self, submitted_proposal):
        """Sync self with a plone submitted proposal instance."""

        self.submitted_oguid = Oguid.for_object(submitted_proposal)
        self.submitted_physical_path = submitted_proposal.get_physical_path()
        self.submitted_admin_unit_id = get_current_admin_unit().id()
        self.submitted_title = submitted_proposal.title
        self.submitted_description = submitted_proposal.description
        self.date_of_submission = submitted_proposal.date_of_submission

    def get_state(self):
        return self.workflow.get_state(self.workflow_state)

    def execute_transition(self, name, text=None):
        self.workflow.execute_transition(None, self, name, text=text)

    def get_admin_unit(self):
        return ogds_service().fetch_admin_unit(self.admin_unit_id)

    def get_submitted_admin_unit(self):
        return ogds_service().fetch_admin_unit(self.submitted_admin_unit_id)

    @property
    def id(self):
        return self.proposal_id

    @property
    def css_class(self):
        return 'contenttype-opengever-meeting-proposal'

    def get_decision_number(self):
        if self.agenda_item:
            return self.agenda_item.get_decision_number()
        return None

    def get_url(self):
        return self._get_url(self.get_admin_unit(), self.physical_path)

    def get_submitted_url(self):
        return self._get_url(self.get_submitted_admin_unit(),
                             self.submitted_physical_path)

    def _get_url(self, admin_unit, physical_path):
        if not (admin_unit and physical_path):
            return ''
        return '/'.join((admin_unit.public_url, physical_path))

    def get_link(self, include_icon=True):
        proposal_ = self.resolve_proposal()
        as_link = proposal_ is None or api.user.has_permission('View', obj=proposal_)
        return self._get_link(self.get_url(),
                              self.title,
                              include_icon=include_icon,
                              as_link=as_link)

    def get_description(self):
        proposal_ = self.resolve_proposal()
        return proposal_.get_description()

    def get_submitted_description(self):
        proposal_ = self.resolve_submitted_proposal()
        return proposal_.get_description()

    def get_submitted_link(self, include_icon=True):
        proposal_ = self.resolve_submitted_proposal()
        as_link = proposal_ is None or api.user.has_permission('View', obj=proposal_)
        return self._get_link(self.get_submitted_url(),
                              proposal_.title,
                              include_icon=include_icon,
                              as_link=as_link)

    def _get_link(self, url, title, include_icon=True, as_link=True):
        title = escape_html(title)
        if as_link:
            if include_icon:
                link = u'<a href="{0}" title="{1}" class="{2}">{1}</a>'.format(
                    url, title, self.css_class)
            else:
                link = u'<a href="{0}" title="{1}">{1}</a>'.format(url, title)
            return link

        if include_icon:
            link = u'<span title="{0}" class="{1}">{0}</span>'.format(
                title, self.css_class)
        else:
            link = u'<span title="{0}">{0}</a>'.format(title)
        return link

    def getPath(self):
        """This method is required by a tabbedview."""

        return self.physical_path

    def resolve_submitted_proposal(self):
        return self.submitted_oguid.resolve_object()

    def resolve_submitted_documents(self):
        return [doc.resolve_submitted() for doc in self.submitted_documents]

    def has_submitted_documents(self):
        return bool(self.submitted_documents)

    def resolve_excerpt_document(self):
        document = self.excerpt_document
        if document:
            return document.oguid.resolve_object()

    def has_submitted_excerpt_document(self):
        return self.submitted_excerpt_document is not None

    def resolve_submitted_excerpt_document(self):
        document = self.submitted_excerpt_document
        if document:
            return document.oguid.resolve_object()

    def can_be_scheduled(self):
        return self.get_state() == self.STATE_SUBMITTED

    def is_submit_additional_documents_allowed(self):
        return self.get_state() in [self.STATE_SUBMITTED, self.STATE_SCHEDULED]

    def is_editable_in_committee(self):
        return self.get_state() in [self.STATE_SUBMITTED, self.STATE_SCHEDULED]

    def schedule(self, meeting):
        assert self.can_be_scheduled()

        self.execute_transition('submitted-scheduled')
        meeting.agenda_items.append(AgendaItem(proposal=self))
        meeting.reorder_agenda_items()

        submitted_proposal = self.resolve_submitted_proposal()
        ProposalScheduledActivity(
            submitted_proposal, getRequest(), meeting.meeting_id).record()
        IHistory(self.resolve_submitted_proposal()).append_record(
            u'scheduled', meeting_id=meeting.meeting_id)

        request_data = {'data': advancedjson.dumps({
            'meeting_id': meeting.meeting_id,
        })}
        expect_ok_response(
            dispatch_request(self.admin_unit_id,
                             '@@receive-proposal-scheduled',
                             path=self.physical_path,
                             data=request_data),
            'Unexpected response {!r} when scheduling proposal.'
        )

    def reject(self, text):
        assert self.workflow.can_execute_transition(self, 'submitted-pending')

        self.submitted_physical_path = None
        self.submitted_admin_unit_id = None
        self.submitted_int_id = None
        self.date_of_submission = None

        # set workflow state directly for once, the transition is used to
        # redirect to a form.
        self.workflow_state = self.STATE_PENDING.name
        IHistory(self.resolve_proposal()).append_record(u'rejected', text=text)

    def remove_scheduled(self, meeting):
        self.execute_transition('scheduled-submitted')
        IHistory(self.resolve_submitted_proposal()).append_record(
            u'remove_scheduled', meeting_id=meeting.meeting_id)

    def resolve_proposal(self):
        return self.oguid.resolve_object()

    def revise(self, agenda_item):
        assert self.get_state() == self.STATE_DECIDED

        document = self.resolve_submitted_proposal().get_proposal_document()
        checkout_manager = getMultiAdapter((document, document.REQUEST),
                                           ICheckinCheckoutManager)
        if checkout_manager.get_checked_out_by() is not None:
            raise ValueError(
                'Cannot revise proposal when proposal document is checked out.')

        IHistory(self.resolve_submitted_proposal()).append_record(u'revised')

    def is_decided(self):
        return self.get_state() == self.STATE_DECIDED

    def reopen(self, agenda_item):
        assert self.is_decided()
        IHistory(self.resolve_submitted_proposal()).append_record(u'reopened')

    def decide(self, agenda_item):
        document = self.resolve_submitted_proposal().get_proposal_document()
        checkout_manager = getMultiAdapter((document, document.REQUEST),
                                           ICheckinCheckoutManager)
        if checkout_manager.get_checked_out_by() is not None:
            raise ValueError(
                'Cannot decide proposal when proposal document is checked out.')

        submitted_proposal = self.resolve_submitted_proposal()
        ProposalDecideActivity(submitted_proposal, getRequest()).record()
        IHistory(submitted_proposal).append_record(u'decided')
        self.execute_transition('scheduled-decided')

    def register_excerpt(self, document_intid):
        """Adds a GeneratedExcerpt database entry and a corresponding
        proposalhistory entry.
        """
        version = self.submitted_excerpt_document.generated_version
        excerpt = GeneratedExcerpt(admin_unit_id=self.admin_unit_id,
                                   int_id=document_intid,
                                   generated_version=version)
        self.session.add(excerpt)
        self.excerpt_document = excerpt

    def return_excerpt(self, document):
        """Return the selected excerpt to the proposals originating dossier.

        The document is registered as official excerpt for this proposal and
        copied to the dossier. Future edits in the excerpt document will
        be synced to the proposals dossier.

        """
        assert document in self.resolve_submitted_proposal().get_excerpts()

        version = document.get_current_version_id(missing_as_zero=True)
        excerpt = GeneratedExcerpt(
            oguid=Oguid.for_object(document), generated_version=version)
        self.submitted_excerpt_document = excerpt

        document_intid = self.copy_excerpt_to_proposal_dossier()
        self.register_excerpt(document_intid)

    def copy_excerpt_to_proposal_dossier(self):
        """Copies the submitted excerpt to the source dossier and returns
        the intid of the created document.
        """
        from opengever.meeting.command import CreateExcerptCommand

        dossier = self.resolve_proposal().get_containing_dossier()
        response = CreateExcerptCommand(
            self.resolve_submitted_excerpt_document(),
            self.admin_unit_id,
            '/'.join(dossier.getPhysicalPath())).execute()
        return response['intid']

    def get_meeting_link(self):
        agenda_item = self.agenda_item
        if not agenda_item:
            return u''

        return agenda_item.meeting.get_link()
