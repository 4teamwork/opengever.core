from collections import OrderedDict
from opengever.base.command import CreateDocumentCommand
from opengever.base.date_time import utcnow_tz_aware
from opengever.base.model import Base
from opengever.base.model import SQLFormSupport
from opengever.base.model import UTCDateTime
from opengever.base.oguid import Oguid
from opengever.base.utils import escape_html
from opengever.globalindex.model import WORKFLOW_STATE_LENGTH
from opengever.meeting import _
from opengever.meeting.browser.meetings.transitions import MeetingTransitionController
from opengever.meeting.exceptions import MissingAdHocTemplate
from opengever.meeting.exceptions import MissingMeetingDossierPermissions
from opengever.meeting.model import AgendaItem
from opengever.meeting.model import Period
from opengever.meeting.model.membership import Membership
from opengever.meeting.workflow import State
from opengever.meeting.workflow import Transition
from opengever.meeting.workflow import Workflow
from opengever.ogds.models import UNIT_ID_LENGTH
from opengever.ogds.models import USER_ID_LENGTH
from opengever.ogds.models.types import UnicodeCoercingText
from opengever.ogds.models.user import User
from plone import api
from plone.i18n.normalizer.interfaces import IFileNameNormalizer
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.orm import backref
from sqlalchemy.orm import composite
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate


meeting_participants = Table(
    'meeting_participants', Base.metadata,
    Column('meeting_id', Integer, ForeignKey('meetings.id')),
    Column('member_id', Integer, ForeignKey('members.id'))
)


class CloseTransition(Transition):
    """Used by pending-closed and held-closed transitions.
    """

    def get_validation_errors(self, model):
        if model.get_undecided_agenda_items():
            return [_(u'label_close_error_has_undecided_agenda_items',
                      u'The meeting cannot be closed because it has undecided'
                      u' agenda items.')]

        return ()

    def execute(self, obj, model):
        assert self.can_execute(model)

        model.close()

        msg = _(u'msg_meeting_successfully_closed',
                default=u'The meeting ${title} has been successfully closed, '
                'the excerpts have been generated and sent back to the '
                'initial dossier.',
                mapping=dict(title=model.get_title()))

        api.portal.show_message(msg, api.portal.get().REQUEST)


class CancelTransition(Transition):

    def get_validation_errors(self, model):
        if model.agenda_items:
            return [_(u"label_meeting_has_agenda_items",
                      u"The meeting already has agenda items and can't "
                      u"be cancelled")]
        return tuple()

    def execute(self, obj, model):
        super(CancelTransition, self).execute(obj, model)

        msg = _(u'msg_meeting_successfully_cancelled',
                default=u'The meeting ${title} has been successfully '
                         'cancelled.',
                mapping=dict(title=model.get_title()))
        api.portal.show_message(msg, api.portal.get().REQUEST)


class Meeting(Base, SQLFormSupport):

    STATE_PENDING = State('pending', is_default=True,
                          title=_('pending', default='Pending'))
    STATE_HELD = State('held', title=_('held', default='Held'))
    STATE_CLOSED = State('closed', title=_('closed', default='Closed'))
    STATE_CANCELLED = State('cancelled',
                            title=_('cancelled', default='Cancelled'))

    workflow = Workflow(
        [STATE_PENDING, STATE_HELD, STATE_CLOSED, STATE_CANCELLED],
        [CloseTransition(
            'pending', 'closed',
            title=_('close_meeting', default='Close meeting')),
         Transition('pending', 'held',
                    title=_('hold', default='Hold meeting'), visible=False),
         CloseTransition(
             'held', 'closed',
             title=_('close_meeting', default='Close meeting')),
         Transition('closed', 'held',
                    title=_('reopen', default='Reopen')),
         CancelTransition('pending', 'cancelled',
                          title=_('cancel', default='Cancel')),
         ],
        show_in_actions_menu=True,
        transition_controller=MeetingTransitionController,
    )

    __tablename__ = 'meetings'

    meeting_id = Column("id", Integer, Sequence("meeting_id_seq"),
                        primary_key=True)
    committee_id = Column(Integer, ForeignKey('committees.id'), nullable=False)
    committee = relationship("Committee", backref='meetings')
    location = Column(String(256))
    title = Column(UnicodeCoercingText)
    start = Column('start_datetime', UTCDateTime(timezone=True), nullable=False)
    end = Column('end_datetime', UTCDateTime(timezone=True))
    workflow_state = Column(String(WORKFLOW_STATE_LENGTH), nullable=False,
                            default=workflow.default_state.name)
    modified = Column(UTCDateTime(timezone=True), nullable=False,
                      default=utcnow_tz_aware)
    meeting_number = Column(Integer)

    presidency = relationship(
        'Member', primaryjoin="Member.member_id==Meeting.presidency_id")
    presidency_id = Column(Integer, ForeignKey('members.id'))
    secretary_id = Column(String(USER_ID_LENGTH), ForeignKey(User.userid))
    secretary = relationship(User, primaryjoin=User.userid == secretary_id)
    other_participants = Column(UnicodeCoercingText)
    participants = relationship('Member',
                                secondary=meeting_participants,
                                order_by='Member.lastname, Member.firstname',
                                backref='meetings')

    dossier_admin_unit_id = Column(String(UNIT_ID_LENGTH), nullable=False)
    dossier_int_id = Column(Integer, nullable=False)
    dossier_oguid = composite(Oguid, dossier_admin_unit_id, dossier_int_id)

    agenda_items = relationship("AgendaItem", order_by='AgendaItem.sort_order',
                                backref='meeting')

    protocol_document_id = Column(Integer, ForeignKey('generateddocuments.id'))
    protocol_document = relationship(
        'GeneratedProtocol', uselist=False,
        backref=backref('meeting', uselist=False),
        primaryjoin="GeneratedProtocol.document_id==Meeting.protocol_document_id")
    protocol_start_page_number = Column(Integer)

    agendaitem_list_document_id = Column(Integer, ForeignKey('generateddocuments.id'))
    agendaitem_list_document = relationship(
        'GeneratedAgendaItemList', uselist=False,
        backref=backref('meeting', uselist=False),
        primaryjoin="GeneratedAgendaItemList.document_id==Meeting.agendaitem_list_document_id")

    def was_protocol_manually_edited(self):
        """checks whether the protocol has been manually edited or not"""
        if not self.has_protocol_document():
            return False
        document = self.protocol_document.resolve_document()
        return not self.protocol_document.is_up_to_date(document)

    def get_other_participants_list(self):
        if self.other_participants is not None:
            return filter(len, map(lambda value: value.strip(),
                                   self.other_participants.split('\n')))
        else:
            return []

    def initialize_participants(self):
        """Set all active members of our committee as participants of
        this meeting.

        """
        self.participants = [membership.member for membership in
                             Membership.query.for_meeting(self)]

    def __repr__(self):
        return '<Meeting at "{}">'.format(self.start)

    def generate_meeting_number(self):
        """Generate meeting number for self.

        This method locks the current period of this meeting to protect its
        meeting_sequence_number against concurrent updates.

        """
        period = Period.query.get_current_for_update(self.committee)

        self.meeting_number = period.get_next_meeting_sequence_number()

    def generate_decision_numbers(self):
        """Generate decision numbers for each agenda item of this meeting.

        This method locks the current period of this meeting to protect its
        decision_sequence_number against concurrent updates.

        """
        period = Period.query.get_current_for_update(self.committee)

        for agenda_item in self.agenda_items:
            agenda_item.generate_decision_number(period)

    def update_protocol_document(self, overwrite=False):
        """Update or create meeting's protocol."""
        from opengever.meeting.command import MergeDocxProtocolCommand
        from opengever.meeting.command import ProtocolOperations

        operations = ProtocolOperations()
        command = MergeDocxProtocolCommand(
            self.get_dossier(), self, operations)
        command.execute(overwrite=overwrite)
        return command

    def hold(self):
        if self.workflow_state == 'held':
            return

        self.generate_meeting_number()
        self.generate_decision_numbers()
        self.workflow_state = 'held'

    def close(self):
        """Closes a meeting means set the meeting in the closed state.

        - generate and set the meeting number
        - generate decision numbers for each agenda_item
        - close each agenda item (generates proposal excerpt and change workflow state)
        - generate or update the protocol if necessary
        """
        self.hold()
        assert not self.get_undecided_agenda_items(), \
            'All agenda items must be decided before a meeting is closed.'

        self.update_protocol_document()
        self.workflow_state = 'closed'

    @property
    def css_class(self):
        return 'contenttype-opengever-meeting-meeting'

    def is_editable(self):
        committee = self.committee.resolve_committee()
        if not api.user.has_permission('Modify portal content', obj=committee):
            return False

        return self.is_active()

    def is_agendalist_editable(self):
        if not self.is_editable():
            return False
        return self.is_pending()

    def is_pending(self):
        return self.get_state() == self.STATE_PENDING

    def is_active(self):
        return self.get_state() in [self.STATE_HELD, self.STATE_PENDING]

    def is_closed(self):
        return self.get_state() == self.STATE_CLOSED

    def has_protocol_document(self):
        return self.protocol_document is not None

    def has_agendaitem_list_document(self):
        return self.agendaitem_list_document is not None

    @property
    def wrapper_id(self):
        return 'meeting-{}'.format(self.meeting_id)

    def _get_title(self, prefix):
        return u"{}-{}".format(
            translate(prefix, context=getRequest()), self.get_title())

    def _get_filename(self, prefix):
        normalizer = getUtility(IFileNameNormalizer, name='gever_filename_normalizer')
        return u"{}-{}.docx".format(
            translate(prefix, context=getRequest()),
            normalizer.normalize(self.get_title()))

    def get_protocol_title(self):
        return self._get_title(_("Protocol"))

    def get_excerpt_title(self):
        return self._get_title(_("Protocol Excerpt"))

    def get_agendaitem_list_title(self):
        return self._get_title(
            _(u'label_agendaitem_list', default=u'Agendaitem list'))

    def get_protocol_filename(self):
        return self._get_filename(_("Protocol"))

    def get_excerpt_filename(self):
        return self._get_filename(_("Protocol Excerpt"))

    def get_agendaitem_list_filename(self):
        return self._get_filename(
            _(u'label_agendaitem_list', default=u'Agendaitem list'))

    def get_protocol_header_template(self):
        return self.committee.get_protocol_header_template()

    def get_protocol_suffix_template(self):
        return self.committee.get_protocol_suffix_template()

    def get_agenda_item_header_template(self):
        return self.committee.get_agenda_item_header_template()

    def get_agenda_item_suffix_template(self):
        return self.committee.get_agenda_item_suffix_template()

    def get_agendaitem_list_template(self):
        return self.committee.get_agendaitem_list_template()

    @property
    def physical_path(self):
        return '/'.join((self.committee.physical_path, self.wrapper_id))

    def execute_transition(self, name):
        self.workflow.execute_transition(self, self, name)

    def can_execute_transition(self, name):
        return self.workflow.can_execute_transition(self, name)

    def get_state(self):
        return self.workflow.get_state(self.workflow_state)

    def update_model(self, data):
        """Manually set the modified timestamp when updating meetings."""

        super(Meeting, self).update_model(data)
        self.modified = utcnow_tz_aware()

        meeting_dossier = self.get_dossier()
        title = data.get('title')
        if meeting_dossier and title:
            meeting_dossier.title = title
            meeting_dossier.reindexObject()

    def get_title(self):
        return self.title

    def get_date(self):
        return api.portal.get_localized_time(datetime=self.start)

    def get_start(self):
        """Returns the start datetime in localized format.
        """
        return api.portal.get_localized_time(
            datetime=self.start, long_format=True)

    def get_end(self):
        """Returns the end datetime in localized format.
        """
        if self.end:
            return api.portal.get_localized_time(
                datetime=self.end, long_format=True)

        return None

    def get_start_time(self):
        return self._get_localized_time(self.start)

    def get_end_time(self):
        if not self.end:
            return None

        return self._get_localized_time(self.end)

    def get_undecided_agenda_items(self):
        """Return a filtered list of this meetings agenda items,
        containing only the items which are not in a "decided" workflow state.
        """
        def is_not_paragraph(agenda_item):
            return not agenda_item.is_paragraph

        def is_not_decided(agenda_item):
            return not agenda_item.is_completed()

        return filter(is_not_decided, filter(is_not_paragraph, self.agenda_items))

    def _get_localized_time(self, date):
        if not date:
            return None

        return api.portal.get_localized_time(datetime=date, time_only=True)

    def schedule_proposal(self, proposal):
        assert proposal.committee == self.committee

        proposal.schedule(self)
        self.reorder_agenda_items()

    def schedule_text(self, title, is_paragraph=False):
        self.agenda_items.append(AgendaItem(title=title,
                                            is_paragraph=is_paragraph))
        self.reorder_agenda_items()

    def schedule_ad_hoc(self, title, template_id=None, description=None):
        committee = self.committee.resolve_committee()

        if template_id is None:
            ad_hoc_template = committee.get_ad_hoc_template()
        else:
            from opengever.meeting.vocabulary import ProposalTemplatesForCommitteeVocabulary
            vocabulary_factory = ProposalTemplatesForCommitteeVocabulary()
            vocabulary = vocabulary_factory(committee)
            templates = [term.value
                         for term in vocabulary
                         if term.value.getId() == template_id]
            assert 1 == len(templates)
            ad_hoc_template = templates[0]

        if not ad_hoc_template:
            raise MissingAdHocTemplate

        meeting_dossier = self.get_dossier()
        if not api.user.get_current().checkPermission(
            'opengever.document: Add document', meeting_dossier):
            raise MissingMeetingDossierPermissions

        ad_hoc_document = CreateDocumentCommand(
            context=meeting_dossier,
            filename=ad_hoc_template.file.filename,
            data=ad_hoc_template.file.data,
            content_type=ad_hoc_template.file.contentType,
            title=title).execute()
        agenda_item = AgendaItem(
            title=title, description=description,
            document=ad_hoc_document, is_paragraph=False)

        self.agenda_items.append(agenda_item)
        self.reorder_agenda_items()
        return agenda_item

    def _set_agenda_item_order(self, new_order):
        agenda_items_by_id = OrderedDict((item.agenda_item_id, item)
                                         for item in self.agenda_items)
        agenda_items = []

        for agenda_item_id in new_order:
            agenda_item = agenda_items_by_id.pop(agenda_item_id, None)
            if agenda_item:
                agenda_items.append(agenda_item)
        agenda_items.extend(agenda_items_by_id.values())
        self.agenda_items = agenda_items

    def reorder_agenda_items(self, new_order=None):
        if new_order:
            self._set_agenda_item_order(new_order)

        sort_order = 1
        number = 1
        for agenda_item in self.agenda_items:
            agenda_item.sort_order = sort_order
            sort_order += 1
            if not agenda_item.is_paragraph:
                agenda_item.number = '{}.'.format(number)
                number += 1

    def get_submitted_link(self):
        return self._get_link(self.get_submitted_admin_unit(),
                              self.submitted_physical_path)

    def get_link(self):
        url = self.get_url()
        if api.user.has_permission('View',
                                   obj=self.committee.resolve_committee()):
            link = u'<a href="{0}" title="{1}" class="{2}">{1}</a>'.format(
                url, escape_html(self.get_title()), self.css_class)
        else:
            link = u'<span title="{0}" class="{1}">{0}</a>'.format(
                escape_html(self.get_title()), self.css_class)
        return link

    def get_url(self, context=None, view='view'):
        elements = [self.committee.get_admin_unit().public_url, self.physical_path]
        if view:
            elements.append(view)

        return '/'.join(elements)

    def get_dossier_url(self):
        return self.dossier_oguid.get_url()

    def get_dossier(self):
        return self.dossier_oguid.resolve_object()
