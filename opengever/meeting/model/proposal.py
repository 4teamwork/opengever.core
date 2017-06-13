from opengever.base.model import Base
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.base.utils import escape_html
from opengever.globalindex.model import WORKFLOW_STATE_LENGTH
from opengever.meeting import _
from opengever.meeting.model import AgendaItem
from opengever.meeting.model import proposalhistory
from opengever.meeting.model.generateddocument import GeneratedExcerpt
from opengever.meeting.workflow import State
from opengever.meeting.workflow import Transition
from opengever.meeting.workflow import Workflow
from opengever.ogds.base.utils import ogds_service
from opengever.ogds.models import UNIT_ID_LENGTH
from opengever.ogds.models import USER_ID_LENGTH
from opengever.ogds.models.types import UnicodeCoercingText
from plone import api
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import backref
from sqlalchemy.orm import composite
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence
from zope.globalrequest import getRequest


class Submit(Transition):

    def execute(self, obj, model):
        assert obj, 'submitting requires a plone context object.'

        if not model.committee.is_active():
            api.portal.show_message(
                _(u'msg_inactive_committee_selected',
                  default=u'The selected committeee has been deactivated, the'
                  ' proposal could not been submitted.'),
                request=getRequest(), type='error')
            return getRequest().RESPONSE.redirect(obj.absolute_url())

        super(Submit, self).execute(obj, model)
        api.content.transition(obj=obj, transition='proposal-transition-submit')
        obj.submit()

        msg = _(u'msg_proposal_submitted',
                default=u'Proposal successfully submitted.')
        api.portal.show_message(msg, request=getRequest())


class Reject(Transition):

    def execute(self, obj, model):
        url = "{}/reject_proposal".format(obj.absolute_url())
        return getRequest().RESPONSE.redirect(url)


class Cancel(Transition):

    def execute(self, obj, model):
        super(Cancel, self).execute(obj, model)
        model.cancel()

        msg = _(u'msg_proposal_cancelled',
                default=u'Proposal cancelled successfully.')
        api.portal.show_message(msg, request=getRequest(), type='info')


class Reactivate(Transition):

    def execute(self, obj, model):
        super(Reactivate, self).execute(obj, model)
        model.reactivate()

        msg = _(u'msg_proposal_reactivated',
                default=u'Proposal reactivated successfully.')
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
    physical_path = Column(String(256), nullable=False)
    creator = Column(String(USER_ID_LENGTH), nullable=False)

    submitted_admin_unit_id = Column(String(UNIT_ID_LENGTH))
    submitted_int_id = Column(Integer)
    submitted_oguid = composite(
        Oguid, submitted_admin_unit_id, submitted_int_id)
    submitted_physical_path = Column(String(256))

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

    history_records = relationship('ProposalHistory',
                                   order_by="desc(ProposalHistory.created)")

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
        Submit('pending', 'submitted',
               title=_('submit', default='Submit')),
        Reject('submitted', 'pending',
               title=_('reject', default='Reject')),
        Transition('submitted', 'scheduled',
                   title=_('schedule', default='Schedule')),
        Transition('scheduled', 'submitted',
                   title=_('un-schedule', default='Remove from schedule')),
        Transition('scheduled', 'decided',
                   title=_('decide', default='Decide')),
        Cancel('pending', 'cancelled',
               title=_('cancel', default='Cancel')),
        Reactivate('cancelled', 'pending',
                   title=_('reactivate', default='Reactivate')),
        ])

    def __repr__(self):
        return "<Proposal {}@{}>".format(self.int_id, self.admin_unit_id)

    def get_state(self):
        return self.workflow.get_state(self.workflow_state)

    def execute_transition(self, name):
        self.workflow.execute_transition(None, self, name)

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

    def get_searchable_text(self):
        # XXX: we no longer have additional searchable text
        return ''

    def get_decision(self):
        if self.agenda_item:
            return self.agenda_item.decision
        return None

    def get_decision_number(self):
        if self.agenda_item:
            return self.agenda_item.decision_number
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
        return self._get_link(self.get_url(),
                              self.resolve_proposal().title,
                              include_icon=include_icon)

    def get_submitted_link(self, include_icon=True):
        return self._get_link(self.get_submitted_url(),
                              self.resolve_submitted_proposal().title,
                              include_icon=include_icon)

    def _get_link(self, url, title, include_icon=True):
        title = escape_html(title)
        if include_icon:
            link = u'<a href="{0}" title="{1}" class="{2}">{1}</a>'.format(
                url, title, self.css_class)
        else:
            link = u'<a href="{0}" title="{1}">{1}</a>'.format(url, title)
        return link

    def getPath(self):
        """This method is required by a tabbedview."""

        return self.physical_path

    def resolve_submitted_proposal(self):
        return self.submitted_oguid.resolve_object()

    def resolve_submitted_documents(self):
        return [doc.resolve_submitted() for doc in self.submitted_documents]

    def has_submitted_documents(self):
        return self.submitted_documents or self.submitted_excerpt_document

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

    def is_editable_in_dossier(self):
        return self.get_state() == self.STATE_PENDING

    def is_editable_in_committee(self):
        return self.get_state() in [self.STATE_SUBMITTED, self.STATE_SCHEDULED]

    def schedule(self, meeting):
        assert self.can_be_scheduled()

        self.execute_transition('submitted-scheduled')
        session = create_session()
        meeting.agenda_items.append(AgendaItem(proposal=self))
        session.add(proposalhistory.Scheduled(proposal=self, meeting=meeting))

    def reject(self, text):
        assert self.workflow.can_execute_transition(self, 'submitted-pending')

        self.submitted_physical_path = None
        self.submitted_admin_unit_id = None
        self.submitted_int_id = None

        # kill references to submitted documents (i.e. copies), they will be
        # deleted.
        query = proposalhistory.ProposalHistory.query.filter_by(
            proposal=self)
        for record in query.all():
            record.submitted_document = None

        # set workflow state directly for once, the transition is used to
        # redirect to a form.
        self.workflow_state = self.STATE_PENDING.name
        session = create_session()
        session.add(proposalhistory.Rejected(proposal=self, text=text))

    def remove_scheduled(self, meeting):
        self.execute_transition('scheduled-submitted')
        session = create_session()
        session.add(
            proposalhistory.RemoveScheduled(proposal=self, meeting=meeting))

    def resolve_proposal(self):
        return self.oguid.resolve_object()

    def generate_excerpt(self, agenda_item):
        from opengever.meeting.command import CreateGeneratedDocumentCommand
        from opengever.meeting.command import ExcerptOperations

        proposal_obj = self.resolve_submitted_proposal()
        operations = ExcerptOperations(agenda_item)
        CreateGeneratedDocumentCommand(
            proposal_obj, agenda_item.meeting, operations).execute()

    def revise(self, agenda_item):
        assert self.get_state() == self.STATE_DECIDED
        self.update_excerpt(agenda_item)
        self.session.add(proposalhistory.ProposalRevised(proposal=self))

    def reopen(self, agenda_item):
        assert self.get_state() == self.STATE_DECIDED
        self.session.add(proposalhistory.ProposalReopened(proposal=self))

    def cancel(self):
        self.session.add(proposalhistory.Cancelled(proposal=self))

    def reactivate(self):
        self.session.add(proposalhistory.Reactivated(proposal=self))

    def update_excerpt(self, agenda_item):
        from opengever.meeting.command import ExcerptOperations
        from opengever.meeting.command import UpdateExcerptInDossierCommand
        from opengever.meeting.command import UpdateGeneratedDocumentCommand

        operations = ExcerptOperations(agenda_item)
        UpdateGeneratedDocumentCommand(
            self.submitted_excerpt_document,
            agenda_item.meeting,
            operations).execute()
        UpdateExcerptInDossierCommand(self).execute()

    def decide(self, agenda_item):
        self.generate_excerpt(agenda_item)
        document_intid = self.copy_excerpt_to_proposal_dossier()
        self.register_excerpt(document_intid)
        self.session.add(proposalhistory.ProposalDecided(proposal=self))
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
