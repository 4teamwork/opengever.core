from BTrees.LOBTree import LOBTree
from contextlib import contextmanager
from datetime import datetime
from persistent import Persistent
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from plone import api
from plone.dexterity.utils import iterSchemata
from plone.restapi.interfaces import IFieldSerializer
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.annotation import IAnnotations
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent
from zope.event import notify
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface
from zope.schema import getFields
import time


class IResponseAddedEvent(IObjectEvent):
    """A response has been added to an object"""


class ResponseAddedEvent(ObjectEvent):

    implements(IResponseAddedEvent)

    def __init__(self, context, response_container, response):
        super(ResponseAddedEvent, self).__init__(context)
        self.response_container = response_container
        self.response = response


class IResponseSupported(Interface):
    """Marker interface for response support.
    """


class IResponseContainer(Interface):
    """Response storage adapter.
    """

    def add(self, response):
        """Add the given response to the container list."""

    def list(self):
        """Returns a list of all responses."""

    def items(self):
        """Returns a list of (id, response object) pairs of all responses."""


@implementer(IResponseContainer)
@adapter(IResponseSupported)
class ResponseContainer(object):
    """Response storage adapter.
    """

    ANNOTATION_KEY = 'opengever.base.responses'

    def __init__(self, context):
        self.context = context

    def __len__(self):
        return len(self.list())

    def add(self, response):
        storage = self._storage(create_if_missing=True)
        if not IResponse.providedBy(response):
            raise ValueError('Only Response objects are allowed to add')

        response_id = long(time.time() * 1e6)
        while response_id in storage:
            response_id += 1

        response.response_id = response_id
        storage[response_id] = response
        notify(ResponseAddedEvent(self.context, self, response))
        return response_id

    def _storage(self, create_if_missing=False):
        ann = IAnnotations(self.context)
        if self.ANNOTATION_KEY not in ann.keys() and create_if_missing:
            ann[self.ANNOTATION_KEY] = LOBTree()

        return ann.get(self.ANNOTATION_KEY, None)

    def list(self):
        storage = self._storage()
        if not storage:
            return []

        return list(storage.values())

    def items(self):
        storage = self._storage()
        if not storage:
            return []

        return list(storage.items())

    def __contains__(self, key):
        storage = self._storage()
        if not storage:
            return False

        if IResponse.providedBy(key):
            key = key.response_id
        return long(key) in self._storage()

    def __getitem__(self, key):
        """Get an item by its key
        """
        storage = self._storage()
        if not storage:
            raise IndexError

        return storage[long(key)]

    def __iter__(self):
        storage = self._storage()
        if not storage:
            return

        for key, response in storage.items():
            yield response


class IResponse(Interface):
    """Interface and schema for the response object, an object added to
    plone content objects."""

    response_type = schema.TextLine(required=True)

    response_id = schema.Int(required=True)

    created = schema.Date(required=True)

    creator = schema.TextLine(required=True)

    text = schema.Text(required=False)

    changes = schema.List(required=False, value_type=schema.Dict())

    # Relations to added objects
    added_object = RelationList(required=False)

    # OGUID releation to a successor
    successor_oguid = schema.TextLine(required=False)

    # Rendered text (html) for caching
    rendered_text = schema.Text(required=False)

    # ID of perfomed transition
    transition = schema.TextLine(required=False)

    # Mime type of the response.
    mimetype = schema.TextLine(required=False)

    relatedItems = RelationList(required=False)


class Response(Persistent):
    """A persistent lightweight object which represents a single response.
    Addable to the response container of plone objects, for example to
    workspace todo's.
    """

    implements(IResponse)

    def __init__(self, response_type='default'):
        self.response_id = None
        self.response_type = response_type

        self.created = datetime.now()
        self.creator = api.user.get_current().id

        self.text = ''
        self.successor_oguid = ''
        self.rendered_text = ''
        self.transition = ''
        self.mimetype = ''
        self.changes = PersistentList()
        self.added_object = PersistentList()
        self.relatedItems = PersistentList()

    def add_change(self, field_id, before, after, field_title=''):
        self.changes.append(PersistentDict(
            field_id=field_id,
            field_title=field_title,  # Deprecated, only for the old gever-ui
            before=before,
            after=after
        ))


COMMENT_RESPONSE_TYPE = 'comment'
SCHEMA_FIELD_CHANGE_RESPONSE_TYPE = 'schema_field'
MOVE_RESPONSE_TYPE = 'move'


class AutoResponseChangesTracker(object):
    """Contextmanager to track changes made on an object and autogenerating
    a response-object with the changes.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.state_before = {}
        self.changes = {}
        self.tracking_field_names = []

    @contextmanager
    def track_changes(self, tracking_field_names):
        self._start_tracking(tracking_field_names)
        yield self
        self._end_tracking()

    def _start_tracking(self, tracking_field_names):
        self.tracking_field_names = tracking_field_names
        self.state_before = {}
        self.changes = {}

        for name, value in self._field_items():
            self.state_before[name] = value

    def _end_tracking(self):
        for name, value in self._field_items():
            value_before = self.state_before.get(name)
            value_after = value
            if value_after == value_before:
                continue

            self.changes[name] = (value_before, value_after)
        self._generate_response_object()

    def _generate_response_object(self):
        if not self.changes:
            return None

        response = Response(SCHEMA_FIELD_CHANGE_RESPONSE_TYPE)
        for key, value in self.changes.items():
            response.add_change(key, *value)

        IResponseContainer(self.context).add(response)
        return response

    def _field_items(self):
        for context_schema in iterSchemata(self.context):
            for name, field in getFields(context_schema).items():
                if name not in self.tracking_field_names:
                    continue

                serializer = queryMultiAdapter(
                    (field, self.context, self.request), IFieldSerializer)

                yield name, serializer()
