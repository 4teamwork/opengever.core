from opengever.activity.model.activity import Activity
from opengever.base.oguid import Oguid
from opengever.tasktemplates.interfaces import IFromSequentialTasktemplate
from opengever.testing import IntegrationTestCase
from plone import api
from zope.interface import alsoProvides


class TestSequentialTaskProcess(IntegrationTestCase):

    features = ('activity', )

    def test_starts_next_task_when_task_gets_resolved(self):
        self.login(self.regular_user)

        self.set_workflow_state('task-state-in-progress', self.inactive_task)
        self.set_workflow_state('task-state-planned', self.archive_task)
        alsoProvides(self.inactive_task, IFromSequentialTasktemplate)
        alsoProvides(self.archive_task, IFromSequentialTasktemplate)

        self.archive_task.set_tasktemplate_predecessor(self.inactive_task)
        self.archive_task.get_sql_object().sync_with(self.archive_task)

        api.content.transition(
            obj=self.inactive_task, transition='task-transition-in-progress-resolved')

        self.assertEquals(
            'task-state-resolved', api.content.get_state(self.inactive_task))
        self.assertEquals(
            'task-state-open', api.content.get_state(self.archive_task))

    def test_handles_already_opened_tasks(self):
        self.login(self.regular_user)

        self.set_workflow_state('task-state-in-progress', self.inactive_task)
        self.set_workflow_state('task-state-open', self.archive_task)
        alsoProvides(self.inactive_task, IFromSequentialTasktemplate)
        alsoProvides(self.archive_task, IFromSequentialTasktemplate)

        self.archive_task.set_tasktemplate_predecessor(self.inactive_task)
        self.archive_task.get_sql_object().sync_with(self.archive_task)

        api.content.transition(
            obj=self.inactive_task, transition='task-transition-in-progress-resolved')

        self.assertEquals(
            'task-state-resolved', api.content.get_state(self.inactive_task))
        self.assertEquals(
            'task-state-open', api.content.get_state(self.archive_task))

    def test_record_activity_when_open_next_task(self):
        self.login(self.regular_user)

        # preperation
        self.set_workflow_state('task-state-in-progress', self.inactive_task)
        self.set_workflow_state('task-state-planned', self.archive_task)
        alsoProvides(self.inactive_task, IFromSequentialTasktemplate)
        alsoProvides(self.archive_task, IFromSequentialTasktemplate)
        self.archive_task.set_tasktemplate_predecessor(self.inactive_task)
        self.archive_task.get_sql_object().sync_with(self.archive_task)

        api.content.transition(
            obj=self.inactive_task,
            transition='task-transition-in-progress-resolved')
        self.assertEquals(
            'task-state-resolved', api.content.get_state(self.inactive_task))
        self.assertEquals(
            'task-state-open', api.content.get_state(self.archive_task))

        activity = Activity.query.all()[-1]
        self.assertEquals('task-added', activity.kind)
        self.assertEquals(
            Oguid.for_object(self.archive_task), activity.resource.oguid)
