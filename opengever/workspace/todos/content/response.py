from datetime import datetime
from opengever.workspace.interfaces import IResponse
from opengever.workspace.interfaces import IResponses
from opengever.workspace.interfaces import IToDo
from Persistence import Persistent
from persistent.list import PersistentList
from plone import api
from plone.restapi.serializer.converters import json_compatible
from zope.annotation import IAnnotations
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implements


class Response(Persistent):
    implements(IResponse)

    def __init__(self, text,
                 created=None,
                 creator=None,
                 modified=None,
                 modifier=None):
        self.text = text
        self.created = created or datetime.now()
        self.creator = creator or api.user.get_current().getId()
        self.modified = modified
        self.modifier = modifier

    def as_dict(self):
        return dict(id=json_compatible(self.id),
                    text=json_compatible(self.text),
                    created=json_compatible(self.created),
                    creator=json_compatible(self.creator),
                    modified=json_compatible(self.modified),
                    modifier=json_compatible(self.modifier))


@adapter(IToDo)
@implementer(IResponses)
class Responses(object):

    responses_key = 'opengever.workspace.todos:responses'
    auto_increment_key = 'opengever.workspace.todos:responses:auto-increment'

    def __init__(self, issue):
        self.annotations = IAnnotations(issue)

    def all(self):
        return tuple(self.annotations.get(self.responses_key, ()))

    def append(self, response):
        if not IResponse.providedBy(response):
            raise ValueError('{!r} is not an IResponse')

        if self.responses_key not in self.annotations:
            self.annotations[self.responses_key] = PersistentList()

        response.id = self.next_id()

        self.annotations[self.responses_key].append(response)
        return response

    def remove(self, response):
        self.annotations.get(self.responses_key, []).remove(response)

    def edit(self, id_, text):
        updated_response = None
        for response in self.all():
            if response.id == id_:
                response.text = text
                response.modifier = api.user.get_current().getId()
                response.modified = datetime.now()
                updated_response = response
                break

        if updated_response is None:
            raise ValueError("Response with id {} not found".format(id_))
        return updated_response

    def next_id(self):
        id_ = self.annotations.get(self.auto_increment_key, 0) + 1
        self.annotations[self.auto_increment_key] = id_
        return id_
