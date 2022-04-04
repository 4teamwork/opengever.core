from Acquisition import aq_inner
from Acquisition import aq_parent
from datetime import date
from datetime import timedelta
from opengever.dossier.behaviors.dossier import IDossier
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.base.actor import INTERACTIVE_ACTOR_CURRENT_USER_ID
from opengever.ogds.base.actor import INTERACTIVE_ACTOR_RESPONSIBLE_ID
from opengever.ogds.base.utils import get_current_org_unit
from opengever.task import TASK_STATE_PLANNED
from opengever.task.activities import TaskAddedActivity
from opengever.task.interfaces import ITaskSettings
from opengever.tasktemplates import is_tasktemplatefolder_nesting_allowed
from opengever.tasktemplates.content.templatefoldersschema import ITaskTemplateFolderSchema
from opengever.tasktemplates.content.templatefoldersschema import sequence_type_vocabulary
from opengever.tasktemplates.interfaces import IDuringTaskTemplateFolderWorkflowTransition
from opengever.tasktemplates.interfaces import IDuringTaskTemplateFolderTriggering
from opengever.tasktemplates.interfaces import IFromParallelTasktemplate
from opengever.tasktemplates.interfaces import IFromSequentialTasktemplate
from plone import api
from plone.dexterity.content import Container
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import createContent
from zope.event import notify
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import noLongerProvides
from zope.lifecycleevent import ObjectCreatedEvent

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
        self.process_creator = ProcessCreator(self.dossier)
        main_task_data = self.get_main_task_data()
        main_task = self.process_creator.create_main_task(main_task_data)
        alsoProvides(self.request, IDuringTaskTemplateFolderTriggering)
        subtasks_data = self.get_subtasks_data()
        self.create_subtasks(main_task, subtasks_data)
        noLongerProvides(self.request, IDuringTaskTemplateFolderTriggering)
        return main_task

    def get_main_task_data(self):
        title = self.main_task_overrides.get("title", self.context.title)
        text = self.main_task_overrides.get("text", self.context.text)
        deadline = self.main_task_overrides.get("deadline", self.get_main_task_deadline())
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

    def create_subtasks(self, main_task, subtasks_data):
        subtasks = []
        for i, data in enumerate(subtasks_data):
            subtask = self.create_subtask(main_task, data, is_first=i == 0)
            subtasks.append(subtask)

        main_task.set_tasktemplate_order(subtasks)

    def set_initial_state(self, task, is_first):
        """Set the initial states to planned for tasks of a sequential
        tasktemplatefolder except for the first if start_immediately is True.
        Tasks of a parallel tasktemplatefolder are skipped.
        """
        if not IFromSequentialTasktemplate.providedBy(task):
            return

        if not self.start_immediately \
           or not is_first:
            task.set_to_planned_state()

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
            relatedItems=self.related_documents,
            deadline=deadline,
        )

        data.update(values)
        self.replace_interactive_actors(data)
        return data

    def create_subtask(self, main_task, data, is_first):
        task = self.process_creator.add_task(
            main_task, data)
        self.set_initial_state(task, is_first)
        task.reindexObject()
        task.get_sql_object().sync_with(task)

        # add activity record for subtask
        if api.content.get_state(task) != TASK_STATE_PLANNED:
            activity = TaskAddedActivity(task, getRequest())
            activity.record()

        return task

    def get_main_task_deadline(self):
        highest_deadline = max(
            [template.deadline for template in self.selected_templates])
        deadline_timedelta = api.portal.get_registry_record(
            'deadline_timedelta', interface=ITaskSettings)
        return date.today() + timedelta(highest_deadline + deadline_timedelta)

    def replace_interactive_actors(self, data):
        data['issuer'] = self.get_interactive_representative(data['issuer'])
        if ActorLookup(data['responsible']).is_interactive_actor():
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

    def set_tasktemplate_predecessor(self, task, predecessor):
        if not self.context.is_sequential:
            return

        if predecessor:
            task.set_tasktemplate_predecessor(predecessor)


class ProcessCreator(object):

    def __init__(self, dossier):
        self.dossier = dossier

    def create_main_task(self, data):
        main_task = self.add_task(self.dossier, data)

        # set the main_task in to the in progress state
        api.content.transition(obj=main_task,
                               transition='task-transition-open-in-progress')

        return main_task

    @staticmethod
    def is_sequential(sequence_type):
        return sequence_type == u'sequential'

    def add_task(self, container, data):
        sequential = False
        if "sequence_type" in data:
            if self.is_sequential(data.pop("sequence_type")):
                sequential = True
        elif IFromSequentialTasktemplate.providedBy(container):
            sequential = True

        task = createContent('opengever.task.task', **data)
        notify(ObjectCreatedEvent(task))
        task = addContentToContainer(container, task, checkConstraints=True)
        self.mark_as_generated_from_tasktemplate(task, sequential)
        return task

    def mark_as_generated_from_tasktemplate(self, task, sequential):
        if sequential:
            alsoProvides(task, IFromSequentialTasktemplate)
        else:
            alsoProvides(task, IFromParallelTasktemplate)
