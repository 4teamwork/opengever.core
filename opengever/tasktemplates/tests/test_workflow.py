from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.tasktemplates.interfaces import IContainSequentialProcess
from opengever.testing import IntegrationTestCase
from plone import api
from zope.interface import alsoProvides


class TestWorfklowForTasksFromTemplatefolders(IntegrationTestCase):

    @browsing
    def test_cancel(self, browser):
        self.login(self.regular_user, browser=browser)

        alsoProvides(self.task, IContainSequentialProcess)
        self.set_workflow_state('task-state-in-progress', self.task)
        self.set_workflow_state('task-state-in-progress', self.subtask)

        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('Cancel')
        browser.fill({'Response': u'Projekt wurde gestoppt.'})
        browser.click_on('Save')

        self.assertEquals(
            'task-state-cancelled', api.content.get_state(self.task))
        self.assertEquals(
            'task-state-cancelled', api.content.get_state(self.subtask))

    @browsing
    def test_cancelnested(self, browser):
        self.login(self.regular_user, browser=browser)
        alsoProvides(self.task, IContainSequentialProcess)

        subtask_level3 = create(
            Builder('task')
            .within(self.subtask)
            .titled(u'Subsubtask')
            .having(
                responsible_client='fa',
                responsible=self.dossier_manager.getId(),
                issuer=self.dossier_responsible.getId(),
                task_type='correction'
            )
            .in_state('task-state-in-progress')
        )

        subtask_level4 = create(
            Builder('task')
            .within(subtask_level3)
            .titled(u'Subtask of Subsubtask')
            .having(
                responsible_client='fa',
                responsible=self.dossier_manager.getId(),
                issuer=self.dossier_responsible.getId(),
                task_type='correction'
            )
            .in_state('task-state-in-progress')
        )

        self.set_workflow_state('task-state-in-progress', self.task)
        self.set_workflow_state('task-state-in-progress', self.subtask)
        self.set_workflow_state('task-state-in-progress', subtask_level3)
        self.set_workflow_state('task-state-in-progress', subtask_level4)


        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('Cancel')
        browser.fill({'Response': u'Projekt wurde gestoppt.'})
        browser.click_on('Save')

        self.assertEquals(
            'task-state-cancelled', api.content.get_state(self.task))
        self.assertEquals(
            'task-state-cancelled', api.content.get_state(self.subtask))
        self.assertEquals(
            'task-state-cancelled', api.content.get_state(subtask_level3))
        self.assertEquals(
            'task-state-cancelled', api.content.get_state(subtask_level4))
