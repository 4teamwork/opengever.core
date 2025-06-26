from opengever.api import _
from opengever.api.actors import serialize_actor_id_to_json_summary
from opengever.api.add import FolderPost
from opengever.api.deserializer import GeverDeserializeFromJson
from opengever.api.globalindex import translate_review_state
from opengever.api.response import ResponseDelete
from opengever.api.response import ResponsePost
from opengever.api.response import SerializeResponseToJson
from opengever.api.serializer import extend_with_responses
from opengever.api.serializer import GeverSerializeFolderToJson
from opengever.api.serializer import SerializeSQLModelToJsonBase
from opengever.api.serializer import SerializeSQLModelToJsonSummaryBase
from opengever.base.helpers import display_name
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.globalindex.model.task import Task
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.models.team import Team
from opengever.task.helper import task_type_value_helper
from opengever.task.interfaces import ICommentResponseHandler
from opengever.task.task import ITask
from opengever.task.task_response import ITaskResponse
from opengever.task.task_response import TaskResponse
from opengever.task.util import TaskAutoResponseChangesTracker
from opengever.tasktemplates.interfaces import IContainParallelProcess
from opengever.tasktemplates.interfaces import IContainSequentialProcess
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from plone.restapi.services.content.update import ContentPatch
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(ITask, Interface)
class SerializeTaskToJson(GeverSerializeFolderToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeTaskToJson, self).__call__(*args, **kwargs)
        result[u'containing_dossier'] = self._get_containing_dossier_summary()
        result[u'sequence_type'] = self._get_sequence_type()
        result[u'is_completed'] = self.context.is_in_final_state
        result[u'creator'] = serialize_actor_id_to_json_summary(self.context.Creator())
        model = self.context.get_sql_object()
        result[u'is_remote_task'] = model.is_remote_task
        result[u'has_remote_predecessor'] = model.has_remote_predecessor
        result[u'has_sequential_successor'] = model.has_sequential_successor
        result[u'responsible_admin_unit_url'] = model.get_assigned_org_unit().admin_unit.public_url
        result[u'is_current_user_responsible'] = self.context.is_current_user_responsible()
        return result

    def _get_containing_dossier_summary(self):
        containing_dossier = self.context.get_main_dossier()
        if not containing_dossier:
            return None
        return getMultiAdapter(
            (containing_dossier, self.request), ISerializeToJsonSummary
        )()

    def _get_sequence_type(self):
        if IContainSequentialProcess.providedBy(self.context):
            return {'title': translate(u'label_sequential_process',
                                       domain='opengever.task',
                                       context=self.request),
                    'token': 'sequential'}
        if IContainParallelProcess.providedBy(self.context):
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

    elif ActorLookup(responsible).is_interactive_actor():
        responsible_client = None

    else:
        responsible_client, responsible = responsible.split(':', 1)

    return {
        'responsible': responsible,
        'responsible_client': responsible_client
    }


@implementer(IDeserializeFromJson)
@adapter(ITask, Interface)
class TaskDeserializeFromJson(GeverDeserializeFromJson):
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
        'dossier_sequence_number',
        'icon',
        'int_id',
        'physical_path',
        'reference_number',
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
            'is_completed': self.context.is_completed,
            # XXX deprecated
            'issuer_fullname': display_name(self.context.issuer),
            'issuer_actor': serialize_actor_id_to_json_summary(self.context.issuer),
            'oguid': str(self.context.oguid),
            # XXX deprecated
            'responsible_fullname': display_name(self.context.responsible),
            'responsible_actor': serialize_actor_id_to_json_summary(self.context.responsible),
            'review_state_label': translate_review_state(self.context.review_state),
            'task_type': task_type_value_helper(self.context.task_type),
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
            'task_type': task_type_value_helper(self.context.task_type),
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


class TaskResponseDelete(ResponseDelete):
    """Delete a response.
    """

    response_class = TaskResponse


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


class TaskPatch(ContentPatch):
    """Specific Patch service for tasks, to prevent changing the
    is_private field."""

    def reply(self):
        current_is_private_value = self.context.is_private
        current_responsible = self.context.responsible
        current_responsible_client = self.context.responsible_client

        changes_tracker = TaskAutoResponseChangesTracker(self.context, self.request)
        with changes_tracker.track_changes(['text', 'relatedItems']):
            data = super(TaskPatch, self).reply()

        # if representation was requested, then the responses will not be up to
        # date in data as the new response was generated after
        # super(TaskPatch, self).reply() is called
        if self.request.getHeader("Prefer") == "return=representation":
            extend_with_responses(data, self.context, self.request)

        if self.context.is_private != current_is_private_value:
            raise BadRequest("It's not allowed to change the is_private option"
                             " of an existing task.")

        if self.context.responsible != current_responsible or \
           self.context.responsible_client != current_responsible_client:
            raise BadRequest(_(u"change_responsible_not_allowed",
                               default=u"It's not allowed to change responsible here. Use \"Reassign\" instead"))
        return data


class CloseTaskPost(Service):
    """Attempts to close a task.

    Permission checks are intentionally omitted here, as the specific permissions or roles required
    to close the task are not known in advance. If the user lacks the necessary permissions,
    an error will be raised by the transition extender.
    """

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        self.context.close_task()

        self.request.response.setStatus(204)
        return super(CloseTaskPost, self).reply()
