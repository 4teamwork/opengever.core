from opengever.base.model import Base
from opengever.base.model import create_session
from opengever.base.transforms import trix2sablon
from opengever.base.widgets import trix_strip_whitespace
from opengever.globalindex.model import WORKFLOW_STATE_LENGTH
from opengever.meeting import _
from opengever.meeting.workflow import State
from opengever.meeting.workflow import Transition
from opengever.meeting.workflow import Workflow
from opengever.ogds.models.types import UnicodeCoercingText
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


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
    decision_number = Column(Integer)

    title = Column(UnicodeCoercingText)
    number = Column('item_number', String(16))
    is_paragraph = Column(Boolean, nullable=False, default=False)
    sort_order = Column(Integer, nullable=False, default=0)

    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)

    discussion = Column(UnicodeCoercingText)
    decision = Column(UnicodeCoercingText)

    def __init__(self, *args, **kwargs):
        """Prefill the decision attributes with proposal's decision_draft.
        """
        proposal = kwargs.get('proposal')
        if proposal and not kwargs.get('decision'):
            submitted_proposal = proposal.resolve_submitted_proposal()
            decision_draft = submitted_proposal.decision_draft
            kwargs.update({'decision': decision_draft})

        super(AgendaItem, self).__init__(*args, **kwargs)

    def update(self, request):
        """Update with changed data."""

        data = request.get(self.name)
        if not data:
            return

        def to_safe_html(markup):
            # keep empty data (whatever it is), it makes transform unhappy
            if not markup:
                return markup

            markup = markup.decode('utf-8')
            markup = trix2sablon.convert(markup)
            return trix_strip_whitespace(markup)

        if self.has_proposal:
            self.submitted_proposal.legal_basis = to_safe_html(data.get('legal_basis'))
            self.submitted_proposal.initial_position = to_safe_html(data.get('initial_position'))
            self.submitted_proposal.considerations = to_safe_html(data.get('considerations'))
            self.submitted_proposal.proposed_action = to_safe_html(data.get('proposed_action'))
            self.submitted_proposal.publish_in = to_safe_html(data.get('publish_in'))
            self.submitted_proposal.disclose_to = to_safe_html(data.get('disclose_to'))
            self.submitted_proposal.copy_for_attention = to_safe_html(data.get('copy_for_attention'))

        self.discussion = to_safe_html(data.get('discussion'))
        self.decision = to_safe_html(data.get('decision'))

    def get_field_data(self, include_initial_position=True,
                       include_legal_basis=True, include_considerations=True,
                       include_proposed_action=True, include_discussion=True,
                       include_decision=True, include_publish_in=True,
                       include_disclose_to=True,
                       include_copy_for_attention=True):
        data = {
            'number': self.number,
            'description': self.description,
            'title': self.get_title(),
            'dossier_reference_number': self.get_dossier_reference_number(),
            'repository_folder_title': self.get_repository_folder_title(),
            'is_paragraph': self.is_paragraph,
            'decision_number': self.decision_number,
            'html:decision_draft': self._sanitize_text(
                self.get_decision_draft())}

        if include_initial_position:
            data['html:initial_position'] = self._sanitize_text(
                self.initial_position)
        if include_legal_basis:
            data['html:legal_basis'] = self._sanitize_text(
                self.legal_basis)
        if include_considerations:
            data['html:considerations'] = self._sanitize_text(
                self.considerations)
        if include_proposed_action:
            data['html:proposed_action'] = self._sanitize_text(
                self.proposed_action)
        if include_discussion:
            data['html:discussion'] = self._sanitize_text(self.discussion)
        if include_decision:
            data['html:decision'] = self._sanitize_text(self.decision)
        if include_publish_in:
            data['html:publish_in'] = self._sanitize_text(self.publish_in)
        if include_disclose_to:
            data['html:disclose_to'] = self._sanitize_text(
                self.disclose_to)
        if include_copy_for_attention:
            data['html:copy_for_attention'] = self._sanitize_text(
                self.copy_for_attention)

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

    def _sanitize_text(self, text):
        if not text:
            return None

        return text

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

    def set_title(self, title):
        if self.has_proposal:
            self.submitted_proposal.title = title
        else:
            self.title = title

    def get_decision_draft(self):
        if self.has_proposal:
            return self.submitted_proposal.decision_draft

    def get_dossier_reference_number(self):
        if self.has_proposal:
            return self.proposal.dossier_reference_number
        return None

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

        session = create_session()
        if self.proposal:
            self.proposal.remove_scheduled(self.meeting)
        session.delete(self)
        self.meeting.reorder_agenda_items()

    def get_proposal_link(self, include_icon=True):
        if not self.has_proposal:
            return self.get_title()

        return self.proposal.get_submitted_link(include_icon=include_icon)

    def serialize(self):
        return {
            'id': self.agenda_item_id,
            'css_class': self.get_css_class(),
            'title': self.get_title(),
            'number': self.number,
            'has_proposal': self.has_proposal,
            'link': self.get_proposal_link(include_icon=False),
            }

    @property
    def has_proposal(self):
        return self.proposal is not None

    @property
    def legal_basis(self):
        return self.submitted_proposal.legal_basis if self.has_proposal else None

    @property
    def initial_position(self):
        return self.submitted_proposal.initial_position if self.has_proposal else None

    @property
    def considerations(self):
        return self.submitted_proposal.considerations if self.has_proposal else None

    @property
    def proposed_action(self):
        return self.submitted_proposal.proposed_action if self.has_proposal else None

    @property
    def publish_in(self):
        return self.submitted_proposal.publish_in if self.has_proposal else None

    @property
    def disclose_to(self):
        return self.submitted_proposal.disclose_to if self.has_proposal else None

    @property
    def copy_for_attention(self):
        return self.submitted_proposal.copy_for_attention if self.has_proposal else None

    @property
    def name(self):
        """Currently used as name for input tags in html."""

        return "agenda_item-{}".format(self.agenda_item_id)

    @property
    def description(self):
        return self.get_title()

    def has_submitted_documents(self):
        return self.has_proposal and self.proposal.has_submitted_documents()

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

        if self.has_proposal:
            self.proposal.decide(self)

        self.workflow.execute_transition(None, self, 'pending-decided')

    def reopen(self):
        if self.has_proposal:
            self.proposal.reopen(self)
        self.workflow.execute_transition(None, self, 'decided-revision')

    def is_reopen_possible(self):
        if not self.is_paragraph:
            return self.get_state() == self.STATE_DECIDED
        return False

    def revise(self):
        assert self.is_revise_possible()

        if self.has_proposal:
            self.proposal.revise(self)
        self.workflow.execute_transition(None, self, 'revision-decided')

    def is_revise_possible(self):
        if not self.is_paragraph:
            return self.get_state() == self.STATE_REVISION
        return False
