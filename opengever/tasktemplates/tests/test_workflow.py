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
