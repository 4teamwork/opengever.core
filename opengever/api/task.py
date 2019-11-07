from opengever.api.response import ResponsePost
from opengever.api.response import SerializeResponseToJson
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.models.team import Team
from opengever.task.interfaces import ICommentResponseHandler
from opengever.task.task import ITask
from opengever.task.task_response import ITaskResponse
from plone.restapi.deserializer import json_body
from plone.restapi.deserializer.dxcontent import DeserializeFromJson
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISerializeToJson
from zExceptions import Unauthorized
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(ITaskResponse, Interface)
class SerializeTaskResponseToJson(SerializeResponseToJson):

    model = ITaskResponse


@implementer(IDeserializeFromJson)
@adapter(ITask, Interface)
class TaskDeserializeFromJson(DeserializeFromJson):
    """A task specific deserializer which allows to pass in the
    responsible_client and responsible value in a combined string.
    In the same way as it is exposed by the APIs querysoure endpoint.
    """

    def __call__(self, validate_all=False, data=None, create=False):
        if data is None:
            data = json_body(self.request)

        self.update_reponsible_field_data(data)

        super(TaskDeserializeFromJson, self).__call__(
            validate_all=validate_all, data=data, create=create)

    def update_reponsible_field_data(self, data):
        """Extract responsible_client when a combined value is used (client,
        responsible separated by a colon).
        """

        if not data.get('responsible'):
            return

        if isinstance(data['responsible'], dict):
            responsible = data['responsible']['token']
        else:
            responsible = data['responsible']

        # Skip values without the orgunit prefix
        if ':' not in responsible:
            return

        if ActorLookup(responsible).is_inbox():
            responsible_client = responsible.split(':', 1)[1]

        elif ActorLookup(responsible).is_team():
            team = Team.query.get_by_actor_id(responsible)
            responsible_client = team.org_unit.unit_id

        else:
            responsible_client, responsible = responsible.split(':', 1)

        data['responsible'] = responsible
        data['responsible_client'] = responsible_client


class TaskResponsePost(ResponsePost):
    """Add a Response to the current context.
    """

    def create_response(self, text):
        response_handler = ICommentResponseHandler(self.context)
        if not response_handler.is_allowed():
            raise Unauthorized(
                "The current user is not allowed to add comments")

        return response_handler.add_response(text)
