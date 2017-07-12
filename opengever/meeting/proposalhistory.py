from BTrees.OOBTree import OOBTree
from datetime import datetime
from opengever.base.date_time import utcnow_tz_aware
from opengever.base.jsonencoder import AdvancedJSONEncoder
from opengever.base.protect import unprotected_write
from opengever.base.request import dispatch_request
from opengever.meeting import _
from opengever.meeting.model import Meeting
from opengever.ogds.base.actor import Actor
from persistent.mapping import PersistentMapping
from plone import api
from uuid import UUID
from uuid import uuid4
from zope.annotation.interfaces import IAnnotations
import json


class ProposalHistory(object):
    """Adapter to keep track of a proposals history. Factory for new entries.

    Lists history records for an object and crates new ones. Records are stored
    in the objects annotations. Keeps a registry of supported history entries.

    History records are stored in the objects annotations with their timestamp
    as key and their data as value.
    """
    record_classes = {}
    annotation_key = 'object_history'

    @classmethod
    def register(cls, clazz):
        assert clazz.name not in cls.record_classes
        cls.record_classes[clazz.name] = clazz

    def __init__(self, context):
        self.context = context

    def __iter__(self):
        history = self._get_history_for_reading()

        for key, val in reversed(history.items()):
            name = val.get('name')
            if not name:
                continue
            clazz = self.record_classes.get(name)
            if not clazz:
                continue

            yield clazz.re_populate(self.context, key, val)

    def append_record(self, name, timestamp=None, **kwargs):
        if timestamp and not isinstance(timestamp, datetime):
            raise TypeError("Invalid type for timestamp: {}".format(
                timestamp.__class__))
        if name not in self.record_classes:
            raise ValueError('No record class registered for {}'.format(name))

        clazz = self.record_classes[name]

        history = self._get_history_for_writing()
        record = clazz(self.context, timestamp=timestamp, **kwargs)
        record.append_to(history)

        if record.needs_syncing:
            # currently we only sync from the submitted side
            # to the dossier
            path = self.context.load_model().physical_path
            request_data = {'data': json.dumps({
                'timestamp': record.timestamp,
                'data': record.data,
            }, cls=AdvancedJSONEncoder)}
            dispatch_request(
                self.context.get_source_admin_unit_id(),
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

    Each record must have a unique `name` from which it can be built via
    IHistory.append_record.

    If `needs_syncing` is `True` a records that is created on the
    `SubmittedProposal` side is automatically added to its corresponding
    `Proposal`.
    """

    name = None
    needs_syncing = False

    @classmethod
    def re_populate(cls, context, timestamp, data):
        record = cls.__new__(cls)
        record.context = context
        record.timestamp = timestamp
        record.data = data
        return record

    def __init__(self, context, timestamp=None, uuid=None):
        timestamp = timestamp or utcnow_tz_aware()
        if uuid is None:
            uuid = uuid4()
        elif isinstance(uuid, basestring):
            uuid = UUID(uuid)

        self.context = context
        self.timestamp = timestamp
        self.data = PersistentMapping(
            created=timestamp,
            userid=api.user.get_current().getId(),
            name=self.name,
            uuid=uuid)

    def append_to(self, history):
        if self.timestamp in history:
            return  # XXX raise?

        history[self.timestamp] = self.data

    def message(self):
        raise NotImplementedError

    @property
    def css_class(self):
        return self.name

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


class ProposalCreated(BaseHistoryRecord):
    """A Proposal has been created."""

    name = 'created'

    def message(self):
        return _(u'proposal_history_label_created',
                 u'Created by ${user}',
                 mapping={'user': self.get_actor_link()})

ProposalHistory.register(ProposalCreated)


class ProposalCancelled(BaseHistoryRecord):

    name = 'cancelled'

    def message(self):
        return _(u'proposal_history_label_cancelled',
                 u'Proposal cancelled by ${user}',
                 mapping={'user': self.get_actor_link()})

ProposalHistory.register(ProposalCancelled)


class ProposalReactivated(BaseHistoryRecord):

    name = 'reactivated'

    def message(self):
        return _(u'proposal_history_label_reactivated',
                 u'Proposal reactivated by ${user}',
                 mapping={'user': self.get_actor_link()})

ProposalHistory.register(ProposalReactivated)


class ProposalSubmitted(BaseHistoryRecord):

    name = 'submitted'

    def message(self):
        return _(u'proposal_history_label_submitted',
                 u'Submitted by ${user}',
                 mapping={'user': self.get_actor_link()})

ProposalHistory.register(ProposalSubmitted)


class DocumentSubmitted(BaseHistoryRecord):

    name = 'document_submitted'
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

ProposalHistory.register(DocumentSubmitted)


class ProposalRejected(BaseHistoryRecord):

    name = 'rejected'

    def __init__(self, context, text, timestamp=None, uuid=None):
        super(ProposalRejected, self).__init__(
            context, timestamp=timestamp, uuid=uuid)
        self.data['text'] = text

    def message(self):
        return _(u'proposal_history_label_rejected',
                 u'Rejected by ${user}',
                 mapping={'user': self.get_actor_link()})

ProposalHistory.register(ProposalRejected)


class ProposalReopened(BaseHistoryRecord):

    name = 'reopened'
    needs_syncing = True

    def message(self):
        return _(u'proposal_history_label_reopened',
                 u'Proposal reopened by ${user}',
                 mapping={'user': self.get_actor_link()})

ProposalHistory.register(ProposalReopened)


class ProposalScheduled(BaseHistoryRecord):

    name = 'scheduled'
    needs_syncing = True

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

ProposalHistory.register(ProposalScheduled)


class ProposalDecided(BaseHistoryRecord):

    name = 'decided'
    needs_syncing = True

    def message(self):
        return _(u'proposal_history_label_decided',
                 u'Proposal decided by ${user}',
                 mapping={'user': self.get_actor_link()})

ProposalHistory.register(ProposalDecided)


class ProposalRevised(BaseHistoryRecord):

    name = 'revised'
    needs_syncing = True

    def message(self):
        return _(u'proposal_history_label_revised',
                 u'Proposal revised by ${user}',
                 mapping={'user': self.get_actor_link()})

ProposalHistory.register(ProposalRevised)


class ProposalRemovedFromSchedule(ProposalScheduled):

    name = 'remove_scheduled'
    css_class = 'scheduleRemoved'
    needs_syncing = True

    def message(self):
        return _(u'proposal_history_label_remove_scheduled',
                 u'Removed from schedule of meeting ${meeting} by ${user}',
                 mapping={'user': self.get_actor_link(),
                          'meeting': self.meeting_title})

ProposalHistory.register(ProposalRemovedFromSchedule)


class DocumentUpdated(DocumentSubmitted):

    name = 'document_updated'
    css_class = 'documentUpdated'

    def message(self):
        return _(u'proposal_history_label_document_updated',
                 u'Submitted document ${title} updated to version ${version} by ${user}',
                 mapping={'user': self.get_actor_link(),
                          'title': self.document_title or '',
                          'version': self.submitted_version})

ProposalHistory.register(DocumentUpdated)
