from AccessControl import getSecurityManager
from opengever.base.model import Base
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.base.utils import to_html_xweb_intelligent
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.globalindex.model import WORKFLOW_STATE_LENGTH
from opengever.meeting import _
from opengever.meeting.exceptions import MissingMeetingDossierPermissions
from opengever.meeting.exceptions import WrongAgendaItemState
from opengever.meeting.model import Period
from opengever.meeting.model.excerpt import Excerpt
from opengever.meeting.workflow import State
from opengever.meeting.workflow import Transition
from opengever.meeting.workflow import Workflow
from opengever.ogds.models import UNIT_ID_LENGTH
from opengever.base.types import UnicodeCoercingText
from opengever.trash.trash import ITrashable
from opengever.trash.trash import ITrashed
from plone import api
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import backref
from sqlalchemy.orm import composite
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence
from zope.component import getMultiAdapter


class AgendaItem(Base):
    """An item must either have a reference to a proposal or a title.

    """

    __tablename__ = 'agendaitems'

    # workflow definition
    STATE_PENDING = State('pending', is_default=True,
                          title=_('pending', default='Pending'))
    STATE_DECIDED = State('decided', title=_('decided', default='Decided'))
    STATE_REVISION = State('revision', title=_('revision', default='Revision'))

    workflow = Workflow(
        [STATE_PENDING, STATE_DECIDED, STATE_REVISION],
        [Transition('pending', 'decided',
                    title=_('decide', default='Decide')),
         Transition('decided', 'revision',
                    title=_('reopen', default='Reopen')),
         Transition('revision', 'decided',
                    title=_('revise', default='Revise')),
         ]
    )

    agenda_item_id = Column("id", Integer, Sequence("agendaitems_id_seq"),
                            primary_key=True)
    workflow_state = Column(String(WORKFLOW_STATE_LENGTH), nullable=False,
                            default=workflow.default_state.name)
    proposal_id = Column(Integer, ForeignKey('proposals.id'))
    proposal = relationship("Proposal", uselist=False,
                            backref=backref('agenda_item', uselist=False))

    ad_hoc_document_admin_unit_id = Column(String(UNIT_ID_LENGTH))
    ad_hoc_document_int_id = Column(Integer)
    ad_hoc_document_oguid = composite(
        Oguid, ad_hoc_document_admin_unit_id, ad_hoc_document_int_id)

    decision_number = Column(Integer)

    title = Column(UnicodeCoercingText)
    description = Column(UnicodeCoercingText)
    number = Column('item_number', String(16))
    is_paragraph = Column(Boolean, nullable=False, default=False)
    sort_order = Column(Integer, nullable=False, default=0)

    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)

    def __init__(self, *args, **kwargs):
        proposal = kwargs.get('proposal')
        document = kwargs.pop('document', None)
        if document:
            assert not proposal, 'must only have one of proposal and document'
            kwargs.update(
                {'ad_hoc_document_oguid': Oguid.for_object(document)})

        super(AgendaItem, self).__init__(*args, **kwargs)

    def get_agenda_item_data(self):
        data = {
            'number': self.number,
            'description': self.get_description(),
            'title': self.get_title(),
            'dossier_reference_number': self.get_dossier_reference_number(),
            'repository_folder_title': self.get_repository_folder_title(),
            'is_paragraph': self.is_paragraph,
            'decision_number': self.decision_number
        }
        self._add_attachment_data(data)
        return data

    def _add_attachment_data(self, data):
        if not self.has_proposal:
            return

        documents = self.proposal.resolve_submitted_documents()
        if not documents:
            return

        attachment_data = []
        for document in documents:
            attachment = {'title': document.title}
            filename = document.get_filename()
            if filename:
                attachment['filename'] = filename
            attachment_data.append(attachment)
        data['attachments'] = attachment_data

    @property
    def submitted_proposal(self):
        if not hasattr(self, '_submitted_proposal'):
            self._submitted_proposal = self.proposal.resolve_submitted_proposal()  # noqa
        return self._submitted_proposal

    def get_title(self, include_number=False):
        title = (self.submitted_proposal.title
                 if self.has_proposal else self.title)
        if include_number and self.number:
            title = u"{} {}".format(self.number, title)

        return title

    def get_title_html(self, include_number=False):
        return to_html_xweb_intelligent(self.get_title(include_number=include_number))

    def set_title(self, title):
        if self.has_proposal:
            self.submitted_proposal.title = title
            self.submitted_proposal.sync_model()
        else:
            self.title = title

    def get_description(self):
        return (self.submitted_proposal.description if self.has_proposal
                else self.description)

    def get_description_html(self):
        return to_html_xweb_intelligent(self.get_description()) or None

    def set_description(self, description):
        if self.has_proposal:
            self.submitted_proposal.description = description
            self.submitted_proposal.sync_model()
        else:
            self.description = description

    def get_decision_number(self):
        # XXX huh? what is this?
        if not self.decision_number:
            return self.decision_number

        period = Period.query.get_current_for_update(self.meeting.committee)
        year = period.date_from.year
        return '{} / {}'.format(year, self.decision_number)

    def get_dossier_reference_number(self):
        if self.has_proposal:
            return self.proposal.dossier_reference_number
        return None

    def get_excerpt_header_template(self):
        return self.meeting.committee.get_excerpt_header_template()

    def get_excerpt_suffix_template(self):
        return self.meeting.committee.get_excerpt_suffix_template()

    def get_repository_folder_title(self):
        if self.has_proposal:
            return self.proposal.repository_folder_title
        return None

    def get_css_class(self):
        css_classes = []
        if self.is_paragraph:
            css_classes.append("paragraph")
        if self.has_submitted_documents():
            css_classes.append("expandable")
        if self.has_proposal:
            css_classes.append("proposal")
        return " ".join(css_classes)

    def get_state(self):
        return self.workflow.get_state(self.workflow_state)

    def generate_decision_number(self, period):
        if self.is_paragraph:
            return

        next_decision_number = period.get_next_decision_sequence_number()
        self.decision_number = next_decision_number

    def remove(self):
        assert self.meeting.is_editable()

        # the agenda_item is ad hoc if it has a document but no proposal
        if self.has_document and not self.has_proposal:
            document = self.resolve_document()
            trasher = ITrashable(document)
            trasher.trash()

        session = create_session()
        if self.proposal:
            self.proposal.remove_scheduled(self.meeting)
        session.delete(self)
        self.meeting.reorder_agenda_items()

    def get_proposal_link(self, include_icon=True):
        if not self.has_proposal:
            return self.get_title_html()

        return self.proposal.get_submitted_link(include_icon=include_icon)

    def serialize(self):
        return {
            'id': self.agenda_item_id,
            'css_class': self.get_css_class(),
            'title': self.get_title_html(),
            'description': self.get_description_html(),
            'number': self.number,
            'has_proposal': self.has_proposal,
            'link': self.get_proposal_link(include_icon=False),
        }

    @property
    def has_proposal(self):
        return self.proposal is not None

    @property
    def has_document(self):
        return self.has_proposal or self.ad_hoc_document_int_id is not None

    def resolve_document(self):
        if not self.has_document:
            return None

        if self.has_proposal:
            proposal = self.proposal.resolve_submitted_proposal()
            return proposal.get_proposal_document()

        return self.ad_hoc_document_oguid.resolve_object()

    def checkin_document(self):
        document = self.resolve_document()
        if not document:
            return

        checkout_manager = getMultiAdapter((document, document.REQUEST),
                                           ICheckinCheckoutManager)
        checkout_manager.checkin()

    @property
    def name(self):
        """Currently used as name for input tags in html."""

        return "agenda_item-{}".format(self.agenda_item_id)

    def has_submitted_documents(self):
        return self.has_proposal and self.proposal.has_submitted_documents()

    def resolve_submitted_documents(self):
        if not self.has_proposal:
            return []

        return self.proposal.resolve_submitted_documents()

    def has_submitted_excerpt_document(self):
        return self.has_proposal and self.proposal.has_submitted_excerpt_document()

    def close(self):
        """Close the agenda item.

        Can be called to close an agenda item, this puts the agenda item in
        decided state using the correct transitions. Currently valid states
        are:
        decided: do nothing
        pending: decide
        revision: revise
        """
        if self.is_revise_possible():
            self.revise()
        self.decide()

    def is_decide_possible(self):
        if not self.is_paragraph:
            return self.get_state() == self.STATE_PENDING
        return False

    def is_decided(self):
        if not self.is_paragraph:
            return self.get_state() == self.STATE_DECIDED
        return False

    def decide(self):
        if self.get_state() == self.STATE_DECIDED:
            return

        self.meeting.hold()

        self.workflow.execute_transition(None, self, 'pending-decided')

    def reopen(self):
        """If the excerpt has been sent back so that the proposal is
        decided, we also have to reopen the proposal"""
        if self.has_proposal and self.is_proposal_decided():
            self.proposal.reopen(self)
        self.workflow.execute_transition(None, self, 'decided-revision')

    def is_reopen_possible(self):
        if not self.is_paragraph:
            return self.get_state() == self.STATE_DECIDED
        return False

    def is_proposal_decided(self):
        if not self.has_proposal:
            return False
        return self.proposal.is_decided()

    def is_completed(self):
        """An ad-hoc agendaitem is completed when it is decided, whereas an
        agendaitem with proposal needs to be decided, the excerpt generated
        and returned to the proposal. A paragraph is always considered completed.
        """
        if self.is_paragraph:
            return True
        if self.has_proposal:
            return self.is_decided() and self.is_proposal_decided()
        return self.is_decided()

    def revise(self):
        """If the excerpt has been sent back so that the proposal is
        decided, we also have to revise the proposal"""
        if not self.is_revise_possible():
            raise WrongAgendaItemState()

        if self.has_proposal and self.is_proposal_decided():
            self.proposal.revise(self)
        self.workflow.execute_transition(None, self, 'revision-decided')

    def is_revise_possible(self):
        if not self.is_paragraph:
            return self.get_state() == self.STATE_REVISION
        return False

    def return_excerpt(self, document):
        # Agendaitems that were decided before we introduced that
        # proposals get decided only when the excerpt is returned
        # can be already decided even if the proposal has not been returned.
        if not self.is_proposal_decided():
            self.proposal.decide(self)
        self.proposal.return_excerpt(document)

    def generate_excerpt(self, title):
        """Generate an excerpt from the agenda items document.

        Can either be an excerpt from the proposals document or an excerpt
        from the ad-hoc agenda items document.
        In both cases the excerpt is stored in the meeting dossier.
        """

        from opengever.meeting.command import MergeDocxExcerptCommand

        if not self.can_generate_excerpt():
            raise WrongAgendaItemState()

        meeting_dossier = self.meeting.get_dossier()
        source_document = self.resolve_document()

        if not source_document:
            raise ValueError('The agenda item has no document.')

        if not api.user.get_current().checkPermission(
                'opengever.document: Add document', meeting_dossier):
            raise MissingMeetingDossierPermissions

        excerpt_document = MergeDocxExcerptCommand(
            context=meeting_dossier,
            agenda_item=self,
            filename=source_document.get_file().filename,
            title=title,
        ).execute()

        if self.has_proposal:
            submitted_proposal = self.proposal.resolve_submitted_proposal()
            submitted_proposal.append_excerpt(excerpt_document)
        else:
            self.excerpts.append(Excerpt(
                excerpt_oguid=Oguid.for_object(excerpt_document)))

        return excerpt_document

    def can_generate_excerpt(self):
        """Return whether excerpts can be generated."""

        if not self.meeting.is_editable():
            return False

        return self.get_state() == self.STATE_DECIDED

    def get_excerpt_documents(self, unrestricted=False, include_trashed=False):
        """Return a list of excerpt documents.

        If the agenda items has a proposal return the proposals excerpt
        documents. Otherwise return the excerpts stored in the meeting
        dossier.
        """
        if self.has_proposal:
            return self.submitted_proposal.get_excerpts(unrestricted=unrestricted,
                                                        include_trashed=include_trashed)

        checkPermission = getSecurityManager().checkPermission
        documents = [excerpt.resolve_document() for excerpt in self.excerpts]
        documents = filter(None, documents)
        if not unrestricted:
            documents = filter(lambda obj: checkPermission('View', obj), documents)
        if not include_trashed:
            documents = filter(lambda obj: not ITrashed.providedBy(obj), documents)
        return documents

    def get_source_dossier_excerpt(self):
        if not self.has_proposal:
            return None

        return self.proposal.resolve_submitted_excerpt_document()
