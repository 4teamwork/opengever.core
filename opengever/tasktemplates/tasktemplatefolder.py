from datetime import date
from datetime import timedelta
from opengever.dossier.behaviors.dossier import IDossier
from opengever.ogds.base.utils import get_current_org_unit
from opengever.task import TASK_STATE_PLANNED
from opengever.task.activities import TaskAddedActivity
from opengever.task.interfaces import ITaskSettings
from opengever.tasktemplates import INTERACTIVE_USERS
from opengever.tasktemplates.content.templatefoldersschema import sequence_type_vocabulary
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


class TaskTemplateFolder(Container):

    @property
    def sequence_type_label(self):
        return sequence_type_vocabulary.by_value[self.sequence_type].title

    @property
    def is_sequential(self):
        return self.sequence_type == u'sequential'

    def trigger(self, dossier, templates, related_documents,
                values, start_immediately):

        trigger = TaskTemplateFolderTrigger(
            self, dossier, templates, related_documents,
            values, start_immediately)
        return trigger.generate()


class TaskTemplateFolderTrigger(object):

    def __init__(self, context, dossier, templates,
                 related_documents, values, start_immediately):
        self.context = context
        self.dossier = dossier
        self.selected_templates = templates
        self.related_documents = related_documents
        self.values = values
        self.start_immediately = start_immediately
        self.request = getRequest()

    def generate(self):
        main_task = self.create_main_task()
        alsoProvides(self.request, IDuringTaskTemplateFolderTriggering)
        self.create_subtasks(main_task)
        noLongerProvides(self.request, IDuringTaskTemplateFolderTriggering)
        return main_task

    def add_task(self, container, data):
        task = createContent('opengever.task.task', **data)
        notify(ObjectCreatedEvent(task))
        task = addContentToContainer(container, task, checkConstraints=True)
        self.mark_as_generated_from_tasktemplate(task)
        return task

    def create_main_task(self):
        data = dict(
            title=self.context.title,
            issuer=api.user.get_current().getId(),
            responsible=api.user.get_current().getId(),
            responsible_client=get_current_org_unit().id(),
            task_type='direct-execution',
            deadline=self.get_main_task_deadline())

        main_task = self.add_task(self.dossier, data)

        # set the main_task in to the in progress state
        api.content.transition(obj=main_task,
                               transition='task-transition-open-in-progress')

        return main_task

    def create_subtasks(self, main_task):
        predecessor = None

        subtasks = []
        for template in self.selected_templates:
            subtask = self.create_subtask(
                main_task, template, self.values.get(template.id))
            subtasks.append(subtask)

        main_task.set_tasktemplate_order(subtasks)

    def set_initial_state(self, task, template):
        """Set the initial states to planned for tasks of a sequential
        tasktemplatefolder except for the first if start_immediately is True.
        Tasks of a parallel tasktemplatefolder are skipped.
        """
        if not self.context.is_sequential:
            return

        if not self.start_immediately \
           or template != self.selected_templates[0]:
            task.set_to_planned_state()

    def create_subtask(self, main_task, template, values):
        data = dict(
            title=template.title,
            issuer=template.issuer,
            responsible=template.responsible,
            responsible_client=template.responsible_client,
            task_type=template.task_type,
            text=template.text,
            relatedItems=self.related_documents,
            deadline=date.today() + timedelta(template.deadline),
        )

        data.update(values)
        self.replace_interactive_actors(data)

        task = self.add_task(main_task, data)
        self.set_initial_state(task, template)
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

    def mark_as_generated_from_tasktemplate(self, task):
        if self.context.is_sequential:
            alsoProvides(task, IFromSequentialTasktemplate)
        else:
            alsoProvides(task, IFromParallelTasktemplate)

    def replace_interactive_actors(self, data):
        data['issuer'] = self.get_interactive_representative(data['issuer'])
        if data['responsible_client'] == INTERACTIVE_USERS:
            data['responsible_client'] = get_current_org_unit().id()
            data['responsible'] = self.get_interactive_representative(
                data['responsible'])

    def get_interactive_representative(self, principal):
        """The current systems knows two interactive users:

        `responsible`: the reponsible of the main dossier.
        `current_user`: the currently logged in user.
        """

        if principal == 'responsible':
            return IDossier(self.dossier.get_main_dossier()).responsible

        elif principal == 'current_user':
            return api.user.get_current().getId()

        else:
            return principal

    def set_tasktemplate_predecessor(self, task, predecessor):
        if not self.context.is_sequential:
            return

        if predecessor:
            task.set_tasktemplate_predecessor(predecessor)
