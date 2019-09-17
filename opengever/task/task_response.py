from opengever.base.response import IResponse
from opengever.base.response import Response
from persistent.list import PersistentList
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.interface import implements


class ITaskResponse(IResponse):

    # Relations to added objects
    added_objects = RelationList(required=False)

    # OGUID releation to a successor
    successor_oguid = schema.TextLine(required=False)

    # Rendered text (html) for caching
    rendered_text = schema.Text(required=False)

    # ID of perfomed transition
    transition = schema.TextLine(required=False)

    # Mime type of the response.
    mimetype = schema.TextLine(required=False)

    related_items = RelationList(required=False)


class TaskResponse(Response):

    implements(ITaskResponse)

    def __init__(self, *args, **kwargs):
        super(TaskResponse, self).__init__(*args, **kwargs)
        self.successor_oguid = ''
        self.rendered_text = ''
        self.transition = ''
        self.mimetype = ''
        self.added_objects = PersistentList()
        self.related_items = PersistentList()

    def add_related_item(self, relation):
        self.related_items.append(relation)
