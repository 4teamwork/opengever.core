from opengever.workspace.interfaces import IResponses
from opengever.workspace.todos.content.response import Response
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class Get(Service):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(Get, self).__init__(context, request)
        self.params = []
        self.responses = IResponses(self.context).all()

    def publishTraverse(self, request, response_id):
        # Consume any path segments after /@registry as parameters

        if response_id:
            self.params.append(response_id)
        return self

    def responses_as_json_serializable(self):
        return map(lambda response: response.as_dict(), self.responses)

    def reply(self):
        if self.params and len(self.params) > 0:
            for response in self.responses:
                if str(response.id) == self.params[0]:
                    return response.as_dict()
            return None

        else:
            # Return all responses
            return [
                {'@id': '{}/@response'.format(self.context.absolute_url()),
                 'responses': self.responses_as_json_serializable()}
            ]


class Post(Service):
    def reply(self):
        response_data = json_body(self.request)
        added = IResponses(self.context).append(
            Response(text=response_data['text']))

        return added.as_dict()


class Patch(Service):
    def reply(self):
        response_data = json_body(self.request)
        text = response_data['text']
        id_ = int(response_data['id'])

        return IResponses(self.context).edit(id_, text).as_dict()


class Delete(Service):
    def reply(self):
        response_data = json_body(self.request)
        id_ = int(response_data['id'])

        for response in IResponses(self.context).all():
            if response.id == id_:
                IResponses(self.context).remove(response)
                self.request.response.setStatus(204)
                return None

        raise ValueError("Could not remove response with id {}".format(id_))
