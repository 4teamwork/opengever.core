from Acquisition import aq_inner
from Acquisition import aq_parent
from datetime import date
from datetime import timedelta
from opengever.base.security import elevated_privileges
from opengever.base.utils import get_date_with_delta_excluding_weekends
from opengever.dossier.behaviors.dossier import IDossier
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.base.actor import INTERACTIVE_ACTOR_CURRENT_USER_ID
from opengever.ogds.base.actor import INTERACTIVE_ACTOR_RESPONSIBLE_ID
from opengever.ogds.base.utils import get_current_org_unit
from opengever.task.interfaces import ITaskSettings
from opengever.task.task import ITask
from opengever.tasktemplates import is_tasktemplatefolder_nesting_allowed
from opengever.tasktemplates.content.templatefoldersschema import ITaskTemplateFolderSchema
from opengever.tasktemplates.content.templatefoldersschema import sequence_type_vocabulary
from opengever.tasktemplates.interfaces import IContainParallelProcess
from opengever.tasktemplates.interfaces import IContainSequentialProcess
from opengever.tasktemplates.interfaces import IDuringTaskTemplateFolderTriggering
from opengever.tasktemplates.interfaces import IDuringTaskTemplateFolderWorkflowTransition
from opengever.tasktemplates.interfaces import IPartOfParallelProcess
from opengever.tasktemplates.interfaces import IPartOfSequentialProcess
from plone import api
from plone.dexterity.content import Container
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import createContent
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import noLongerProvides


ACTIVE_STATE = 'tasktemplatefolder-state-activ'
INACTIVE_STATE = 'tasktemplatefolder-state-inactiv'
TRANSITION_ACTIVATE = 'tasktemplatefolder-transition-inactiv-activ'


class TaskTemplateFolder(Container):

    @property
    def sequence_type_label(self):
        return sequence_type_vocabulary.by_value[self.sequence_type].title

    @property
    def is_sequential(self):
        return self.sequence_type == u'sequential'

    def is_subtasktemplatefolder(self):
        parent = aq_parent(aq_inner(self))
        return ITaskTemplateFolderSchema.providedBy(parent)

    def is_workflow_transition_allowed(self):
        if IDuringTaskTemplateFolderWorkflowTransition.providedBy(getRequest()):
            # Transition happens recursively so we need to allow it during
            # transition of the main TaskTemplateFolder.
            return True
        return not self.is_subtasktemplatefolder()

    def contains_subtasktemplatefolders(self):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.unrestrictedSearchResults(
            path='/'.join(self.getPhysicalPath()),
            object_provides=ITaskTemplateFolderSchema.__identifier__)
        return len(brains) > 1

    def trigger(self, dossier, templates, related_documents,
                values, start_immediately, main_task_overrides=None):

        if main_task_overrides is None:
            main_task_overrides = {}

        trigger = TaskTemplateFolderTrigger(
            self, dossier, templates, related_documents,
            main_task_overrides, values, start_immediately)
        return trigger.generate()

    def allowedContentTypes(self, *args, **kwargs):
        types = super(TaskTemplateFolder, self).allowedContentTypes(*args, **kwargs)

        def filter_type(fti):
            if fti.id == "opengever.tasktemplates.tasktemplatefolder":
                return is_tasktemplatefolder_nesting_allowed()
            return True

        return filter(filter_type, types)


class TaskTemplateFolderTrigger(object):

    def __init__(self, context, dossier, templates,
                 related_documents, main_task_overrides, values, start_immediately):
        self.context = context
        self.dossier = dossier
        self.selected_templates = templates
        self.related_documents = related_documents
        self.main_task_overrides = main_task_overrides
        self.values = values
        self.start_immediately = start_immediately
        self.request = getRequest()

    def generate(self):
        process_data = {
            "start_immediately": self.start_immediately,
            "process": self.get_main_task_data(),
            "related_documents": self.related_documents,
        }
        process_data["process"]["items"] = self.get_subtasks_data()
        process_data = ProcessDataPreprocessor(self.dossier, process_data)()
        self.process_creator = ProcessCreator(self.dossier, process_data)
        main_task = self.process_creator()
        return main_task

    def get_main_task_data(self):
        title = self.main_task_overrides.get("title", self.context.title)
        text = self.main_task_overrides.get("text", self.context.text)
        deadline = self.main_task_overrides.get("deadline")
        return dict(
            title=title,
            text=text,
            issuer=api.user.get_current().getId(),
            responsible=api.user.get_current().getId(),
            responsible_client=get_current_org_unit().id(),
            task_type='direct-execution',
            deadline=deadline,
            sequence_type=self.context.sequence_type)

    def get_subtasks_data(self):
        subtasks_data = []
        for i, template in enumerate(self.selected_templates):
            subtasks_data.append(self.get_subtask_data(template, self.values.get(template.id)))
        return subtasks_data

    def get_subtask_data(self, template, values):
        title = values.get("title", template.title)
        text = values.get("text", template.text)
        deadline = values.get("deadline", date.today() + timedelta(template.deadline))
        data = dict(
            title=title,
            issuer=template.issuer,
            responsible=template.responsible,
            responsible_client=template.responsible_client,
            task_type=template.task_type,
            text=text,
            deadline=deadline,
        )

        data.update(values)
        return data


class ProcessDataPreprocessor(object):

    def __init__(self, dossier, process_data):
        self.dossier = dossier
        self.process_data = process_data

    def __call__(self):
        self.recursive_replace_interactive_actors()
        self.recursive_set_deadlines()
        return self.process_data

    def recursive_replace_interactive_actors(self):
        self._recursive_replace_interactive_actors(
            self.process_data.get("process", {}))
        return self.process_data

    def _recursive_replace_interactive_actors(self, data):
        self.replace_interactive_actors(data)
        if self.has_children(data):
            for item in data.get("items", []):
                self._recursive_replace_interactive_actors(item)

    @staticmethod
    def has_children(data):
        return bool(data.get("items"))

    def recursive_set_deadlines(self):
        self._recursive_set_deadlines(self.process_data.get("process", {}))
        return self.process_data

    def _recursive_set_deadlines(self, data):
        if self.has_children(data):
            longest_deadline = date.today()
            for item in data.get("items", []):
                deadline = self._recursive_set_deadlines(item)
                longest_deadline = max(longest_deadline, deadline)

            if data.get("deadline") is None:
                data["deadline"] = get_date_with_delta_excluding_weekends(
                    longest_deadline, self.default_deadline_timedelta)
        return data["deadline"]

    @property
    def default_deadline_timedelta(self):
        return api.portal.get_registry_record(
            'deadline_timedelta', interface=ITaskSettings)

    def replace_interactive_actors(self, data):
        if ActorLookup(data.get('issuer')).is_interactive_actor():
            data['issuer'] = self.get_interactive_representative(data['issuer'])

        if ActorLookup(data.get('responsible')).is_interactive_actor():
            data['responsible_client'] = get_current_org_unit().id()
            data['responsible'] = self.get_interactive_representative(
                data['responsible'])

    def get_interactive_representative(self, principal):
        """The current systems knows two interactive users:

        `responsible`: the reponsible of the main dossier.
        `current_user`: the currently logged in user.
        """
        if principal == INTERACTIVE_ACTOR_RESPONSIBLE_ID:
            return IDossier(self.dossier.get_main_dossier()).responsible

        elif principal == INTERACTIVE_ACTOR_CURRENT_USER_ID:
            return api.user.get_current().getId()

        else:
            return principal


class ProcessCreator(object):

    def __init__(self, dossier, process_data):
        self.dossier = dossier
        self.process_data = process_data
        self.start_immediately = self.process_data.get("start_immediately")
        self.request = getRequest()
        self.related_documents = self.process_data.get("related_documents", [])

    def __call__(self):
        main_task_data = self.process_data["process"]
        main_task = self.create_main_task(main_task_data)
        alsoProvides(self.request, IDuringTaskTemplateFolderTriggering)
        with elevated_privileges():
            self.create_subtasks(main_task, self.process_data["process"], main_task)

        if self.start_immediately or IContainParallelProcess.providedBy(main_task):
            main_task.start_subprocess()

        noLongerProvides(self.request, IDuringTaskTemplateFolderTriggering)
        return main_task

    @staticmethod
    def has_children(data):
        return bool(data.get("items"))

    def create_main_task(self, data):
        main_task = self.add_task(self.dossier, data)

        # set the main_task in to the in progress state
        api.content.transition(obj=main_task,
                               transition='task-transition-open-in-progress')

        return main_task

    def create_subtasks(self, container, data, main_task):
        subtasks = []
        for i, subtask_data in enumerate(data["items"]):
            subtask = self.create_subtask(container, subtask_data, main_task)
            if self.has_children(subtask_data):
                self.create_subtasks(subtask, subtask_data, main_task)
            subtasks.append(subtask)
        container.set_tasktemplate_order(subtasks)

    def create_subtask(self, container, data, main_task):
        task = self.add_task(
            container, data, related_documents=self.related_documents)
        task.set_to_planned_state()
        task.reindexObject()
        task.sync()

        return task

    @staticmethod
    def is_sequential(sequence_type):
        return sequence_type == u'sequential'

    def add_task(self, container, data, related_documents=[]):
        sequence_type = data.get("sequence_type")
        task = createContent('opengever.task.task',
                             relatedItems=related_documents,
                             **data)
        task = addContentToContainer(container, task, checkConstraints=True)

        self.add_marker_interfaces(container, task, sequence_type)
        return task

    def add_marker_interfaces(self, container, task, sequence_type):
        if sequence_type:
            # contains interfaces
            if self.is_sequential(sequence_type):
                alsoProvides(task, IContainSequentialProcess)
            else:
                alsoProvides(task, IContainParallelProcess)

        # part-of interfaces
        if ITask.providedBy(container):
            if IContainSequentialProcess.providedBy(container):
                alsoProvides(task, IPartOfSequentialProcess)
            elif IContainParallelProcess.providedBy(container):
                alsoProvides(task, IPartOfParallelProcess)
