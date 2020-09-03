from opengever.api.response import ResponsePost
from opengever.api.response import SerializeResponseToJson
from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.api.serializer import SerializeSQLModelToJsonBase
from opengever.base.helpers import display_name
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.globalindex.browser.report import task_type_helper
from opengever.globalindex.model.task import Task
from opengever.inbox import FORWARDING_TASK_TYPE_ID
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.models.team import Team
from opengever.task.interfaces import ICommentResponseHandler
from opengever.task.task import ITask
from opengever.task.task_response import ITaskResponse
from plone.restapi.deserializer import json_body
from plone.restapi.deserializer.dxcontent import DeserializeFromJson
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from zExceptions import Unauthorized
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(ITask, Interface)
class SerializeTaskToJson(GeverSerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeTaskToJson, self).__call__(*args, **kwargs)
        result[u'containing_dossier'] = self._get_containing_dossier_summary()
        return result

    def _get_containing_dossier_summary(self):
        containing_dossier = self.context.get_main_dossier()
        if not containing_dossier:
            return None
        return getMultiAdapter(
            (containing_dossier, self.request), ISerializeToJsonSummary
        )()


@implementer(ISerializeToJson)
@adapter(ITaskResponse, Interface)
class SerializeTaskResponseToJson(SerializeResponseToJson):

    model = ITaskResponse


def deserialize_responsible(data):
    """Extract responsible_client when a combined value is used (client,
       responsible separated by a colon).
    """
    if isinstance(data, dict):
        responsible = data['token']
    else:
        responsible = data

    # Skip values without the orgunit prefix
    if not responsible or ':' not in responsible:
        return None

    if ActorLookup(responsible).is_inbox():
        responsible_client = responsible.split(':', 1)[1]

    elif ActorLookup(responsible).is_team():
        team = Team.query.get_by_actor_id(responsible)
        responsible_client = team.org_unit.unit_id

    else:
        responsible_client, responsible = responsible.split(':', 1)

    return {
        'responsible': responsible,
        'responsible_client': responsible_client
    }


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
        responsible = deserialize_responsible(data.get('responsible'))
        if responsible:
            data.update(responsible)


@implementer(ISerializeToJson)
@adapter(Task, IOpengeverBaseLayer)
class SerializeTaskModelToJson(SerializeSQLModelToJsonBase):

    ADDITIONAL_METADATA = {
        '@id': lambda task: task.absolute_url(),
        'issuer_fullname': lambda task: display_name(task.issuer),
        'oguid': lambda task: str(task.oguid),
        'responsible_fullname': lambda task: display_name(task.responsible),
        'task_type': lambda task: task_type_helper(task.task_type),
    }

    # Some columns were ignored in @globalindex from where this serializer
    # has been exctracted. When refactoring, that behavior was preserved, but
    # if we encounter issues with missing data adding all columns should
    # not pose any issues.
    IGNORED_COLUMNS = [
        'admin_unit_id',
        'breadcrumb_title',
        'completed',
        'containing_subdossier',
        'dossier_sequence_number',
        'icon',
        'int_id',
        'physical_path',
        'reference_number',
        'sequence_number',
        'tasktemplate_predecessor_id',
        'text',
    ]

    def get_columns(self):
        ignored_columns = set(
            self.ADDITIONAL_METADATA.keys() + self.IGNORED_COLUMNS
        )
        return [
            column for column in self.context.__table__.columns
            if column.name not in ignored_columns
        ]

    def add_additional_metadata(self, data):
        for key, value in self.ADDITIONAL_METADATA.items():
            data[key] = value(self.context)

    @property
    def content_type(self):
        """Figure out a tasks content type from the task_type column.

        We don't store the content type in globalindex but task_type is
        distinct and we can use it to figure out the content type.
        """
        if self.context.task_type == FORWARDING_TASK_TYPE_ID:
            return 'opengever.inbox.forwarding'
        return 'opengever.task.task'


class TaskResponsePost(ResponsePost):
    """Add a Response to the current context.
    """

    def create_response(self, text):
        response_handler = ICommentResponseHandler(self.context)
        if not response_handler.is_allowed():
            raise Unauthorized(
                "The current user is not allowed to add comments")

        return response_handler.add_response(text)
