from opengever.api.add import get_validation_errors
from opengever.api.task import deserialize_responsible
from opengever.base.source import DossierPathSourceBinder
from opengever.ogds.base.utils import get_current_org_unit
from opengever.task import _ as task_mf
from opengever.task.task import ITask
from opengever.tasktemplates import _ as tasktemplate_mf
from opengever.tasktemplates.content.templatefoldersschema import sequence_type_vocabulary
from opengever.tasktemplates.tasktemplatefolder import ProcessCreator
from opengever.tasktemplates.tasktemplatefolder import ProcessDataPreprocessor
from plone import api
from plone.app.textfield import RichText
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from plone.supermodel import model
from z3c.relationfield.relation import RelationValue
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zExceptions import BadRequest
from zope import schema
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.intid.interfaces import IIntIds


class IProcessSchema(model.Schema):

    start_immediately = schema.Bool(
        required=True,
        default=True
    )

    process = schema.Dict(
        title=u'process',
        key_type=schema.TextLine(),
        required=True)

    related_documents = RelationList(
        required=False,
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            source=DossierPathSourceBinder(
                portal_type=("opengever.document.document", "ftw.mail.mail"),
                navigation_tree_query={
                    'review_state': {'not': 'document-state-shadow'},
                    'object_provides':
                    ['opengever.dossier.behaviors.dossier.IDossierMarker',
                     'opengever.document.document.IDocumentSchema',
                     'opengever.task.task.ITask',
                     'ftw.mail.mail.IMail', ],
                }),
        )
    )


class ITaskContainer(model.Schema):

    items = schema.List(
        title=u'items',
        required=True)

    sequence_type = schema.Choice(
        title=tasktemplate_mf(u'label_sequence_type', default='Type'),
        vocabulary=sequence_type_vocabulary,
        required=True,
    )

    title = schema.TextLine(
        title=task_mf(u"label_title", default=u"Title"),
        description=task_mf('help_title', default=u""),
        required=True,
        max_length=256,
    )

    text = RichText(
        title=task_mf(u"label_text", default=u"Text"),
        description=task_mf(u"help_text", default=u""),

        required=False,
        default_mime_type='text/html',
        output_mime_type='text/x-html-safe')

    deadline = schema.Date(
        title=task_mf(u"label_deadline", default=u"Deadline"),
        description=task_mf(u"help_deadline", default=u""),
        required=False,
    )


class ProcessPost(Service):
    """API Endpoint to create a process.
    """

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)
        data = json_body(self.request)
        # Before deserializing the fields we need to replace the interactive
        # actors, which are not valid as such.
        data_processor = ProcessDataPreprocessor(self.context, data)
        data = data_processor.recursive_replace_interactive_actors()

        # We now need to deserialize the fields
        self.deserialize_data(data)

        # use schema validation for basic fields
        errors = get_validation_errors(self.context, data, IProcessSchema)
        if errors:
            self.raise_bad_request(errors)

        self.validate_tasks(data["process"], errors)

        if errors:
            self.raise_bad_request(errors)

        self.make_related_documents_relation_values(data)
        self.fill_task_container_data(data["process"])

        data = data_processor.recursive_set_deadlines()
        process_creator = ProcessCreator(self.context, data)
        task = process_creator()

        serializer = queryMultiAdapter((task, self.request), ISerializeToJson)
        result = serializer()
        # the folder serializer uses the current url to display the @id. this
        # wont work as we are using the serializer outside a request to the
        # actual item, we are in the @trigger-task-template service. thus we
        # have to make sure to return the correct id.
        result['@id'] = task.absolute_url()
        return result

    def make_related_documents_relation_values(self, data):
        relations = []
        for doc in data.get("related_documents"):
            relations.append(RelationValue(getUtility(IIntIds).getId(doc)))

        data["related_documents"] = relations

    def fill_task_container_data(self, data):
        """The task containers have some automatic values for certain fields,
        as they are simply used to contain a set of parallel or sequential
        subtasks.
        """
        default_data = {
            "issuer": api.user.get_current().getId(),
            "responsible": api.user.get_current().getId(),
            "responsible_client": get_current_org_unit().id(),
            "task_type": "direct-execution"
        }
        self.recursive_fill_task_container_data(data, default_data)

    def recursive_fill_task_container_data(self, data, default_data):
        if self.is_task_container(data):
            data.update(default_data)
            for subtask_data in data.get("items", []):
                self.recursive_fill_task_container_data(subtask_data, default_data)

    @staticmethod
    def is_task_container(data):
        if "items" in data or "sequence_type" in data:
            return True
        return False

    @staticmethod
    def raise_bad_request(errors):
        errors = [{"field": each[0], "error": each[1]} for each in errors]
        raise BadRequest(errors)

    def get_schema(self, data):
        if self.is_task_container(data):
            return ITaskContainer
        return ITask

    def deserialize_data_with_schema(self, data, schema):
        # responsible needs to be treated before any further deserialization as
        # it might need to get split up into responsible_client and responsible.
        responsible = deserialize_responsible(data.get('responsible'))
        if responsible:
            data.update(responsible)

        for name, value in data.items():
            field = schema.get(name)
            if None in (field, value):
                continue

            deserializer = queryMultiAdapter(
                (field, self.context, self.request), IFieldDeserializer)
            data[name] = deserializer(value)

    def deserialize_data(self, data):
        self.deserialize_data_with_schema(data, IProcessSchema)
        self._recursive_deserialization(data.get("process", {}))

    def _recursive_deserialization(self, data):
        self.deserialize_data_with_schema(data, self.get_schema(data))
        for subtask_data in data.get("items", []):
            self._recursive_deserialization(subtask_data)

    def validate_tasks(self, data, errors):
        errors.extend(get_validation_errors(
            self.context, data, self.get_schema(data)))

        for subtask_data in data.get("items", []):
            self.validate_tasks(subtask_data, errors)
