from AccessControl import getSecurityManager
from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.zipexport.utils import normalize_path
from opengever.base.model import Base
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.base.transforms import trix2sablon
from opengever.base.widgets import trix_strip_whitespace
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.globalindex.model import WORKFLOW_STATE_LENGTH
from opengever.meeting import _
from opengever.meeting import is_word_meeting_implementation_enabled
from opengever.meeting import require_word_meeting_feature
from opengever.meeting.exceptions import MissingMeetingDossierPermissions
from opengever.meeting.exceptions import WrongAgendaItemState
from opengever.meeting.model import Period
from opengever.meeting.model.excerpt import Excerpt
from opengever.meeting.workflow import State
from opengever.meeting.workflow import Transition
from opengever.meeting.workflow import Workflow
from opengever.ogds.models import UNIT_ID_LENGTH
from opengever.ogds.models.types import UnicodeCoercingText
from opengever.trash.trash import ITrashable
from plone import api
from Products.CMFPlone.utils import safe_unicode
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import backref
from sqlalchemy.orm import composite
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence
from tzlocal import get_localzone
from zope.component import getMultiAdapter
import os


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

        document = kwargs.pop('document', None)
        if document:
            assert not proposal, 'must only have one of proposal and document'
            kwargs.update(
                {'ad_hoc_document_oguid': Oguid.for_object(document)})

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
            self.submitted_proposal.sync_model()
        else:
            self.title = title

    def get_decision_draft(self):
        if self.has_proposal:
            return self.submitted_proposal.decision_draft

    def get_decision_number(self):
        if not is_word_meeting_implementation_enabled():
            return self.decision_number

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

    def get_document_filename_for_zip(self, document):
        return normalize_path(u'{} {}/{}{}'.format(
            self.number,
            safe_unicode(self.get_title()),
            safe_unicode(document.Title()),
            os.path.splitext(document.file.filename)[1]))

    def get_proposal_link(self, include_icon=True):
        if not self.has_proposal:
            return self.get_title()

        return self.proposal.get_submitted_link(include_icon=include_icon)

    @require_word_meeting_feature
    def get_data_for_zip_export(self):
        agenda_item_data = {
            'title': safe_unicode(self.get_title()),
        }

        if self.has_document:
            document = self.resolve_document()
            agenda_item_data.update({
                'number': self.number,
                'proposal': {
                    'checksum': (IBumblebeeDocument(document)
                                 .get_checksum()),
                    'file': self.get_document_filename_for_zip(document),
                    'modified': safe_unicode(
                        get_localzone().localize(
                            document.modified().asdatetime()
                            .replace(tzinfo=None)
                        ).isoformat()),
                }
            })

        if self.has_submitted_documents():
            agenda_item_data.update({
                'attachments': [{
                    'checksum': (IBumblebeeDocument(document)
                                 .get_checksum()),
                    'file': self.get_document_filename_for_zip(document),
                    'modified': safe_unicode(
                        get_localzone().localize(
                            document.modified().asdatetime()
                            .replace(tzinfo=None)
                        ).isoformat()),
                    'title': safe_unicode(document.Title()),
                }
                for document in self.proposal.resolve_submitted_documents()],
            })

        return agenda_item_data

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
    def has_document(self):
        return self.has_proposal or self.ad_hoc_document_int_id is not None

    def resolve_document(self):
        if not self.has_document:
            return None

        if self.has_proposal:
            proposal = self.proposal.resolve_submitted_proposal()
            return proposal.get_proposal_document()

        return self.ad_hoc_document_oguid.resolve_object()

    @require_word_meeting_feature
    def checkin_document(self):
        document = self.resolve_document()
        if not document:
            return

        checkout_manager = getMultiAdapter((document, document.REQUEST),
                                           ICheckinCheckoutManager)
        checkout_manager.checkin()

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
        if not self.is_revise_possible():
            raise WrongAgendaItemState()

        if self.has_proposal:
            self.proposal.revise(self)
        self.workflow.execute_transition(None, self, 'revision-decided')

    def is_revise_possible(self):
        if not self.is_paragraph:
            return self.get_state() == self.STATE_REVISION
        return False

    def return_excerpt(self, document):
        self.proposal.return_excerpt(document)

    @require_word_meeting_feature
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
            filename=source_document.file.filename,
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

    @require_word_meeting_feature
    def get_excerpt_documents(self, unrestricted=False):
        """Return a list of excerpt documents.

        If the agenda items has a proposal return the proposals excerpt
        documents. Otherwise return the excerpts stored in the meeting
        dossier.
        """
        if self.has_proposal:
            return self.submitted_proposal.get_excerpts(unrestricted=unrestricted)

        checkPermission = getSecurityManager().checkPermission
        documents = [excerpt.resolve_document() for excerpt in self.excerpts]
        documents = filter(None, documents)
        if not unrestricted:
            documents = filter(lambda obj: checkPermission('View', obj), documents)

        return documents

    @require_word_meeting_feature
    def get_source_dossier_excerpt(self):
        if not self.has_proposal:
            return None

        return self.proposal.resolve_submitted_excerpt_document()
