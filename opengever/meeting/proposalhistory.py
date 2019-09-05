from BTrees.OOBTree import OOBTree
from datetime import datetime
from opengever.base import advancedjson
from opengever.base.date_time import utcnow_tz_aware
from opengever.base.oguid import Oguid
from opengever.base.protect import unprotected_write
from opengever.base.request import dispatch_request
from opengever.meeting import _
from opengever.meeting.activity.activities import ProposalCommentedActivitiy
from opengever.meeting.activity.activities import ProposalDecideActivity
from opengever.meeting.model import Meeting
from opengever.ogds.base.actor import Actor
from persistent.mapping import PersistentMapping
from plone import api
from uuid import UUID
from uuid import uuid4
from zope.annotation.interfaces import IAnnotations


class ProposalHistory(object):
    """Adapter to keep track of a proposals history. Factory for new entries.

    Lists history records for an object and creates new ones. Records are stored
    in the objects annotations. Keeps a registry of supported history entries.

    History records are stored in the objects annotations with their timestamp
    as key and their data as value.
    """
    record_classes = {}
    annotation_key = 'object_history'

    @classmethod
    def register(cls, clazz):
        assert clazz.history_type not in cls.record_classes
        cls.record_classes[clazz.history_type] = clazz
        return clazz

    def __init__(self, context):
        self.context = context

    def __iter__(self):
        history = self._get_history_for_reading()

        for key, val in reversed(history.items()):
            history_type = val.get('history_type')
            if not history_type:
                continue
            clazz = self.record_classes.get(history_type)
            if not clazz:
                continue

            yield clazz.re_populate(self.context, key, val)

    def append_record(self, history_type, timestamp=None, **kwargs):
        if timestamp and not isinstance(timestamp, datetime):
            raise TypeError("Invalid type for timestamp: {}".format(
                timestamp.__class__))
        if history_type not in self.record_classes:
            raise ValueError('No record class registered for {}'.format(
                history_type))

        clazz = self.record_classes[history_type]

        history = self._get_history_for_writing()
        record = clazz(self.context, timestamp=timestamp, **kwargs)
        record.append_to(history)

        if record.needs_syncing and self.context.is_submitted():
            path = self.context.get_sync_target_path()
            admin_unit_id = self.context.get_sync_admin_unit_id()

            request_data = {'data': advancedjson.dumps({
                'timestamp': record.timestamp,
                'data': record.data,
            })}
            dispatch_request(
                admin_unit_id,
                '@@receive-proposal-history',
                path=path,
                data=request_data,)
        return record

    def receive_record(self, timestamp, data):
        if not isinstance(timestamp, datetime):
            raise TypeError("Invalid type for timestamp: {}".format(
                timestamp.__class__))
        if not isinstance(data, PersistentMapping):
            raise TypeError("Invalid type for data: {}".format(
                data.__class__))

        history = self._get_history_for_writing()
        history[timestamp] = data

        self.record_classes[data.get('history_type')].receive(
            self.context, self.context.REQUEST, data)

    def _get_history_for_writing(self):
        """Return the history for writing and make sure a default is also
        initialized if it is the first time the history is accessed.
        """
        return unprotected_write(IAnnotations(self.context).setdefault(
            self.annotation_key, OOBTree()))

    def _get_history_for_reading(self):
        """"Return the history for reading and make sure to not cause a write
        on display by initialization. Instead just return a default value.
        """
        return IAnnotations(self.context).get(self.annotation_key, OOBTree())


class BaseHistoryRecord(object):
    """Basic implementation of a history record.

    Contains basic set of required data and abstract implementation. Can
    re-populate iself from data by invoking the __new__ method directly and
    then re-populating the attributes on the instance instead of calling
    __init__.

    Each record must have a unique `history_type` from which it can be built
    with IHistory.append_record.

    If `needs_syncing` is `True` a records is created on one side is
    automatically added to its corresponding `Proposal` or `SubmittedProposal`.
    """

    history_type = None
    needs_syncing = False

    @classmethod
    def re_populate(cls, context, timestamp, data):
        record = cls.__new__(cls)
        record.context = context
        record.timestamp = timestamp
        record.data = data
        return record

    def __init__(self, context, timestamp=None, uuid=None, text=None):
        timestamp = timestamp or utcnow_tz_aware()
        if uuid is None:
            uuid = uuid4()
        elif isinstance(uuid, basestring):
            uuid = UUID(uuid)

        self.context = context
        self.timestamp = timestamp
        self.data = PersistentMapping(
            created=timestamp,
            userid=unicode(api.user.get_current().getId()),
            history_type=self.history_type,
            uuid=uuid,
            text=text)

    def append_to(self, history):
        if self.timestamp in history:
            raise ValueError('Timestamp {} already in use'.format(
                self.timestamp))

        history[self.timestamp] = self.data

    def message(self):
        raise NotImplementedError

    @property
    def css_class(self):
        return self.history_type

    @property
    def created(self):
        return self.data['created']

    @property
    def text(self):
        return self.data.get('text')

    @property
    def uuid(self):
        return self.data.get('uuid')

    def get_actor_link(self):
        return Actor.lookup(self.data['userid']).get_link()

    @classmethod
    def receive(cls, context, request, data):
        pass


@ProposalHistory.register
class ProposalCreated(BaseHistoryRecord):
    """A Proposal has been created."""

    history_type = u'created'

    def message(self):
        return _(u'proposal_history_label_created',
                 u'Created by ${user}',
                 mapping={'user': self.get_actor_link()})


@ProposalHistory.register
class ProposalCommented(BaseHistoryRecord):

    history_type = u'commented'
    needs_syncing = True

    def message(self):
        return _(u'proposal_history_label_commented',
                 u'Proposal commented by ${user}',
                 mapping={'user': self.get_actor_link()})

    @classmethod
    def receive(cls, context, request, data):
        ProposalCommentedActivitiy(context, request).record()


@ProposalHistory.register
class ProposalCancelled(BaseHistoryRecord):

    history_type = u'cancelled'

    def message(self):
        return _(u'proposal_history_label_cancelled',
                 u'Proposal cancelled by ${user}',
                 mapping={'user': self.get_actor_link()})


@ProposalHistory.register
class ProposalReactivated(BaseHistoryRecord):

    history_type = u'reactivated'

    def message(self):
        return _(u'proposal_history_label_reactivated',
                 u'Proposal reactivated by ${user}',
                 mapping={'user': self.get_actor_link()})


@ProposalHistory.register
class ProposalSubmitted(BaseHistoryRecord):

    history_type = u'submitted'

    def message(self):
        return _(u'proposal_history_label_submitted',
                 u'Submitted by ${user}',
                 mapping={'user': self.get_actor_link()})


@ProposalHistory.register
class DocumentSubmitted(BaseHistoryRecord):

    history_type = u'document_submitted'
    css_class = 'documentAdded'

    def __init__(self, context, document_title, submitted_version,
                 timestamp=None, uuid=None):
        super(DocumentSubmitted, self).__init__(
            context, timestamp=timestamp, uuid=uuid)
        self.data['document_title'] = document_title
        self.data['submitted_version'] = submitted_version

    @property
    def document_title(self):
        return self.data.get('document_title')

    @property
    def submitted_version(self):
        return self.data.get('submitted_version')

    def message(self):
        return _(u'proposal_history_label_document_submitted',
                 u'Document ${title} submitted in version ${version} by ${user}',
                 mapping={'user': self.get_actor_link(),
                          'title': self.document_title or '',
                          'version': self.submitted_version})


@ProposalHistory.register
class ProposalRejected(BaseHistoryRecord):

    history_type = u'rejected'

    def __init__(self, context, text, timestamp=None, uuid=None):
        super(ProposalRejected, self).__init__(
            context, timestamp=timestamp, uuid=uuid)
        self.data['text'] = text

    def message(self):
        return _(u'proposal_history_label_rejected',
                 u'Rejected by ${user}',
                 mapping={'user': self.get_actor_link()})


@ProposalHistory.register
class ProposalReopened(BaseHistoryRecord):

    history_type = u'reopened'
    needs_syncing = True

    def message(self):
        return _(u'proposal_history_label_reopened',
                 u'Proposal reopened by ${user}',
                 mapping={'user': self.get_actor_link()})


@ProposalHistory.register
class ProposalScheduled(BaseHistoryRecord):

    history_type = u'scheduled'

    def __init__(self, context, meeting_id, timestamp=None, uuid=None):
        super(ProposalScheduled, self).__init__(
            context, timestamp=timestamp, uuid=uuid)
        self.data['meeting_id'] = meeting_id

    @property
    def meeting_title(self):
        meeting_id = self.data.get('meeting_id')
        meeting = Meeting.query.get(meeting_id)
        meeting_title = meeting.get_title() if meeting else u''
        return meeting_title

    def message(self):
        return _(u'proposal_history_label_scheduled',
                 u'Scheduled for meeting ${meeting} by ${user}',
                 mapping={'user': self.get_actor_link(),
                          'meeting': self.meeting_title})


@ProposalHistory.register
class ProposalDecided(BaseHistoryRecord):

    history_type = u'decided'
    needs_syncing = True

    def message(self):
        return _(u'proposal_history_label_decided',
                 u'Proposal decided by ${user}',
                 mapping={'user': self.get_actor_link()})

    @classmethod
    def receive(cls, context, request, data):
        ProposalDecideActivity(context, request).record()


@ProposalHistory.register
class ProposalRevised(BaseHistoryRecord):

    history_type = u'revised'
    needs_syncing = True

    def message(self):
        return _(u'proposal_history_label_revised',
                 u'Proposal revised by ${user}',
                 mapping={'user': self.get_actor_link()})


@ProposalHistory.register
class ProposalRemovedFromSchedule(ProposalScheduled):

    history_type = u'remove_scheduled'
    css_class = 'scheduleRemoved'

    def message(self):
        return _(u'proposal_history_label_remove_scheduled',
                 u'Removed from schedule of meeting ${meeting} by ${user}',
                 mapping={'user': self.get_actor_link(),
                          'meeting': self.meeting_title})


@ProposalHistory.register
class DocumentUpdated(DocumentSubmitted):

    history_type = u'document_updated'
    css_class = 'documentUpdated'

    def message(self):
        return _(u'proposal_history_label_document_updated',
                 u'Submitted document ${title} updated to version ${version} by ${user}',
                 mapping={'user': self.get_actor_link(),
                          'title': self.document_title or '',
                          'version': self.submitted_version})


@ProposalHistory.register
class SuccessorCreated(BaseHistoryRecord):
    """A successor was created.

    This history entry is created on a predecessor when a successor is created.
    """

    history_type = u'successor_created'
    css_class = 'created'

    def __init__(self, context, successor_oguid, timestamp=None, uuid=None):
        super(SuccessorCreated, self).__init__(
            context, timestamp=timestamp, uuid=uuid)
        self.data['successor_oguid'] = successor_oguid

    def message(self):
        return _(u'proposal_history_label_successor_created',
                 u'Successor proposal ${successor_link} created by ${user}',
                 mapping={'successor_link': self.get_successor_link(),
                          'user': self.get_actor_link()})

    def get_successor(self):
        return Oguid.parse(self.data['successor_oguid']).resolve_object()

    def get_successor_link(self):
        return self.get_successor().load_model().get_link(include_icon=False)
