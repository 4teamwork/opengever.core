from opengever.base.oguid import Oguid
from opengever.base.response import IResponse
from opengever.base.response import Response
from opengever.meeting import _
from opengever.meeting.model import Meeting
from opengever.ogds.base.actor import Actor
from persistent.dict import PersistentDict
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.converters import json_compatible
from z3c.form.interfaces import IDataManager
from zope import schema
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import implements
from zope.schema import getFields


NEED_SYNCING = (u'revised', u'reopened', u'commented')


class ProposalResponseDescription(object):

    css_classes = {
        u'document_submitted': 'documentAdded',
        u'remove_scheduled': 'scheduleRemoved',
        u'document_updated': 'documentUpdated',
        u'successor_created': 'created'
    }

    def __init__(self, response):
        self.response = response

    def __getattr__(self, name):
        return getattr(self.response, name)

    @property
    def css_class(self):
        return self.css_classes.get(self.response_type, self.response_type)

    @property
    def mapping(self):
        mapping = {'user': self.user}
        if self.response_type in ['document_submitted', 'document_updated']:
            mapping['title'] = self.document_title
            mapping['version'] = self.submitted_version
        elif self.response_type in ['scheduled', 'remove_scheduled']:
            mapping['meeting'] = self.meeting_title
        elif self.response_type == 'successor_created':
            mapping['successor_link'] = self.successor_link
        return mapping

    def message(self):
        messages = {
            'created': _(u'proposal_history_label_created',
                         u'Created by ${user}',
                         self.mapping),

            u'commented': _(u'proposal_history_label_commented',
                            u'Proposal commented by ${user}',
                            self.mapping),

            u'cancelled': _(u'proposal_history_label_cancelled',
                            u'Proposal cancelled by ${user}',
                            self.mapping),

            u'reactivated': _(u'proposal_history_label_reactivated',
                              u'Proposal reactivated by ${user}',
                              self.mapping),

            u'submitted': _(u'proposal_history_label_submitted',
                            u'Submitted by ${user}',
                            self.mapping),

            u'document_submitted': _(
                u'proposal_history_label_document_submitted',
                u'Document ${title} submitted in version ${version} by ${user}',
                self.mapping),

            u'rejected': _(u'proposal_history_label_rejected',
                           u'Rejected by ${user}',
                           self.mapping),

            u'reopened': _(u'proposal_history_label_reopened',
                           u'Proposal reopened by ${user}',
                           self.mapping),

            u'scheduled': _(u'proposal_history_label_scheduled',
                            u'Scheduled for meeting ${meeting} by ${user}',
                            self.mapping),

            u'decided': _(u'proposal_history_label_decided',
                          u'Proposal decided by ${user}',
                          self.mapping),

            u'revised': _(u'proposal_history_label_revised',
                          u'Proposal revised by ${user}',
                          self.mapping),

            u'remove_scheduled': _(
                u'proposal_history_label_remove_scheduled',
                u'Removed from schedule of meeting ${meeting} by ${user}',
                self.mapping),

            u'document_updated': _(
                u'proposal_history_label_document_updated',
                u'Submitted document ${title} updated to version ${version} by ${user}',
                self.mapping),

            u'successor_created': _(
                u'proposal_history_label_successor_created',
                u'Successor proposal ${successor_link} created by ${user}',
                self.mapping),
        }
        return messages[self.response.response_type]

    @property
    def user(self):
        return Actor.lookup(self.response.creator).get_link()

    @property
    def successor_link(self):
        successor = Oguid.parse(self.response.successor_oguid).resolve_object()
        return successor.load_model().get_link(include_icon=False)

    @property
    def meeting_title(self):
        meeting = Meeting.query.get(self.response.meeting_id)
        return meeting.get_title() if meeting else u''


class IProposalResponse(IResponse):
    """Interface and schema for the proposal specific response object,
    containing an additional field"""

    additional_data = schema.Dict(required=False)


class ProposalResponse(Response):

    implements(IProposalResponse)

    def __init__(self, response_type='commented', text=u'', **kwargs):
        super(ProposalResponse, self).__init__(response_type)

        # Because during transport creation time gets rounded down to seconds
        # we round it directly here to avoid potential ordering issues.
        self.created = self.created.replace(microsecond=0)

        # Transitions are executed by default with text=None, which propagates
        # to the Response, explicitely setting the text=None.
        # We therefore set the correct default value here.
        if text is None:
            text = u''

        self.text = text
        self.additional_data = PersistentDict()
        self.additional_data.update(kwargs)

    def __getattr__(self, name):
        if name in self.additional_data:
            return self.additional_data.get(name)
        raise AttributeError

    @property
    def needs_syncing(self):
        # Override of needs_syncing is needed to avoid syncing an already
        # synced response.
        return getattr(self, "_needs_syncing", self.response_type in NEED_SYNCING)

    def serialize(self):
        request = getRequest()
        data = {}
        for name, field in getFields(IProposalResponse).items():
            serializer = queryMultiAdapter(
                (field, self, request), IFieldSerializer)
            value = serializer()
            data[json_compatible(name)] = value
        return data

    def deserialize(self, data):
        fields = getFields(IProposalResponse)
        request = getRequest()
        for name, field in fields.items():
            if name not in data:
                continue
            # Deserialize to field value
            deserializer = queryMultiAdapter(
                (field, self, request), IFieldDeserializer
            )
            value = deserializer(data[name])
            # set value
            dm = queryMultiAdapter((self, field), IDataManager)
            dm.set(value)
