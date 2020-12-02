from opengever.api.actors import serialize_actor_id_to_json_summary
from opengever.api.add import FolderPost
from opengever.api.response import ResponsePost
from opengever.api.response import SerializeResponseToJson
from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.api.serializer import SerializeSQLModelToJsonBase
from opengever.api.serializer import SerializeSQLModelToJsonSummaryBase
from opengever.base.helpers import display_name
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.globalindex.browser.report import task_type_helper
from opengever.globalindex.model.task import Task
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.models.team import Team
from opengever.task.interfaces import ICommentResponseHandler
from opengever.task.task import ITask
from opengever.task.task_response import ITaskResponse
from opengever.tasktemplates.interfaces import IFromParallelTasktemplate
from opengever.tasktemplates.interfaces import IFromSequentialTasktemplate
from plone.restapi.deserializer import json_body
from plone.restapi.deserializer.dxcontent import DeserializeFromJson
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(ITask, Interface)
class SerializeTaskToJson(GeverSerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeTaskToJson, self).__call__(*args, **kwargs)
        result[u'containing_dossier'] = self._get_containing_dossier_summary()
        result[u'sequence_type'] = self._get_sequence_type()
        return result

    def _get_containing_dossier_summary(self):
        containing_dossier = self.context.get_main_dossier()
        if not containing_dossier:
            return None
        return getMultiAdapter(
            (containing_dossier, self.request), ISerializeToJsonSummary
        )()

    def _get_sequence_type(self):
        if IFromSequentialTasktemplate.providedBy(self.context):
            return {'title': translate(u'label_sequential_process',
                                       domain='opengever.task',
                                       context=self.request),
                    'token': 'sequential'}
        if IFromParallelTasktemplate.providedBy(self.context):
            return {'title': translate(u'label_parallel_process',
                                       domain='opengever.task',
                                       context=self.request),
                    'token': 'parallel'}
        return None


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
        ignored_columns = set(self.IGNORED_COLUMNS)
        return [
            column for column in self.context.__table__.columns
            if column.name not in ignored_columns
        ]

    def add_additional_metadata(self, data):
        data.update({
            '@id': self.context.absolute_url(),
            # XXX deprecated
            'issuer_fullname': display_name(self.context.issuer),
            'issuer_actor': serialize_actor_id_to_json_summary(self.context.issuer),
            'oguid': str(self.context.oguid),
            # XXX deprecated
            'responsible_fullname': display_name(self.context.responsible),
            'responsible_actor': serialize_actor_id_to_json_summary(self.context.responsible),
            'task_type': task_type_helper(self.context.task_type),
        })

    @property
    def content_type(self):
        return self.context.content_type


@implementer(ISerializeToJsonSummary)
@adapter(Task, IOpengeverBaseLayer)
class SerializeTaskModelToJsonSummary(SerializeSQLModelToJsonSummaryBase):

    item_columns = (
        'review_state',
        'task_id',
        'title',
    )

    def add_additional_metadata(self, data):
        data.update({
            'oguid': str(self.context.oguid),
            'task_type': task_type_helper(self.context.task_type),
        })

    @property
    def get_url(self):
        return self.context.absolute_url()

    @property
    def content_type(self):
        return self.context.content_type


class TaskResponsePost(ResponsePost):
    """Add a Response to the current context.
    """

    def create_response(self, text):
        response_handler = ICommentResponseHandler(self.context)
        if not response_handler.is_allowed():
            raise Unauthorized(
                "The current user is not allowed to add comments")

        return response_handler.add_response(text)


@implementer(IExpandableElement)
@adapter(ITask, IOpengeverBaseLayer)
class TaskPredecessor(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            "predecessor": {
                "@id": "{}/@predecessor".format(self.context.absolute_url())
            }
        }
        if not expand:
            return result

        predecessor = self.context.get_sql_object().predecessor
        if predecessor:
            serializer = getMultiAdapter(
                (predecessor, self.request), ISerializeToJsonSummary
            )
            result['predecessor']['item'] = serializer()
        else:
            result['predecessor']['item'] = None

        return result


class TaskPredecessorGet(Service):

    def reply(self):
        predecessor = TaskPredecessor(self.context, self.request)
        return predecessor(expand=True)['predecessor']


@implementer(IExpandableElement)
@adapter(ITask, IOpengeverBaseLayer)
class TaskSuccessors(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
                "successors": {
                    "@id": "{}/@successors".format(self.context.absolute_url())
                }
            }
        if not expand:
            return result

        items = []
        result['successors']['items'] = items
        for successor in self.context.get_sql_object().successors:
            serializer = getMultiAdapter(
                (successor, self.request), ISerializeToJsonSummary
            )
            items.append(serializer())

        return result


class TaskSuccessorsGet(Service):

    def reply(self):
        successors = TaskSuccessors(self.context, self.request)
        return successors(expand=True)['successors']


class TaskPost(FolderPost):
    def add_object_to_context(self):
        super(TaskPost, self).add_object_to_context()

        # Subtasks having a sequential main task requires a special handling for
        # setting the position within the main task.
        if self.context.is_sequential_main_task():
            try:
                position = int(self.request_data.get(
                    'position',
                    len(self.context.get_tasktemplate_order())))
            except (ValueError):
                raise BadRequest("Could not parse `position` attribute")

            self.context.add_task_to_tasktemplate_order(position, self.obj)
