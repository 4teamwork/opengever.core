from datetime import datetime
from opengever.base import _
from persistent import Persistent
from persistent.list import PersistentList
from plone import api
from zope import schema
from zope.annotation import IAnnotations
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface


class IResponseSupported(Interface):
    """Marker interface for response support.
    """


class IResponseContainer(Interface):
    """Response storage adapter.
    """

    def add(self, response):
        """Add the given response to the container list."""

    def list(self):
        """Returns a list of all response."""


@implementer(IResponseContainer)
@adapter(IResponseSupported)
class ResponseContainer(object):
    """Response storage adapter.
    """

    ANNOTATION_KEY = 'opengever.base.responses'

    def __init__(self, context):
        self.context = context

    def add(self, response):
        self.storage(create_if_missing=True).append(response)

    def storage(self, create_if_missing=False):
        ann = IAnnotations(self.context)
        if self.ANNOTATION_KEY not in ann.keys() and create_if_missing:
            ann[self.ANNOTATION_KEY] = PersistentList()

        return ann.get(self.ANNOTATION_KEY, None)

    def list(self):
        storage = self.storage()
        if not storage:
            return []

        return storage


class IResponse(Interface):
    """Interface and schema for the response object, an object added to
    plone content objects."""

    created = schema.Date(
        title=_(u'label_created', default=u'Created'),
        required=True
    )

    creator = schema.TextLine(
        title=_(u'label_creator', default=u'Creator'),
        required=True
    )

    text = schema.Text(
        title=_(u'label_text', default=u'Text'),
        required=True
    )


class Response(Persistent):
    """A persistent lightweight object which represents a single response.
    Addable to the response container of pone objects, for example to
    workspace todo's.
    """

    implements(IResponse)

    def __init__(self, text):
        self.text = text
        self.created = datetime.now()
        self.creator = api.user.get_current().id
